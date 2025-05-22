#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import random
from datetime import datetime

# Cores ANSI
green = "\033[1;32m"
red = "\033[1;31m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
cyan = "\033[1;36m"
purple = "\033[1;35m"
gray = "\033[1;30m"
reset = "\033[0m"

# Banner com cor azul
banner = f"""{cyan}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣄⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⣡⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠙⣦⡙⢦⡀⠀⠀⠀⠀⠀⠀⡀⣄⡀⠀⡴⠸⣄⠀⣠⠎⢦⠀⢀⣠⢀⠀⠀⠀⠀⠀⠀⢀⡴⢋⣴⠏⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠀⠘⢯⣦⣉⡳⠦⣄⡾⠶⠄⠛⢄⠉⣙⠁⣆⣌⠶⢃⣰⠈⢛⠉⠠⠚⠢⠶⠿⣠⠤⠞⣋⢴⡿⠋⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⢠⠀⠈⢻⡻⣽⣶⣦⣄⠠⣄⠕⣤⣢⣞⣷⡜⣿⣶⣿⢧⣾⣷⣗⣤⠪⢀⠄⣠⣴⣶⣟⣟⡟⠁⠀⢠⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⡸⡂⠀⠀⠓⠘⢦⠀⠁⠁⠘⣦⢪⢿⣿⣿⠻⣿⣿⣿⠟⣿⣿⣿⡵⣴⠃⠘⠉⠐⡵⠋⠞⠀⠀⢀⢇⣻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⣧⡀⠀⠀⠀⠄⠘⣧⠀⠀⠀⠸⣿⣿⣿⣿⣇⠘⣿⠃⣸⣿⣿⣿⣿⠇⠀⠀⠀⣼⠃⠀⠀⠀⠀⠘⢼⡸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⢿⡳⠀⠀⠀⠀⠀⠘⣧⡘⣦⣷⣻⢿⡿⣿⣿⣧⠀⣰⣿⣿⢿⡿⣿⣼⣴⣇⣼⠃⠀⠀⠀⠀⢀⠞⣿⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⢸⡀⡈⢷⠄⠀⠀⠄⣲⣶⣾⡿⠿⢝⠿⢷⡕⠸⡿⣿⢷⣿⣯⡏⢪⡾⠫⣻⠿⢿⣷⣶⣖⠢⠀⠀⠀⡾⢃⠀⡇⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢯⡛⠁⠘⠀⠀⠀⠀⡴⣖⣚⣿⣧⣄⠠⡀⠀⠹⣆⢳⠉⠀⠉⡞⣠⠏⠀⢀⠄⣠⣼⣿⣓⣒⠦⠀⠀⠀⠀⠂⡈⠛⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⢋⣤⣤⡖⠋⠁⠀⣠⣴⣟⢿⡿⣿⣿⣽⣦⣄⠈⠎⠣⠀⠘⠱⠁⢠⣴⣯⣿⣿⢿⡿⣿⣦⣄⠀⠈⠛⣶⣦⣄⡘⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢟⡖⢀⣤⡤⠔⠂⠠⠼⢿⡡⠌⠁⠈⡀⠻⣝⣿⣿⣆⡆⠀⠀⠀⢠⣴⣿⣿⢿⠟⢁⠁⠈⠀⢉⡿⠷⠄⠐⠢⠤⣤⡀⢲⡛⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠐⡻⠉⠀⠀⠀⠀⣀⡬⠀⠀⡤⡀⠻⣦⡀⠙⣿⡿⠇⠀⠀⠀⠸⢿⣿⠃⢁⣴⡟⢀⣤⠀⠀⢥⣄⠀⠀⠀⠀⠉⢝⠂⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢇⣼⣧⢾⣽⡂⢠⣾⠿⢿⣿⣧⣝⣿⣦⣄⠀⠀⠀⠀⠠⣴⣀⣦⡤⠀⠀⠀⠀⣀⣴⣟⣫⣴⣿⣿⠿⣷⣄⢀⢮⡷⢮⣧⡘⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡚⠉⠐⣩⡯⠖⢀⣤⢆⡀⠀⠉⠛⢻⡭⠀⠀⠲⢮⣽⣦⠸⣿⠏⣴⣏⡽⠖⠀⠀⢹⡟⠛⠋⠀⠀⡰⣤⡄⠰⢽⣍⠂⠉⢛⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⣠⠀⢚⡭⠂⠀⢉⣾⡿⠉⠀⠀⠀⢠⡶⢿⣷⣿⣦⠸⠿⠳⠉⠞⠿⠏⣴⣿⣾⡿⢶⣄⠀⠀⠀⠨⢿⣷⡍⠀⠐⢮⡓⠄⣄⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡏⡴⢋⣔⠄⠀⠀⡟⠀⡴⣾⠀⠀⡏⠀⢰⣿⢿⡇⠐⠊⠻⣿⠟⠉⠂⢹⣿⣿⡞⠀⠸⡄⠀⢳⢦⠀⢻⠀⠀⠠⡢⡙⢦⣹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠟⡀⢸⣿⠊⠀⠀⠃⠀⠁⡏⡆⠀⠀⠐⢌⠻⣟⣧⡀⠀⠀⠀⠀⠀⢀⣼⣳⡟⡡⠂⠀⠀⢰⢿⠈⠂⠈⠀⠀⠑⣽⡇⢀⠻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢸⡧⠀⠀⡀⠀⠀⠀⠁⢟⣆⠀⠀⠠⡓⢽⡿⡗⠆⠀⠀⠀⠠⢾⢟⡿⢊⠅⠀⢠⣸⡻⠈⠀⠀⠀⢀⠀⠀⢾⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠈⣠⡎⣾⠄⠰⡁⠄⠀⠀⠈⢻⡀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡀⠀⢀⡾⠁⠀⠀⠀⣀⠆⠀⣳⢰⣄⠁⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣰⠋⣧⠟⢀⢀⣿⡔⢰⠇⠀⠀⠁⠀⠀⣿⠀⡇⢰⢠⠀⡆⡆⢸⠀⣷⠁⠀⠈⠀⠀⠐⡆⢢⣻⡀⡀⠻⣸⠙⣆⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠇⠀⠸⡄⡾⣆⠻⡇⠘⠀⢀⠀⠀⠀⢀⠹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠏⠀⠀⠀⠀⡀⠀⠃⢸⠟⣰⣿⢀⠏⠀⠸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠁⣿⠀⣴⠀⢸⢺⠀⠀⠀⠘⠀⢸⠀⠀⠀⠀⠀⠀⠀⡇⠀⡇⠀⠀⠀⢳⡄⠀⣶⠀⢹⠈⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡜⠹⠳⣌⣿⡄⠀⠀⢇⠀⢻⢠⠀⠀⠀⠀⠀⡄⡯⠀⢰⠀⠀⢠⣿⢡⠞⠏⢧⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠈⠫⢳⣔⢠⠀⠀⡌⠈⠋⠃⠂⠘⠉⠁⢁⠀⠀⡄⣤⡞⠝⠁⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢶⡆⣦⠈⠓⠒⠒⠒⠒⠒⠚⠁⣰⢠⣵⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠘⢧⡈⢾⣴⣾⣦⠶⢃⡼⠃⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡈⠛⢃⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

                ⣰⣦⡀⠀⠀⠀⠀⠀⠀⠀⢠⡄⠀⠀⡰⣶⣲⣤⠀⠀⢰⡶⠀⣠⣴⣶⣶⣴⣒
                ⢻⣿⡇⠀⠀⣤⣷⠀⠀⠀⣼⡇⠀⡟⡟⠉⠉⢻⣆⠀⢸⡇⠀⣿⣿⡇⠀⠀⠀
                ⢨⣿⣇⠀⠀⢻⣿⠀⠀⢀⣿⠁⢸⡯⠀⠀⠀⢸⣿⠀⣺⡇⠀⠸⣿⣿⡿⠿⠛
                ⠀⢿⣿⡀⢀⣾⢿⣦⠀⣼⡇⠀⠸⡇⠀⠀⠀⣸⡿⠀⣺⠅⠀⠀⣿⡇⠀⠀⠀
                ⠀⠈⣿⣇⣾⠇⠈⣿⣿⡟⠀⠀⠀⠯⢶⣶⠾⠟⠁⠀⢿⣦⡶⠄⢹⠇⠀⠀⠀ 𓃦ᨒꨄ︎ 🐾
                ⠀⠀⠘⢿⠏⠀⠀⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


        ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░  ░▒▓█▓▒░
{reset}
"""

