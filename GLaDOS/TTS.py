import subprocess
import whisper
import os
import signal
import requests

AUDIO_FILE = "input.wav"
MIC_DEVICE = "default"
SAMPLE_RATE = "16000"
LANGUAGE = "pt"
MODEL_SIZE = "base"

OLLAMA_URL = "http://192.168.1.150:11434/api/generate"
LLAMA_MODEL = "llama3.2:1b"


def record_audio():
    print("Ouvindo... (ENTER para parar)")
    process = subprocess.Popen([
        "arecord",
        "-D", MIC_DEVICE,
        "-f", "S16_LE",
        "-r", SAMPLE_RATE,
        "-c", "1",
        AUDIO_FILE
    ])
    input()
    process.send_signal(signal.SIGINT)
    process.wait()


def transcribe():
    print("Transcrevendo...")
    result = whisper_model.transcribe(
        AUDIO_FILE,
        language=LANGUAGE,
        fp16=False
    )
    text = result["text"].strip()
    print(f"Você disse: {text}")
    return text

def ask_llama(prompt):
    print("Pensando...")
    payload = {
        "model": LLAMA_MODEL,
        "prompt": (
            "You will receive a question in Brazilian Portuguese. "
            "Understand it, but answer ONLY in English. "
            "Answer in one short paragraph, maximum 20 characters, "
            "no lists, direct text.\n\n"
            f"Question: {prompt}"
        ),
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["response"]

def speak(text):
    print("Falando...")
    subprocess.Popen(
        f'curl -L --retry 30 --get --fail '
        f'--data-urlencode "text={text}" '
        f'"https://glados.c-net.org/generate" | aplay',
        shell=True
    )

# ================== MAIN ==================

print("Carregando modelo Whisper...\n")
whisper_model = whisper.load_model(MODEL_SIZE)
print("Whisper carregado!\n")

try:
    while True:
        input("Aperte ENTER para começar a gravar...\n")
        record_audio()

        user_text = transcribe()
        if not user_text:
            continue

        response = ask_llama(user_text)
        print(f"\nResposta:\n{response}\n")

        speak(response)

except KeyboardInterrupt:
    print("\nSaindo...")
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
