<div align="center">

# 🤖 RobotEye

**Rosto robótico em tela cheia com olhos animados, reconhecimento de voz e respostas faladas por IA local.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2E7D32?style=for-the-badge&logo=python&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)

</div>

---

## Sobre

O **RobotEye** transforma qualquer tela (de um monitor a um display ligado num Raspberry Pi) no
rosto de um robô. É uma adaptação para Python da biblioteca
[FluxGarage RoboEyes](https://github.com/FluxGarage/RoboEyes), que originalmente desenha olhos
animados em telas OLED pequenas, com melhorias próprias: escala para qualquer resolução,
novas expressões e integração com voz.

## Visão Geral

O projeto permite:

- desenhar olhos animados em tela cheia, adaptados a qualquer resolução (base 2560×1440)
- piscar, olhar em volta e dormir sozinho
- mostrar expressões: feliz, risada, bravo e tonto
- ouvir o que você fala (microfone + **Whisper**, em português)
- responder com um modelo de linguagem local via **Ollama** (`llama3.2:1b`)
- falar a resposta em voz alta com um serviço de texto para fala

## Estrutura

```text
.
|-- Tests/
|   `-- robo_olhos.py     olhos com animações automáticas (feliz, risada, bravo, tonto, sono)
|-- GLaDOS/
|   |-- glados.py         rosto com fala espontânea e ciclo de sono
|   `-- TTS.py            ouvir (arecord + Whisper) → pensar (Ollama) → falar
|-- initScript.sh         setup automático para Raspberry Pi / Debian
`-- requirements.txt
```

## Como Funciona

```text
🎤 microfone ─► arecord ─► Whisper (fala → texto) ─► Ollama / Llama 3.2 ─► texto → voz ─► 🔊
                                                                         └─► olhos animados (Pygame)
```

## Rodando

### Só os olhos

```bash
pip install -r requirements.txt
python3 Tests/robo_olhos.py
```

Abre em tela cheia. Feche com `ESC`.

### Raspberry Pi (setup automático)

```bash
curl -O https://raw.githubusercontent.com/kerlonr/RobotEye/main/initScript.sh
bash initScript.sh
```

O script atualiza o sistema, instala Pygame e dependências, clona o repositório e habilita o
Bluetooth (para usar uma caixa de som sem fio no futuro).

### Conversa por voz

Requer o `openai-whisper` instalado e um servidor **Ollama** acessível na rede.
Ajuste `OLLAMA_URL` e `LLAMA_MODEL` no topo de `GLaDOS/TTS.py` e rode:

```bash
pip install openai-whisper requests
python3 GLaDOS/TTS.py
```

Fale, aperte `ENTER` para parar de gravar e aguarde a resposta.

## Próximos Passos

- juntar olhos e conversa por voz num único programa
- sincronizar as expressões com o que o robô está falando
- som por caixa Bluetooth