def progress_bar_wolf(task, cmd, color):
    width = 30
    spin_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spin_idx = 0
    progress = 0

    print(f"{color}{task}...{reset} ", end='', flush=True)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while proc.poll() is None:
        progress = min(progress + random.randint(1, 3), 100)
        filled = int(width * progress / 100)
        empty = width - filled
        # Aqui, adicione o código de cor verde na barra preenchida:
        bar_filled = f"{green}{'█' * filled}{reset}"
        bar_empty = '-' * empty
        spinner = spin_chars[spin_idx]
        print(f"\r{color}{task}...{reset} {spinner} [{bar_filled}{bar_empty}] {progress}%", end='', flush=True)
        spin_idx = (spin_idx + 1) % len(spin_chars)
        time.sleep(0.1)
    proc.wait()
    print(f"\r{color}{task}...{reset} ✔ [{green}{'█'*width}{reset}] 100% {green}[Success]{reset}")
    return proc.returncode


def check_internet():
    print(f"{yellow}🕒 {datetime.now().strftime('%H:%M')}{reset}")
    print(f"{yellow}Verificando conexão com a internet...{reset}")
    result = subprocess.run("ping -c 1 google.com", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        print(f"{red}✖ Sem conexão! Conecte-se à internet.{reset}")
        sys.exit(1)
    print(f"{green}✔ Conexão OK{reset}\n")

def setup_storage():
    print(f"\n{blue}🔧 Configurando permissão de armazenamento...{reset}")
    result = subprocess.run("termux-setup-storage", shell=True)
    if result.returncode == 0:
        print(f"{green}✔ Armazenamento configurado{reset}")
    else:
        print(f"{yellow}⚠ Configure manualmente com: termux-setup-storage{reset}")

def main():
    os.system('clear')
    print(banner)
    print(f"{yellow}📦 Iniciando instalação das dependências do Wolf no Termux...{reset}")

    check_internet()

    progress_bar_wolf("Atualizando pacotes", "pkg update -y && pkg upgrade -y", blue)
    progress_bar_wolf("Instalando Python", "pkg install python -y", cyan)
    progress_bar_wolf("Instalando FFmpeg", "pkg install ffmpeg -y", purple)
    progress_bar_wolf("Instalando wget, git e aria2", "pkg install wget git aria2 -y", blue)
    progress_bar_wolf("Instalando yt-dlp (pip)", "pip install --upgrade yt-dlp", cyan)
    progress_bar_wolf("Instalando requests (pip)", "pip install --upgrade requests", purple)

    setup_storage()

    print(f"\n{green}🎉 Todas as dependências foram instaladas com sucesso!{reset}")
    print(f"{yellow}🐺 Execute: python3 wolf-9.0.py{reset}")
    print(f"{gray}🕒 Tempo total: {yellow}{int(time.time() - start_time)} segundos{reset}")

if __name__ == "__main__":
    start_time = time.time()
    main()
