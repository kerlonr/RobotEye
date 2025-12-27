#!/bin/bash

set -e

echo "======================================"
echo "        ROBOT EYE - SETUP"
echo "======================================"


# Atualização básica do sistema
echo "[1/4] Atualizando sistema..."
sudo apt update
sudo apt upgrade -y


# Dependências do sistema
echo "[2/4] Instalando dependências do sistema..."
sudo apt install -y \
    python3-pygame \
    git \
    xserver-xorg \

# Clone do repositório
echo "[3/4] Clonando repositório RobotEye..."

cd ~
if [ -d "RobotEye" ]; then
    echo "Repositório já existe. Atualizando..."
    cd RobotEye
    git pull
else
    git clone https://github.com/kerlonr/RobotEye.git
    cd RobotEye
fi

# Bluetooth
echo "[4/4] Habilitando Bluetooth... (Futuro)"
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Finalização
echo "======================================"
echo "    Setup concluído com sucesso!"
echo "    Para rodar:"
echo "      python3 robo_olhos.py"
echo "    Reboot recomendado!"
echo "======================================"
