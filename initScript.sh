#!/bin/bash

set -e

echo "======================================"
echo "        ROBOT EYE - SETUP"
echo "======================================"


# Atualização básica do sistema
echo "[1/6] Atualizando sistema..."
sudo apt update
sudo apt upgrade -y


# Dependências do sistema
echo "[2/6] Instalando dependências do sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    xserver-xorg \

# Clone do repositório
echo "[3/6] Clonando repositório RobotEye..."

cd ~
if [ -d "RobotEye" ]; then
    echo "Repositório já existe. Atualizando..."
    cd RobotEye
    git pull
else
    git clone https://github.com/kerlonr/RobotEye.git
    cd RobotEye
fi

# Dependências Python
echo "[4/5] Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Bluetooth
echo "[5/5] Habilitando Bluetooth... (Futuro)"
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Finalização
echo "======================================"
echo "    Setup concluído com sucesso!"
echo "    Para rodar:"
echo "      python3 robo_olhos.py"
echo "    Reboot recomendado!"
echo "======================================"
