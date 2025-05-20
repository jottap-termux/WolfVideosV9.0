#!/bin/bash

# Limpa a tela
clear

# Banner estiloso com cores
echo -e "\033[1;36m"
echo "  ____    __    ____  _______  __        ______   ______   .___  ___.  _______"
echo "  \   \  /  \  /   / |   ____||  |      /      | /  __  \  |   \/   | |   ____|"
echo "   \   \/    \/   /  |  |__   |  |     |  ,----'|  |  |  | |  \  /  | |  |__"  
echo "    \            /   |   __|  |  |     |  |     |  |  |  | |  |\/|  | |   __|" 
echo "     \    /\    /    |  |____ |  `----.|  `----.|  `--'  | |  |  |  | |  |____"
echo "      \__/  \__/     |_______||_______| \______| \______/  |__|  |__| |_______|"
echo -e "\033[1;31m"
echo "  __      __   ______   __    __   ______   __  __   ______   ______"
echo " |  |    |  | /  __  \ |  |  |  | |   ___| |  |/  | |   ___| |   ___|"
echo " |  |    |  | |  |  | | |  |__|  | |  |___  |     | |  |___  |  |___" 
echo " |  |    |  | |  |  | | |   __   | |   ___| |  |\  | |   ___| |   ___|"
echo " |  `----|  | |  `--' | |  |  |  | |  |___  |  | \  | |  |___ |  |___"
echo "  \______/__/  \______/ |__|  |__| |______| |__|  \__| |______| |______|"
echo -e "\033[1;33m"
echo "  _______   ______   .______       _______  __   __       _______."
echo " /  _____| /  __  \  |   _  \     |   ____||  | |  |     /       |"
echo "|  |  __  |  |  |  | |  |_)  |    |  |__   |  | |  |    |   (----\`"
echo "|  | |_ | |  |  |  | |      /     |   __|  |  | |  |     \   \\"
echo "|  |__| | |  \`--'  | |  |\  \----.|  |____ |  | |  | .----)   |"
echo " \______|  \______/  | _| \`._____||_______||__| |__| |_______/"

echo -e "\033[0m"
echo
echo -e "\033[1;36mIniciando instalação das dependências...\033[0m"
sleep 2

# Função de barra de progresso animada
progress_bar() {
    local i=0
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while [ $i -le 100 ]; do
        local idx=$((i % 10))
        printf "\r\033[1;32m[%s] Instalando... %3d%%\033[0m" "${spin:$idx:1}" "$i"
        sleep 0.03
        i=$((i+2))
    done
    printf "\r\033[1;32m[✓] Instalação concluída!        \033[0m\n"
}

# Função para instalar dependências
install_dependencies() {
    # Atualizar repositórios
    echo -e "\033[1;34m[•] Atualizando repositórios...\033[0m"
    if command -v apt &> /dev/null; then
        sudo apt update -y > /dev/null 2>&1
    elif command -v pkg &> /dev/null; then
        pkg update -y > /dev/null 2>&1
    fi
    progress_bar

    # Instalar Python e pip
    echo -e "\033[1;34m[•] Instalando Python e pip...\033[0m"
    if command -v apt &> /dev/null; then
        sudo apt install -y python3 python3-pip > /dev/null 2>&1
    elif command -v pkg &> /dev/null; then
        pkg install -y python > /dev/null 2>&1
    fi
    progress_bar

    # Atualizar pip
    echo -e "\033[1;34m[•] Atualizando pip...\033[0m"
    python3 -m pip install --upgrade pip > /dev/null 2>&1 || python -m pip install --upgrade pip > /dev/null 2>&1
    progress_bar

    # Instalar bibliotecas Python necessárias
    echo -e "\033[1;34m[•] Instalando bibliotecas Python...\033[0m"
    pip install requests yt-dlp spotdl > /dev/null 2>&1
    progress_bar

    # Instalar aria2
    echo -e "\033[1;34m[•] Instalando aria2...\033[0m"
    if command -v apt &> /dev/null; then
        sudo apt install -y aria2 > /dev/null 2>&1
    elif command -v pkg &> /dev/null; then
        pkg install -y aria2 > /dev/null 2>&1
    fi
    progress_bar
}

# Executar instalação
install_dependencies

# Mostrar monitor de processos
echo -e "\n\033[1;35mAbrindo monitor de processos (top)...\033[0m"
sleep 1
top -b -n 1 | head -n 12

echo -e "\n\033[1;32mTodas as dependências foram instaladas com sucesso!\033[0m"
echo -e "\033[1;33mExecute o script principal com: python3 wolf-9.0.py\033[0m"
