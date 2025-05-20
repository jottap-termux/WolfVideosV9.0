#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import requests
import shutil
import time
import re
import urllib.parse
import signal
import webbrowser
from threading import Thread
from queue import Queue, Empty
from datetime import datetime

# Configurações
HOME = os.path.expanduser("~")
PASTA_DOWNLOADS = "/sdcard/WolfVideos"
ARQUIVO_DOWNLOAD_ARCHIVE = os.path.join(PASTA_DOWNLOADS, "baixados.txt")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
ARQUIVO_COOKIES = "/sdcard/cookies.txt"
URL_ATUALIZACAO_COOKIES = "https://jottap-termux.github.io/cookies.txt"
ATUALIZAR_COOKIES_AUTO = True
TERMUX_PATH = "/data/data/com.termux/files/home/.local/bin"
ARQUIVO_DOWNLOADS_PARCIAL = os.path.join(PASTA_DOWNLOADS, ".downloads_parciais.txt")
ARQUIVO_LOG = os.path.join(PASTA_DOWNLOADS, "historico_downloads.log")
SCRIPT_URL = "https://raw.githubusercontent.com/jottap-termux/wolf/main/wolfv8.5.py"

FORMATOS_VIDEO = {
    '1': {'desc': '🎯 Best quality (4K if available)', 'code': 'best'},
    '2': {'desc': '🖥 1080p HD', 'code': '137+140'},
    '3': {'desc': '💻 720p HD', 'code': '22'},
    '4': {'desc': '📱 480p', 'code': '135+140'},
    '5': {'desc': '📼 360p', 'code': '18'}
}
FORMATOS_AUDIO = {
    '1': {'desc': '🎧 MP3 (High quality 320kbps)', 'code': 'mp3', 'params': '-x --audio-format mp3 --audio-quality 0'},
    '2': {'desc': '🎵 AAC (High quality)', 'code': 'aac', 'params': '-x --audio-format aac'},
    '3': {'desc': '🎼 FLAC (Lossless)', 'code': 'flac', 'params': '-x --audio-format flac'},
    '4': {'desc': '🎤 M4A (YouTube default)', 'code': 'm4a', 'params': '-x --audio-format m4a'},
    '5': {'desc': '🎶 OPUS (Efficient)', 'code': 'opus', 'params': '-x --audio-format opus'},
    '6': {'desc': '💿 MP3 with cover art', 'code': 'mp3', 'params': '-x --audio-format mp3 --audio-quality 0 --embed-thumbnail --add-metadata'}
}

download_interrompido = False

class ProgressoItem:
    """Armazena os dados de progresso de cada item da playlist"""
    def __init__(self, index, total, titulo):
        self.index = index      # Número do item (ex: 3/25)
        self.total = total      # Total de itens na playlist
        self.titulo = titulo    # Título do vídeo/música
        self.progresso = 0      # Porcentagem (0-100)
        self.completo = False   # Se o download foi finalizado

ARQUIVO_PASTAS_WOLF = os.path.join(HOME, ".pastas_wolf.txt")

def registrar_pasta_downloads(pasta):
    """Registra a pasta de downloads no histórico se ainda não estiver lá"""
    try:
        if not os.path.exists(ARQUIVO_PASTAS_WOLF):
            with open(ARQUIVO_PASTAS_WOLF, "w") as f:
                f.write(f"{pasta}\n")
        else:
            with open(ARQUIVO_PASTAS_WOLF, "r+") as f:
                pastas = [linha.strip() for linha in f.readlines()]
                if pasta not in pastas:
                    f.write(f"{pasta}\n")
    except Exception as e:
        print(f"[!] Erro ao registrar pasta: {e}")

def atualizar_cookies():
    try:
        print("\033[1;34m[•] Atualizando cookies...\033[0m")
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(URL_ATUALIZACAO_COOKIES, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(ARQUIVO_COOKIES, 'w') as f:
                f.write(response.text)
            print("\033[1;32m[✓] Cookies atualizados!\033[0m")
        else:
            print("\033[1;31m[!] Não foi possível atualizar os cookies\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Erro ao atualizar cookies: {e}\033[0m")

def encontrar_arquivo_estado():
    """Procura o arquivo .downloads_parciais.txt em todas as pastas do histórico"""
    if not os.path.exists(ARQUIVO_PASTAS_WOLF):
        return None, None
    with open(ARQUIVO_PASTAS_WOLF) as f:
        pastas = [linha.strip() for linha in f.readlines()]
    for pasta in pastas:
        arquivo_parcial = os.path.join(pasta, ".downloads_parciais.txt")
        if os.path.exists(arquivo_parcial):
            return pasta, arquivo_parcial
    return None, None

# ... agora as outras funções, como baixar_playlist, etc ...

# Registra a pasta padrão ao iniciar o script
registrar_pasta_downloads(PASTA_DOWNLOADS)

def limpar_tela():
    os.system('clear' if os.name == 'posix' else 'cls')

download_interrompido = False  # variável global para controle

# === HISTÓRICO DE PASTAS DE DOWNLOADS ===

def executar_comando_silencioso(comando):
    """
    Executa um comando no shell de forma silenciosa.
    Retorna True se o comando teve sucesso, False caso contrário.
    """
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return resultado.returncode == 0
    except Exception:
        return False

def criar_cookies():
    cookies_padrao = """# Netscape HTTP Cookie File
.xvideos.com    TRUE    /       FALSE   1735689600      ts      1
.xvideos.com    TRUE    /       FALSE   1735689600      platform      pc
.xvideos.com    TRUE    /       FALSE   1735689600      hash    5a8d9f8e7c6b5a4d3e2f1
"""
    try:
        if not os.path.exists(ARQUIVO_COOKIES):
            with open(ARQUIVO_COOKIES, 'w', encoding='utf-8') as f:
                f.write(cookies_padrao)
    except PermissionError:
        alt_cookies = os.path.join(HOME, ".cookies.txt")
        with open(alt_cookies, 'w', encoding='utf-8') as f:
            f.write(cookies_padrao)
        return alt_cookies
    return ARQUIVO_COOKIES


def baixar_video_com_progresso(url):
    cmd = f'yt-dlp --newline "{url}"'
    processo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    try:
        while True:
            linha = processo.stdout.readline()
            if not linha:
                break
            linha = linha.decode('utf-8', errors='ignore') if isinstance(linha, bytes) else linha
            match = re.search(r'(\d+(?:\.\d+)?)%', linha)
            if match:
                progresso = float(match.group(1))
                barra_len = 30
                blocos = int(progresso / 100 * barra_len)
                barra = '█' * blocos + '-' * (barra_len - blocos)
                sys.stdout.write(f"\r\033[36mBaixando {spinner[i % len(spinner)]}\033[0m [{barra}] {progresso:.1f}% ")
                sys.stdout.flush()
                i += 1
        processo.wait()
        if processo.returncode == 0:
            print("\nDownload concluído!")
        else:
            print("\nErro no download.")
    except KeyboardInterrupt:
        processo.terminate()
        print("\nDownload interrompido pelo usuário.")

def mostrar_barra_progresso(mensagem="Processando"):
    global download_interrompido
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    total = 50
    for i in range(total + 1):
        if download_interrompido:
            break
        progresso = int((i / total) * 100)
        barra = '█' * i + '-' * (total - i)
        frame = spinner[i % len(spinner)]
        sys.stdout.write(f"\r\033[36m{mensagem} {frame}\033[0m [{barra}] {progresso}% ")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()


class ProgressoItem:
    """Armazena os dados de progresso de cada item da playlist"""
    def __init__(self, index, total, titulo):
        self.index = index      # Número do item (ex: 3/25)
        self.total = total      # Total de itens na playlist
        self.titulo = titulo    # Título do vídeo/música
        self.progresso = 0      # Porcentagem (0-100)
        self.completo = False   # Se o download foi finalizado

def mostrar_spinner():
    """Retorna um caractere do spinner animado para usar nas barras"""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    return spinner[int(time.time() * 10) % len(spinner)]

def mostrar_progresso_musica(num_seq, total_seq, titulo, progresso, spinner_char):
    titulo_curto = (titulo[:25] + '...') if len(titulo) > 28 else titulo
    barra_len = 20
    blocos_cheios = int(progresso * barra_len / 100)
    preenchimento = ['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    if progresso < 100:
        idx_extra = int((progresso % 5) * (len(preenchimento)-1) / 5)
        idx_extra = min(idx_extra, len(preenchimento)-1)
        char_extra = preenchimento[idx_extra]
    else:
        char_extra = ''
    barra = '█' * blocos_cheios + char_extra
    barra = barra.ljust(barra_len, ' ')
    sys.stdout.write("\r\033[K")
    if progresso >= 100:
        print(f"\033[1;32m[✓] {num_seq}/{total_seq} {titulo_curto.ljust(30)}\033[0m")
    else:
        sys.stdout.write(
            f"\033[1;36m{spinner_char} [{num_seq:03d}/{total_seq:03d}] {titulo_curto.ljust(25)} "
            f"[{barra}] {progresso:5.1f}%\033[0m"
        )
        sys.stdout.flush()

def log_download(link, status):
    try:
        with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {status} - {link}\n")
    except Exception as e:
        print(f"[!] Falha ao registrar download: {e}")


def obter_titulo_video(url):
    try:
        comando = f'yt-dlp --get-title --no-warnings "{url}"'
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            return resultado.stdout.strip()
        return None
    except Exception:
        return None


def limpar_arquivos_temporarios():
    if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        print("\033[1;32m[✓] Arquivos temporários limpos!\033[0m")
        time.sleep(1)

def baixar_playlist(link, tipo='video'):
    """
    Baixa uma playlist inteira (áudio ou vídeo) com suporte a retomada usando --download-archive.
    """
    global download_interrompido

    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    ARQUIVO_DOWNLOAD_ARCHIVE = os.path.join(PASTA_DOWNLOADS, "baixados.txt")

    print("\033[1;34m[•] Obtendo informações da playlist...\033[0m")
    mostrar_barra_progresso("Analisando")

    try:
        cmd_info = f'yt-dlp --playlist-items 1-500 --flat-playlist --print "%(playlist_index)s %(title)s" "{link}"'
        resultado = subprocess.run(cmd_info, shell=True, capture_output=True, text=True)
        itens = [linha.split(' ', 1) for linha in resultado.stdout.strip().split('\n') if linha]
        total_itens = len(itens)
        titulos = {int(idx): titulo.strip() for idx, titulo in itens}
    except Exception as e:
        print(f"\033[1;31m[!] Erro: {str(e)}\033[0m")
        return False

    if total_itens == 0:
        print("\033[1;31m[!] Playlist vazia ou não encontrada\033[0m")
        return False

    print(f"\033[1;32m[✓] Encontradas {total_itens} músicas/vídeos\033[0m")

    base_cmd = f'yt-dlp --newline --user-agent "{USER_AGENT}" --cookies "{ARQUIVO_COOKIES}" --download-archive "{ARQUIVO_DOWNLOAD_ARCHIVE}"'

    if shutil.which("aria2c"):
        base_cmd += " --downloader aria2c --external-downloader-args '-x 16 -k 1M'"
        print("\033[1;33m[⚡] Usando aria2c para download acelerado\033[0m")

    if tipo == 'video':
        mostrar_menu_video_qualidade()
        opcao = input("\n\033[1;36m🎬 Qualidade (1-5): \033[0m").strip()
        qualidade = FORMATOS_VIDEO.get(opcao, {}).get('code', 'best')
        cmd = (
            f'{base_cmd} -f "{qualidade}+bestaudio" --merge-output-format mp4 '
            f'-o "{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s" '
            f'"{link}"'
        )
    else:
        mostrar_menu_audio_formatos()
        opcao = input("\n\033[1;36m🎵 Formato (1-6): \033[0m").strip()
        formato = FORMATOS_AUDIO.get(opcao, FORMATOS_AUDIO['1'])
        cmd = (
            f'{base_cmd} {formato["params"]} '
            f'-o "{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s" '
            f'"{link}"'
        )

    print("\033[1;34m[•] Iniciando download da playlist...\033[0m")
    processo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    try:
        while True:
            if download_interrompido:
                processo.terminate()
                break
            line = processo.stdout.readline()
            if not line:
                break
            sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        processo.terminate()
        download_interrompido = True
        print("\n\033[1;31m[!] Download interrompido\033[0m")
        return False

    processo.wait()
    if processo.returncode == 0:
        print("\033[1;32m[✓] Download completo!\033[0m")
        return True
    else:
        print("\033[1;31m[!] Ocorreu um erro durante o download.\033[0m")
        return False

def salvar_progresso_playlist(url, tipo, escolha, baixados):
    """
    Salva o progresso do download da playlist no arquivo .downloads_parciais.txt
    """
    try:
        with open(ARQUIVO_DOWNLOADS_PARCIAL, 'w', encoding='utf-8') as f:
            f.write(f"{url}\n{tipo}\n{escolha}\n")
            for idx in sorted(baixados):
                f.write(f"{idx}\n")
    except Exception as e:
        print(f"[!] Erro ao salvar progresso: {e}")

def finalizar_download_playlist():
    """
    Remove o arquivo de progresso se o download foi concluído com sucesso.
    """
    if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        os.remove(ARQUIVO_DOWNLOADS_PARCIAL)

def baixar_spotify_deezer():
    print("\033[1;36m[•] Baixar de Spotify ou Deezer\033[0m")
    link = input("\n\033[1;36m🔗 Digite a URL da música/playlist: \033[0m").strip()
    if not link.startswith(("http://", "https://")):
        print("\033[1;31m[!] URL inválida\033[0m")
        return

    print("\033[1;33m[•] Iniciando download com spotDL...\033[0m")
    comando = f"spotdl download \"{link}\" --output \"{PASTA_DOWNLOADS}/wolf-spotfy-premium\""
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"\033[1;32m[✓] Download concluído! Arquivos em: {PASTA_DOWNLOADS}\033[0m")
    except subprocess.CalledProcessError:
        print("\033[1;31m[!] Falha ao baixar com spotDL\033[0m")

def baixar_playlist_com_progresso(url, tipo='audio'):
    """
    Baixa uma playlist com barra de progresso, salva o progresso assim que começa cada item,
    e exibe o status [✓] 1/14 Nome... corretamente, inclusive em retomadas.
    """
    global download_interrompido

    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

    print("\033[1;34m[•] Obtendo informações da playlist...\033[0m")
    mostrar_barra_progresso("Analisando")

    cmd_info = f'yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "{url}"'
    resultado = subprocess.run(cmd_info, shell=True, capture_output=True, text=True)
    itens = [linha.split(' ', 1) for linha in resultado.stdout.strip().split('\n') if linha]
    total_itens = len(itens)
    titulos = {int(idx): titulo.strip() for idx, titulo in itens if idx.isdigit()}
    todos_indices = [int(idx) for idx, _ in itens if idx.isdigit()]

    print(f"\033[1;32m[✓] Encontradas {total_itens} músicas/vídeos\033[0m")

    if tipo == 'video':
        mostrar_menu_video_qualidade()
        escolha = input("\n\033[1;36m🎬 Qualidade (1-5): \033[0m").strip()
        formato = FORMATOS_VIDEO.get(escolha, FORMATOS_VIDEO['1'])
        params = f'-f "{formato["code"]}+bestaudio" --merge-output-format mp4'
    else:
        mostrar_menu_audio_formatos()
        escolha = input("\n\033[1;36m🎵 Formato (1-6): \033[0m").strip()
        formato = FORMATOS_AUDIO.get(escolha, FORMATOS_AUDIO['1'])
        params = formato['params']

    base_cmd = f'yt-dlp --newline --user-agent "{USER_AGENT}" --cookies "{ARQUIVO_COOKIES}"'
    output_tpl = f'"{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s"'
    cmd = f'{base_cmd} {params} -o {output_tpl} "{url}"'

    # --- CORREÇÃO: Carrega ordem_baixados de arquivo, se existir ---
    ordem_baixados = []
    if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        try:
            with open(ARQUIVO_DOWNLOADS_PARCIAL, 'r', encoding='utf-8') as f:
                linhas = f.read().splitlines()
                # linhas[0]=url, [1]=tipo, [2]=escolha, [3:]=índices baixados
                for idx in linhas[3:]:
                    if idx.isdigit():
                        ordem_baixados.append(int(idx))
        except Exception as e:
            print(f"[!] Erro ao ler progresso anterior: {e}")

    baixados = set(ordem_baixados)
    item_atual = None
    progresso = 0

    try:
        processo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        while True:
            line = processo.stdout.readline()
            if not line:
                break

            if "[download] Downloading item" in line:
                parts = line.split()
                if len(parts) >= 4 and parts[3].isdigit():
                    idx = int(parts[3])
                    item_atual = idx
                    progresso = 0
                    if idx not in ordem_baixados:
                        ordem_baixados.append(idx)
                    baixados.add(idx)
                    # Salva o progresso assim que começa o item
                    with open(ARQUIVO_DOWNLOADS_PARCIAL, 'w', encoding='utf-8') as f:
                        f.write(f"{url}\n{tipo}\n{escolha}\n")
                        for idx2 in ordem_baixados:
                            f.write(f"{idx2}\n")

            elif "[download]" in line and "%" in line and item_atual:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    progresso = float(match.group(1))
                    # Posição sequencial do item atual
                    if item_atual in ordem_baixados:
                        num_seq = ordem_baixados.index(item_atual) + 1
                    else:
                        num_seq = len(ordem_baixados) + 1
                    mostrar_progresso_musica(
                        num_seq,
                        total_itens,
                        titulos.get(item_atual, f"Item {item_atual}"),
                        progresso,
                        mostrar_spinner()
                    )

            elif "[download] 100%" in line and item_atual:
                progresso = 100
                if item_atual in ordem_baixados:
                    num_seq = ordem_baixados.index(item_atual) + 1
                else:
                    num_seq = len(ordem_baixados) + 1
                    ordem_baixados.append(item_atual)
                mostrar_progresso_musica(
                    num_seq,
                    total_itens,
                    titulos.get(item_atual, f"Item {item_atual}"),
                    progresso,
                    mostrar_spinner()
                )
                baixados.add(item_atual)
                with open(ARQUIVO_DOWNLOADS_PARCIAL, 'w', encoding='utf-8') as f:
                    f.write(f"{url}\n{tipo}\n{escolha}\n")
                    for idx2 in ordem_baixados:
                        f.write(f"{idx2}\n")
                item_atual = None

    except KeyboardInterrupt:
        processo.terminate()
        print("\n\033[1;31m[!] Download interrompido pelo usuário.\033[0m")
        return False

    processo.wait()

    if processo.returncode == 0:
        print("\n\033[1;32m[✓] Download completo!\033[0m")
        if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
            os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        return True
    else:
        print("\n\033[1;31m[!] Ocorreu um erro durante o download.\033[0m")
        return False

# Supondo que FORMATOS_AUDIO já esteja definido
def escolher_formato_audio():
    print("""
╔════════════════════════════════════════╗
║        🎵 AUDIO FORMAT OPTIONS         ║
╠════════════════════════════════════════╣
║ 1. 🎧 MP3 (High quality 320kbps)       ║
║ 2. 🎵 AAC (High quality)               ║
║ 3. 🎼 FLAC (Lossless)                  ║
║ 4. 🎤 M4A (YouTube default)            ║
║ 5. 🎶 OPUS (Efficient)                 ║
║ 6. 💿 MP3 with cover art               ║
║ 0. 🚪 Voltar                           ║
╚════════════════════════════════════════╝
""")
    while True:
        escolha = input("🎵 Formato (0-6): ").strip()
        if escolha == '0':
            return None
        if escolha in FORMATOS_AUDIO:
            return FORMATOS_AUDIO[escolha]
        print("Opção inválida, tente novamente.")

def menu_playlist():
    url = input("🔗 Digite a URL da playlist: ").strip()
    formato = escolher_formato_audio()
    if not formato:
        print("Operação cancelada.")
        return
    params_extra = formato.get('params', '')
    baixar_playlist_com_progresso(url, formato_audio=formato['code'], params_extra=params_extra)


def baixar_playlist_com_formato():
    url = input("🔗 Digite a URL da playlist: ").strip()
    print("[•] Obtendo informações da playlist...")
    formato = escolher_formato_audio()
    if not formato:
        print("Operação cancelada pelo usuário.")
        return
    params_extra = formato.get('params', '')
    sucesso = baixar_playlist_com_progresso(url, formato_audio=formato['code'], params_extra=params_extra)
    if sucesso:
        print("Download da playlist concluído com sucesso!")
    else:
        print("Falha no download da playlist.")


def atualizar_script():
    print("\033[1;34m[•] Atualizando script...\033[0m")
    try:
        response = requests.get(SCRIPT_URL, timeout=10)
        if response.status_code == 200:
            with open(sys.argv[0], "w") as f:
                f.write(response.text)
            print("\033[1;32m[✓] Script atualizado! Reinicie o programa.\033[0m")
            sys.exit(0)
        else:
            print("\033[1;31m[!] Não foi possível baixar a nova versão\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Erro ao atualizar: {e}\033[0m")
        time.sleep(2)

def editar_cookies():
    print(f"\033[1;36m[•] Editando cookies: {ARQUIVO_COOKIES}\033[0m")
    editor = os.environ.get("EDITOR", "nano" if shutil.which("nano") else "notepad" if os.name == "nt" else "vi")
    os.system(f'{editor} "{ARQUIVO_COOKIES}"')

def player_integrado():
    """Player completo com tratamento de erros avançado"""
    import os
    import subprocess
    import time
    from threading import Thread
    import urllib.parse
    
    # Configurações
    PASTA_DOWNLOADS = "/sdcard/WolfVideos"
    PLAYER_TERMUX = "termux-media-player"  # Player nativo do Termux
    TIMEOUT_REPRODUCAO = 15  # segundos

    # --- Funções auxiliares ---
    def limpar_tela():
        os.system('clear' if os.name == 'posix' else 'cls')

    def verificar_arquivo(caminho):
        """Verifica se o arquivo é válido para reprodução"""
        try:
            if not os.path.exists(caminho):
                return False, "Arquivo não encontrado"
            
            if not os.access(caminho, os.R_OK):
                return False, "Sem permissão de leitura"
            
            tamanho = os.path.getsize(caminho)
            if tamanho < 1024:
                return False, "Arquivo muito pequeno (corrompido?)"
            
            return True, "OK"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def reproduzir_com_fallback(caminho):
        """Tenta vários métodos de reprodução com fallback"""
        caminho_seguro = urllib.parse.quote(caminho)
        metodos = []
        
        # Prioridade de métodos de reprodução
        if 'com.termux' in os.environ.get('HOME', ''):
            metodos = [
                ["termux-media-player", "play", caminho_seguro],
                ["termux-open", caminho_seguro],
                ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW",
                 "-d", f"file://{caminho_seguro}", "--grant-read-uri-permission"]
            ]
        else:
            metodos = [
                ['xdg-open', caminho_seguro] if sys.platform == 'linux' else ['open', caminho_seguro]
            ]

        for metodo in metodos:
            try:
                resultado = subprocess.run(
                    metodo,
                    timeout=TIMEOUT_REPRODUCAO,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                if resultado.returncode == 0:
                    return True
            except Exception:
                continue
        
        return False

    def exibir_controles_basicos():
        print("""
\033[1;36mControles Básicos:
[P] Pausar/Continuar
[→] Avançar 10 segundos
[←] Retroceder 10 segundos
[Q] Sair do player
\033[0m""")

    # --- Interface principal ---
    while True:
        limpar_tela()
        print("""\033[1;36m
╔════════════════════════════════════════╗
║         🎵 PLAYER DE MÍDIA            ║
╠════════════════════════════════════════╣
\033[0m""")

        # Verificar se a pasta existe
        if not os.path.exists(PASTA_DOWNLOADS):
            print("║ \033[1;31mPasta de downloads não encontrada!\033[0m")
            print("╚════════════════════════════════════════╝")
            input("\nPressione Enter para voltar...")
            return

        # Listar arquivos de mídia
        try:
            arquivos = []
            for f in os.listdir(PASTA_DOWNLOADS):
                if f.lower().endswith(('.mp3', '.mp4', '.m4a', '.webm', '.wav')):
                    caminho = os.path.join(PASTA_DOWNLOADS, f)
                    if os.path.isfile(caminho):
                        arquivos.append((f, caminho))

            if not arquivos:
                print("║ Nenhum arquivo de mídia encontrado")
                print("╚════════════════════════════════════════╝")
                input("\nPressione Enter para voltar...")
                return

            # Exibir lista
            for idx, (nome, _) in enumerate(arquivos, 1):
                print(f"║ {idx:2d}. {nome[:55]}")

            print("╚════════════════════════════════════════╝")

            # Seleção do usuário
            escolha = input("\nEscolha o arquivo (0=Voltar): ").strip()
            if escolha == '0':
                return

            if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(arquivos):
                print("\033[1;31mSeleção inválida!\033[0m")
                time.sleep(1)
                continue

            nome_arquivo, caminho_arquivo = arquivos[int(escolha)-1]

            # Verificar arquivo
            valido, mensagem = verificar_arquivo(caminho_arquivo)
            if not valido:
                print(f"\n\033[1;31mErro: {mensagem}\033[0m")
                input("\nPressione Enter para continuar...")
                continue

            # Tentar reproduzir
            print(f"\n\033[1;33mPreparando: {nome_arquivo}\033[0m")
            exibir_controles_basicos()

            if reproduzir_com_fallback(caminho_arquivo):
                print("\033[1;32mReprodução iniciada (use os controles do player)\033[0m")
            else:
                print("\033[1;31mFalha ao reproduzir - Nenhum método funcionou\033[0m")
                print("\033[1;33mDica: Instale VLC ou outro player compatível\033[0m")

            input("\nPressione Enter para voltar...")

        except Exception as e:
            print(f"\n\033[1;31mErro crítico: {str(e)}\033[0m")
            input("\nPressione Enter para continuar...")

def baixar_conteudo(link, formato='mp4', qualidade=None, params_extra=None):
    global download_interrompido, PASTA_DOWNLOADS

    # 1. Configuração inicial
    ytdlp_path = None
    possible_paths = [
        shutil.which("yt-dlp"),
        os.path.join(HOME, ".local/bin/yt-dlp"),
        "/data/data/com.termux/files/usr/bin/yt-dlp"
    ]

    # 2. Localizar yt-dlp
    for path in possible_paths:
        if path and os.path.exists(path):
            ytdlp_path = path
            break

    if not ytdlp_path:
        print("\033[1;31m[!] yt-dlp não encontrado. Use a opção 9 para instalar.\033[0m")
        return False

    # 3. Obter título do vídeo
    titulo = obter_titulo_video(link)
    if titulo:
        print(f"\n\033[1;34m[•] Baixando: {titulo}\033[0m")

    # 4. Montar comando base
    base_cmd = f'{ytdlp_path} --newline --user-agent "{USER_AGENT}" --cookies "{ARQUIVO_COOKIES}"'
    output_template = f'"{PASTA_DOWNLOADS}/%(title)s.%(ext)s"'

    # 5. Verificar e configurar aria2c
    aria2_path = shutil.which("aria2c")
    usando_aria2c = False
    if aria2_path:
        base_cmd += " --downloader aria2c --external-downloader-args '-x 16 -k 1M'"
        usando_aria2c = True
        print("\033[1;33m[⚡] Usando aria2c para download acelerado\033[0m")

    # 6. Montar comando final
    if params_extra:
        comando = f'{base_cmd} {params_extra} -o {output_template} "{link}"'
    elif formato == 'mp3':
        comando = f'{base_cmd} -x --audio-format mp3 --audio-quality 0 -o {output_template} "{link}"'
    elif qualidade:
        comando = f'{base_cmd} -f "{qualidade}+bestaudio" --merge-output-format {formato} -o {output_template} "{link}"'
    else:
        comando = f'{base_cmd} -f best -o {output_template} "{link}"'

    # 7. Função de execução com tratamento de erros
    def executar_download(cmd):
        nonlocal usando_aria2c
        processo = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )

        queue = Queue()

        def enqueue_output(out, queue):
            for line in iter(out.readline, ''):
                queue.put(line)
            out.close()

        Thread(target=enqueue_output, args=(processo.stdout, queue), daemon=True).start()

        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        progresso = 0
        i = 0
        ultimo_progresso = 0

        try:
            while True:
                if download_interrompido:
                    processo.terminate()
                    break

                try:
                    line = queue.get_nowait()
                    match = (re.search(r'(\d+\.\d+)%', line) or
                             re.search(r'(\d+)%', line) or
                             re.search(r'\[download\]\s+(\d+\.?\d*)%', line))
                    if match:
                        progresso = float(match.group(1))
                        ultimo_progresso = progresso
                except Empty:
                    progresso = ultimo_progresso

                # Atualizar barra de progresso
                barra_completa = 50
                barra_preenchida = int(progresso * barra_completa / 100)
                barra = '█' * barra_preenchida + '-' * (barra_completa - barra_preenchida)
                sys.stdout.write(f"\r\033[36mBaixando {spinner[i % len(spinner)]} [{barra}] {progresso:.1f}%\033[0m")
                sys.stdout.flush()
                i += 1

                if processo.poll() is not None:
                    break
                time.sleep(0.1)

        except KeyboardInterrupt:
            processo.terminate()
            sys.stdout.write("\n\033[1;31m[!] Download cancelado\033[0m\n")
            return False

        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        return processo.returncode == 0

    # 8. Executar e tratar fallback
    try:
        resultado = executar_download(comando)

        # Tentar fallback sem aria2c se necessário
        if not resultado and usando_aria2c:
            print("\n\033[1;33m[!] Fallback: Tentando sem aria2c...\033[0m")
            base_cmd_sem_aria2c = base_cmd.replace("--downloader aria2c --external-downloader-args '-x 16 -k 1M'", "")
            comando_sem_aria2c = comando.replace(base_cmd, base_cmd_sem_aria2c)
            resultado = executar_download(comando_sem_aria2c)

        status = "SUCESSO" if resultado else "ERRO"

    except Exception as e:
        print(f"\n\033[1;31m[!] Erro crítico: {str(e)}\033[0m")
        status = "ERRO"

    finally:
        log_download(link, status)

    return resultado

def baixar_multiplas_urls(tipo='video'):
    """Baixa múltiplas URLs de uma vez"""
    print("\033[1;36m[•] Modo múltiplas URLs (CTRL+D para finalizar)\033[0m")
    print("\033[1;33m[•] Cole as URLs uma por linha:\033[0m")

    urls = []
    try:
        while True:
            url = input().strip()
            if url.startswith(('http://', 'https://')):
                urls.append(url)
            elif url:
                print("\033[1;31m[!] URL inválida\033[0m")
    except EOFError:
        pass

    if not urls:
        print("\033[1;31m[!] Nenhuma URL fornecida\033[0m")
        return

    if tipo == 'video':
        mostrar_menu_video_qualidade()
        opcao = input("\n\033[1;36m🎬 Escolha a qualidade [1-5]: \033[0m").strip()
        qualidade = FORMATOS_VIDEO[opcao]['code'] if opcao in FORMATOS_VIDEO else 'best'
    else:
        mostrar_menu_audio_formatos()
        opcao = input("\n\033[1;36m🎵 Escolha o formato [1-6]: \033[0m").strip()
        formato = FORMATOS_AUDIO[opcao] if opcao in FORMATOS_AUDIO else FORMATOS_AUDIO['1']

    for i, url in enumerate(urls, 1):
        print(f"\n\033[1;35m[•] Baixando URL {i}/{len(urls)}\033[0m")
        mostrar_barra_progresso("Processando")

        if tipo == 'video':
            baixar_conteudo(url, 'mp4', qualidade)
        else:
            baixar_conteudo(url, formato['code'], None, formato['params'])

def mostrar_progresso_playlist(item, total, titulo, progresso, spinner_idx):
    barra_len = 20
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    max_titulo_len = 25
    ellipsis = '...'
    if len(titulo) > max_titulo_len:
        titulo_curto = titulo[:max_titulo_len - len(ellipsis)] + ellipsis
    else:
        titulo_curto = titulo
    progresso_clamped = min(100.0, max(0.0, float(progresso)))
    progresso_frac = progresso_clamped / 100.0
    blocos_cheios = int(progresso_frac * barra_len)
    barra = '█' * blocos_cheios + '-' * (barra_len - blocos_cheios)
    if progresso_clamped >= 100.0:
        sys.stdout.write(f"\r\033[1;32m[✓] [{item:02d}/{total:02d}] {titulo_curto.ljust(max_titulo_len)} [{barra}] 100%\033[0m\n")
    else:
        sys.stdout.write(f"\r\033[1;36m{spinner[spinner_idx % len(spinner)]} [{item:02d}/{total:02d}] {titulo_curto.ljust(max_titulo_len)} [{barra}] {progresso_clamped:5.1f}%\033[0m")
        sys.stdout.flush()


def verificar_e_configurar_ambiente():
    global PASTA_DOWNLOADS
    print("\033[1;34m[•] Configurando ambiente...\033[0m")
    is_termux = 'com.termux' in HOME
    if is_termux:
        storage_paths = [
            '/storage/emulated/0/WolfVideos',
            '/sdcard/WolfVideos',
            os.path.join(HOME, 'storage/shared/WolfVideos')
        ]
        for path in storage_paths:
            try:
                os.makedirs(path, exist_ok=True)
                if os.access(path, os.W_OK):
                    PASTA_DOWNLOADS = path
                    break
            except (PermissionError, OSError):
                continue
        # Se não conseguiu usar nenhuma pasta externa, usa interna
        if not os.access(PASTA_DOWNLOADS, os.W_OK):
            PASTA_DOWNLOADS = os.path.join(HOME, "WolfVideos")
            os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
            print("\033[1;33m[!] Usando pasta interna por falta de permissões\033[0m")
        # Garante que o PATH do Termux está correto
        termux_paths = [
            "/data/data/com.termux/files/usr/bin",
            "/data/data/com.termux/files/home/.local/bin"
        ]
        for path in termux_paths:
            if path not in os.environ["PATH"] and os.path.exists(path):
                os.environ["PATH"] += f":{path}"
    print(f"\033[1;32m[✓] Pasta de downloads: {PASTA_DOWNLOADS}\033[0m")
    if not instalar_dependencias_auto():
        print("\033[1;31m[!] Falha na instalação das dependências\033[0m")
        sys.exit(1)
    criar_cookies()
    if ATUALIZAR_COOKIES_AUTO:
        atualizar_cookies()
    try:
        test_file = os.path.join(PASTA_DOWNLOADS, ".test_permission")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        print(f"\033[1;31m[!] Erro de permissão na pasta: {e}\033[0m")
        print("\033[1;33m[!] Execute no Termux: termux-setup-storage\033[0m")
        sys.exit(1)


def instalar_dependencias_auto():
    print("\033[1;34m[•] Verificando dependências...\033[0m")
    mostrar_barra_progresso("Verificando")
    try:
        is_termux = 'com.termux' in HOME
        basic_packages = ["python", "ffmpeg", "libxml2", "libxslt", "binutils", "wget", "git", "aria2"]
        if is_termux:
            executar_comando_silencioso("rm -f /data/data/com.termux/files/usr/var/lib/apt/lists/lock")
            executar_comando_silencioso("rm -f /data/data/com.termux/files/usr/var/cache/apt/archives/lock")
            if not executar_comando_silencioso("pkg update -y"):
                executar_comando_silencioso("apt update -y")
            for pkg in basic_packages:
                if not shutil.which(pkg.split()[0]):
                    executar_comando_silencioso(f"pkg install -y {pkg}")
            if not shutil.which("pip"):
                executar_comando_silencioso("pkg install -y python-pip")
        else:
            executar_comando_silencioso("sudo apt update -y")
            executar_comando_silencioso("sudo apt install -y python3 python3-pip ffmpeg wget aria2")
        pip_packages = ["yt-dlp", "requests"]
        for pkg in pip_packages:
            executar_comando_silencioso(f"{sys.executable} -m pip install --user --upgrade {pkg}")
        if not shutil.which("yt-dlp"):
            ytdlp_path = os.path.join(TERMUX_PATH, "yt-dlp")
            if not os.path.exists(TERMUX_PATH):
                os.makedirs(TERMUX_PATH, exist_ok=True)
            executar_comando_silencioso(f"ln -s {HOME}/.local/bin/yt-dlp {ytdlp_path}")
        print("\033[1;32m[✓] Dependências instaladas/atualizadas!\033[0m")
        return True
    except Exception as e:
        print(f"\033[1;31m[!] Erro durante instalação: {e}\033[0m")
        return False

def mostrar_banner():
    print("""\033[1;36m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
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
               \033[1;32m
                ⣰⣦⡀⠀⠀⠀⠀⠀⠀⠀⢠⡄⠀⠀⡰⣶⣲⣤⠀⠀⢰⡶⠀⣠⣴⣶⣶⣴⣒
                ⢻⣿⡇⠀⠀⣤⣷⠀⠀⠀⣼⡇⠀⡟⡟⠉⠉⢻⣆⠀⢸⡇⠀⣿⣿⡇⠀⠀⠀
                ⢨⣿⣇⠀⠀⢻⣿⠀⠀⢀⣿⠁⢸⡯⠀⠀⠀⢸⣿⠀⣺⡇⠀⠸⣿⣿⡿⠿⠛
                ⠀⢿⣿⡀⢀⣾⢿⣦⠀⣼⡇⠀⠸⡇⠀⠀⠀⣸⡿⠀⣺⠅⠀⠀⣿⡇⠀⠀⠀
                ⠀⠈⣿⣇⣾⠇⠈⣿⣿⡟⠀⠀⠀⠯⢶⣶⠾⠟⠁⠀⢿⣦⡶⠄⢹⠇⠀⠀⠀ 𓃦ᨒꨄ︎ 🐾
                ⠀⠀⠘⢿⠏⠀⠀⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

\033[1;31m
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓██████▓▒░ ░▒▓███████▓▒░
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
   ░▒▓██▓▒░  ░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓██████▓▒░░▒▓███████▓▒░




 \033[1;32m_______________________________________________
 | insta:jottap_62 • by jottap_62 • v9.0 • Wolf |
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
\033[1;33m• Recursos Premium:
  ✔ Download de vídeos 4K/1080p
  ✔ Conversão para MP3 com qualidade de estúdio
  ✔ Download de multi plataformas 
  ✔ Bypass de paywalls e restrições
  ✔ Sistema de cookies automático
  ✔ Criador por Wolf Edit e Jottp_62
  ✔ Player integrado com pré-visualização
  ✔ Suporte a múltiplas plataformas\033[0m""")

def mostrar_menu_principal():
    print("""\033[1;36m
╔════════════════════════════════════════╗
║    🎬 WOLF VIDEO DOWNLOADER PREMIUM    ║
╠════════════════════════════════════════╣
║ 1. 🎥 Baixar vídeo (melhor qualidade)  ║
║ 2. 📊 Escolher qualidade específica    ║
║ 3. 🎧 Converter para áudio             ║
║ 4. 📋 Listar formatos disponíveis      ║
║ 5. 📺 Baixar playlist de vídeos        ║
║ 6. 🎵 Baixar playlist de áudios        ║
║ 7. 📂 Baixar múltiplos vídeos          ║
║ 8. 🎶 Baixar múltiplos áudios          ║
║ 9. 🔄 Atualizar ferramentas            ║
║10. 🍪 Atualizar cookies manualmente    ║
║11. ⚙️ Configurações                     ║
║12. ⏯️ Continuar download de playlist    ║
║13. 🟢 Player integrado                 ║
║14. 🧹 Limpar arquivos temporários      ║
║15. 📝 Editar cookies manualmente       ║
║16. ⬆️ Atualizar script                  ║
║17. 🟢 Baixar de Spotify/Deezer         ║
║ 0. 🚪 Sair                             ║
╚════════════════════════════════════════╝
\033[0m""")

def mostrar_menu_video_qualidade():
    print("""\033[1;36m
╔════════════════════════════════════════╗
║        📽  VIDEO QUALITY OPTIONS        ║
╠════════════════════════════════════════╣
║ 1. 🎯 Best quality (4K if available)   ║
║ 2. 🖥  1080p HD                         ║
║ 3. 💻  720p HD                         ║
║ 4. 📱  480p                            ║
║ 5. 📼  360p                            ║
║ 0. 🚪 Voltar                           ║
╚════════════════════════════════════════╝
\033[0m""")


def mostrar_menu_audio_formatos():
    limpar_tela()
    print("""\033[1;36m
╔════════════════════════════════════════╗
║        🎵 AUDIO FORMAT OPTIONS         ║
╠════════════════════════════════════════╣
║ 1. 🎧 MP3 (High quality 320kbps)       ║
║ 2. 🎵 AAC (High quality)               ║
║ 3. 🎼 FLAC (Lossless)                  ║
║ 4. 🎤 M4A (YouTube default)            ║
║ 5. 🎶 OPUS (Efficient)                 ║
║ 6. 💿 MP3 with cover art               ║
║ 0. 🚪 Voltar                           ║
╚════════════════════════════════════════╝
\033[0m""")


def listar_formatos(link):
    """Lista os formatos disponíveis para download"""
    print("\033[1;36m[•] Listando formatos disponíveis...\033[0m")
    mostrar_barra_progresso("Analisando")

    # Executa o comando para listar formatos
    executar_comando_silencioso(f'yt-dlp --cookies "{ARQUIVO_COOKIES}" -F "{link}"')

    while True:
        limpar_tela()
        mostrar_menu_video_qualidade()
        opcao = input("\n\033[1;36m🎬 Escolha uma opção [0-5]: \033[0m").strip()

        if opcao == "0":
            break
        elif opcao in FORMATOS_VIDEO:
            print("\033[1;33m[•] Iniciando download...\033[0m")

            # Obtém o título antes de começar
            titulo = obter_titulo_video(link)
            if titulo:
                print(f"\033[1;34m[•] Baixando: {titulo}\033[0m")

            if baixar_conteudo(link, 'mp4', FORMATOS_VIDEO[opcao]['code']):
                # Limpa a linha da barra de progresso
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()
                print(f"\033[1;32m[✓] Concluído! Arquivo em: {PASTA_DOWNLOADS}\033[0m")
            break
        else:
            print("\033[1;31m[!] Opção inválida\033[0m")
            time.sleep(1)

print("\033[1;33m[⚡] Usando aria2c para download acelerado\033[0m")

def mostrar_menu_config():
    global ATUALIZAR_COOKIES_AUTO, PASTA_DOWNLOADS  # Declare globals no início
    while True:
        limpar_tela()
        print("""\033[1;36m
╔════════════════════════════════════════╗
║            ⚙️ CONFIGURAÇÕES             ║
╠════════════════════════════════════════╣
║ 1. 📂 Alterar pasta de downloads       ║
║ 2. {} Atualizar cookies automaticamente║
║ 3. ⚡ Instalar todas as dependências   ║
║ 0. 🔙 Voltar                           ║
╚════════════════════════════════════════╝
\033[0m""".format("✅" if ATUALIZAR_COOKIES_AUTO else "❌"))

        opcao = input("\n\033[1;36mEscolha uma opção [0-3]➤ \033[0m").strip()

        if opcao == "1":
            nova_pasta = input("Digite o caminho da nova pasta de downloads: ").strip()
            if os.path.isdir(nova_pasta) and os.access(nova_pasta, os.W_OK):
                PASTA_DOWNLOADS = nova_pasta
                print(f"\033[1;32m[Pasta de downloads alterada para: {PASTA_DOWNLOADS}]\033[0m")
            else:
                print("\033[1;31m[Pasta inválida ou sem permissão de escrita]\033[0m")
            input("Pressione Enter para continuar...")

        elif opcao == "2":
            ATUALIZAR_COOKIES_AUTO = not ATUALIZAR_COOKIES_AUTO
            status = "ativado" if ATUALIZAR_COOKIES_AUTO else "desativado"
            print(f"\033[1;32m[Atualização automática de cookies {status}]\033[0m")
            input("Pressione Enter para continuar...")

        elif opcao == "3":
            print("\033[1;34m[•] Instalando todas as dependências...\033[0m")
            instalar_dependencias_auto()
            input("\n\033[1;36mPressione Enter para continuar...\033[0m")

        elif opcao == "0":
            return

        else:
            print("\033[1;31m[Opção inválida]\033[0m")
            time.sleep(1)

def sinal_handler(sig, frame):
    """Lida com sinais de interrupção salvando o estado"""
    global download_interrompido
    download_interrompido = True

    # Verifica se há um download em andamento
    if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        with open(ARQUIVO_DOWNLOADS_PARCIAL, 'r') as f:
            link = f.readline().strip()
            print("\n\033[1;33m[!] Recebido sinal de interrupção - Estado salvo\033[0m")
            print(f"\033[1;34m[•] Você pode continuar este download depois: {link}\033[0m")

    sys.exit(0)

def continuar_download_unificado():
    """
    Função universal que:
    - Funciona para vídeos E áudios
    - Mostra progresso real sem repetições
    - Mantém a estrutura de pastas organizada
    """
    # Verificação inicial (igual para ambos)
    if not os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        print("\033[1;31m[!] Nenhum download parcial encontrado\033[0m")
        return False

    # Leitura do estado (compatível com ambos)
    try:
        with open(ARQUIVO_DOWNLOADS_PARCIAL, 'r', encoding='utf-8') as f:
            url = f.readline().strip()
            tipo = f.readline().strip()  # 'video' ou 'audio'
            escolha = f.readline().strip()
            baixados = {int(linha.strip()) for linha in f if linha.strip().isdigit()}
    except Exception as e:
        print(f"\033[1;31m[!] Erro ao ler estado: {e}\033[0m")
        return False

    # Obter itens da playlist (comum)
    cmd_info = f'yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "{url}"'
    try:
        result = subprocess.run(cmd_info, shell=True, capture_output=True, text=True, check=True)
        itens = [lin.split(' ', 1) for lin in result.stdout.splitlines() if ' ' in lin]
        todos_itens = {int(idx): tit.strip() for idx, tit in itens}
    except subprocess.CalledProcessError:
        print("\033[1;31m[!] Erro ao obter a playlist\033[0m")
        return False

    pendentes = [idx for idx in sorted(todos_itens) if idx not in baixados]
    if not pendentes:
        print("\033[1;32m[✓] Todos os itens já baixados!\033[0m")
        os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        return True

    # Configuração dinâmica por tipo
    if tipo == 'video':
        formato = FORMATOS_VIDEO.get(escolha, FORMATOS_VIDEO['1'])
        params = f'-f "{formato["code"]}+bestaudio" --merge-output-format mp4'
        output_tpl = f'"{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s"'
    else:  # audio
        formato = FORMATOS_AUDIO.get(escolha, FORMATOS_AUDIO['1'])
        params = formato['params']
        output_tpl = f'"{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s"'

    base_cmd = f'yt-dlp --newline --user-agent "{USER_AGENT}" --cookies "{ARQUIVO_COOKIES}"'
    cmd = f'{base_cmd} {params} -o {output_tpl} --playlist-items {",".join(map(str, pendentes))} "{url}"'

    print(f"\033[1;34m[•] Continuando {tipo}: {len(pendentes)} itens restantes\033[0m")

    # Controle de execução
    processo = None
    item_atual = None
    arquivo_atual = ""
    ultimo_progresso = 0

    try:
        processo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        while True:
            line = processo.stdout.readline()
            if not line and processo.poll() is not None:
                break

            # Captura metadados REAIS
            if "[download] Destination:" in line:
                arquivo_atual = os.path.basename(line.split("Destination:")[1].strip())
                item_atual = next((k for k in todos_itens if str(k) in arquivo_atual), None)

            # Progresso para AMBOS os tipos
            elif item_atual and "[download]" in line and ("%" in line or "ETA" in line):
                progresso = 0
                if "%" in line:
                    match = re.search(r'(\d+\.?\d*)%', line)
                    if match:
                        progresso = float(match.group(1))
                        ultimo_progresso = progresso
                
                pos_real = list(todos_itens.keys()).index(item_atual) + 1
                titulo = arquivo_atual if arquivo_atual else todos_itens.get(item_atual, f"Item {item_atual}")
                
                mostrar_progresso_musica(
                    pos_real,
                    len(todos_itens),
                    titulo,
                    ultimo_progresso,
                    mostrar_spinner()
                )

            # Finalização
            elif "100%" in line and item_atual:
                baixados.add(item_atual)
                with open(ARQUIVO_DOWNLOADS_PARCIAL, 'w', encoding='utf-8') as f:
                    f.write(f"{url}\n{tipo}\n{escolha}\n")
                    f.writelines(f"{idx}\n" for idx in sorted(baixados))
                item_atual = None

    except KeyboardInterrupt:
        if processo:
            processo.terminate()
        print("\n\033[1;31m[!] Download interrompido\033[0m")
        return False

    if processo and processo.returncode == 0:
        print("\n\033[1;32m[✓] Download concluído!\033[0m")
        if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
            os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        return True

    print("\n\033[1;31m[!] Erro no download\033[0m")
    return False

def continuar_download_playlist():
    """
    Versão final que corrige todos os problemas de exibição:
    - Mostra o item REAL sendo baixado
    - Progresso preciso sem repetições
    - Compatível com playlists grandes
    """
    if not os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
        print("\033[1;31m[!] Nenhum download parcial encontrado\033[0m")
        return False

    # Leitura do estado atual
    try:
        with open(ARQUIVO_DOWNLOADS_PARCIAL, 'r', encoding='utf-8') as f:
            url = f.readline().strip()
            tipo = f.readline().strip()
            escolha = f.readline().strip()
            baixados = {int(linha.strip()) for linha in f if linha.strip().isdigit()}
    except Exception as e:
        print(f"\033[1;31m[!] Erro ao ler estado: {str(e)}\033[0m")
        return False

    # Obter todos os itens da playlist
    cmd_info = f'yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "{url}"'
    try:
        resultado = subprocess.run(cmd_info, shell=True, capture_output=True, text=True, check=True)
        itens = [linha.split(' ', 1) for linha in resultado.stdout.strip().split('\n') if ' ' in linha]
        todos_itens = {int(idx): titulo.strip() for idx, titulo in itens}
    except subprocess.CalledProcessError:
        print("\033[1;31m[!] Erro ao obter informações da playlist\033[0m")
        return False

    # Filtrar itens pendentes
    pendentes = [idx for idx in sorted(todos_itens.keys()) if idx not in baixados]
    if not pendentes:
        print("\033[1;32m[✓] Todos os itens já foram baixados!\033[0m")
        os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        return True

    # Configuração do comando
    if tipo == 'video':
        formato = FORMATOS_VIDEO.get(escolha, FORMATOS_VIDEO['1'])
        params = f'-f "{formato["code"]}+bestaudio" --merge-output-format mp4'
    else:
        formato = FORMATOS_AUDIO.get(escolha, FORMATOS_AUDIO['1'])
        params = formato['params']

    base_cmd = f'yt-dlp --newline --user-agent "{USER_AGENT}" --cookies "{ARQUIVO_COOKIES}"'
    output_tpl = f'"{PASTA_DOWNLOADS}/%(playlist_index)s - %(title)s.%(ext)s"'
    cmd = f'{base_cmd} {params} -o {output_tpl} --playlist-items {",".join(map(str, pendentes))} "{url}"'

    print(f"\033[1;34m[•] Continuando download: {len(pendentes)} itens restantes\033[0m")

    # Variáveis de controle
    processo = None
    item_atual = None
    nome_arquivo_atual = ""
    progresso = 0
    spinner_idx = 0

    try:
        processo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        while True:
            line = processo.stdout.readline()
            if not line and processo.poll() is not None:
                break

            # Captura o nome real do arquivo sendo processado
            if "[download] Destination:" in line:
                nome_arquivo_atual = os.path.basename(line.split("Destination:")[1].strip())
                item_atual = next((idx for idx in pendentes if str(idx) in nome_arquivo_atual), None)

            # Atualiza progresso
            elif item_atual and "[download]" in line and "%" in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    progresso = float(match.group(1))
                    posicao_real = list(todos_itens.keys()).index(item_atual) + 1

                    mostrar_progresso_musica(
                        posicao_real,
                        len(todos_itens),
                        nome_arquivo_atual,  # Mostra o nome exato do arquivo
                        progresso,
                        mostrar_spinner()
                    )
                    spinner_idx += 1

            # Item concluído
            elif "[download] 100%" in line and item_atual:
                baixados.add(item_atual)
                with open(ARQUIVO_DOWNLOADS_PARCIAL, 'w', encoding='utf-8') as f:
                    f.write(f"{url}\n{tipo}\n{escolha}\n")
                    for idx in sorted(baixados):
                        f.write(f"{idx}\n")
                item_atual = None

    except KeyboardInterrupt:
        if processo:
            processo.terminate()
        print("\n\033[1;31m[!] Download interrompido\033[0m")
        return False

    if processo and processo.returncode == 0:
        print("\n\033[1;32m[✓] Download concluído com sucesso!\033[0m")
        if os.path.exists(ARQUIVO_DOWNLOADS_PARCIAL):
            os.remove(ARQUIVO_DOWNLOADS_PARCIAL)
        return True
    else:
        print("\n\033[1;31m[!] Erro durante o download\033[0m")
        return False

def main():
    import signal
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    limpar_tela()
    mostrar_banner()
    verificar_e_configurar_ambiente()

    while True:
        limpar_tela()
        mostrar_banner()
        mostrar_menu_principal()
        opcao = input("\n\033[1;36m✨ Escolha uma opção [0-16]➤ \033[0m").strip()

        if opcao == "0":
            limpar_tela()
            break

        elif opcao == "1":
            link = input("\n\033[1;36m🔗 Digite a URL➤ \033[0m").strip()
            if not link.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            mostrar_barra_progresso("Baixando")
            baixar_conteudo(link, 'mp4')
            input("\nPressione Enter para voltar...")

        elif opcao == "2":
            mostrar_menu_video_qualidade()
            q = input("\n\033[1;36m🎬 Escolha a qualidade [0-5]➤ \033[0m").strip()
            if q == "0":
                continue
            if q not in FORMATOS_VIDEO:
                print("\033[1;31m[!] Opção inválida\033[0m")
                time.sleep(1)
                continue
            link = input("\n\033[1;36m🔗 Digite a URL: \033[0m").strip()
            if not link.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            qualidade = FORMATOS_VIDEO[q]['code']
            mostrar_barra_progresso("Baixando")
            baixar_conteudo(link, 'mp4', qualidade)
            input("\nPressione Enter para voltar...")

        elif opcao == "3":
            mostrar_menu_audio_formatos()
            q = input("\n\033[1;36m🎵 Escolha o formato [0-6]➤ \033[0m").strip()
            if q == "0":
                continue
            if q not in FORMATOS_AUDIO:
                print("\033[1;31m[!] Opção inválida\033[0m")
                time.sleep(1)
                continue
            link = input("\n\033[1;36m🔗 Digite a URL: \033[0m").strip()
            if not link.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            formato = FORMATOS_AUDIO[q]
            mostrar_barra_progresso("Baixando")
            baixar_conteudo(link, formato['code'], None, formato['params'])
            input("\nPressione Enter para voltar...")

        elif opcao == "4":
            link = input("\n\033[1;36m🔗 Digite a URL➤ \033[0m").strip()
            if not link.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            print("\033[1;36m[•] Listando formatos disponíveis...\033[0m")
            comando = f'yt-dlp --cookies "{ARQUIVO_COOKIES}" -F "{link}"'
            subprocess.run(comando, shell=True)
            print("\033[1;33m[•] Para baixar em um formato específico, use o menu 2.\033[0m")
            input("\033[1;36mPressione Enter para voltar ao menu...\033[0m")

        elif opcao == "5":
            url = input("🔗 Digite a URL da playlist➤ ").strip()
            if not url.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            sucesso = baixar_playlist_com_progresso(url, tipo='video')
            if sucesso:
                print("\033[1;32m[✓] Download da playlist de vídeos concluído com sucesso!\033[0m")
            else:
                print("\033[1;31m[!] Falha no download da playlist de vídeos.\033[0m")
            input("\nPressione Enter para voltar...")

        elif opcao == "6":
            url = input("🔗 Digite a URL da playlist➤ ").strip()
            if not url.startswith(('http://', 'https://')):
                print("\033[1;31m[!] URL inválida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            sucesso = baixar_playlist_com_progresso(url, tipo='audio')
            if sucesso:
                print("\033[1;32m[✓] Download da playlist de áudios concluído com sucesso!\033[0m")
            else:
                print("\033[1;31m[!] Falha no download da playlist de áudios.\033[0m")
            input("\nPressione Enter para voltar...")

        elif opcao == "7":
            print("\033[1;36m[•] Modo múltiplas URLs (CTRL+D para finalizar)\033[0m")
            print("\033[1;33m[•] Cole as URLs uma por linha:\033[0m")
            urls = []
            try:
                while True:
                    url = input().strip()
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
                    elif url:
                        print("\033[1;31m[!] URL inválida\033[0m")
            except EOFError:
                pass
            if not urls:
                print("\033[1;31m[!] Nenhuma URL fornecida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            mostrar_menu_video_qualidade()
            opcao_q = input("\n\033[1;36m🎬 Escolha a qualidade [1-5]: \033[0m").strip()
            qualidade = FORMATOS_VIDEO[opcao_q]['code'] if opcao_q in FORMATOS_VIDEO else 'best'
            for i, url in enumerate(urls, 1):
                print(f"\n\033[1;35m[•] Baixando URL {i}/{len(urls)}\033[0m")
                mostrar_barra_progresso("Processando")
                baixar_conteudo(url, 'mp4', qualidade)
            input("\nPressione Enter para voltar...")

        elif opcao == "8":
            print("\033[1;36m[•] Modo múltiplas URLs (CTRL+D para finalizar)\033[0m")
            print("\033[1;33m[•] Cole as URLs uma por linha:\033[0m")
            urls = []
            try:
                while True:
                    url = input().strip()
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
                    elif url:
                        print("\033[1;31m[!] URL inválida\033[0m")
            except EOFError:
                pass
            if not urls:
                print("\033[1;31m[!] Nenhuma URL fornecida\033[0m")
                input("\nPressione Enter para voltar...")
                continue
            mostrar_menu_audio_formatos()
            opcao_q = input("\n\033[1;36m🎵 Escolha o formato [1-6]: \033[0m").strip()
            formato = FORMATOS_AUDIO[opcao_q] if opcao_q in FORMATOS_AUDIO else FORMATOS_AUDIO['1']
            for i, url in enumerate(urls, 1):
                print(f"\n\033[1;35m[•] Baixando URL {i}/{len(urls)}\033[0m")
                mostrar_barra_progresso("Processando")
                baixar_conteudo(url, formato['code'], None, formato['params'])
            input("\nPressione Enter para voltar...")

        elif opcao == "9":
            instalar_dependencias_auto()
            input("\nPressione Enter para voltar...")

        elif opcao == "10":
            atualizar_cookies()
            input("\nPressione Enter para voltar...")

        elif opcao == "11":
            mostrar_menu_config()

        elif opcao == "12":
            sucesso = continuar_download_playlist()
            if sucesso:
                print("\033[1;32m[✓] Download continuado com sucesso!\033[0m")
            else:
                print("\033[1;31m[!] Não foi possível continuar o download.\033[0m")
            input("\nPressione Enter para voltar...")

        elif opcao == "13":
            player_integrado()

        elif opcao == "14":
            limpar_arquivos_temporarios()

        elif opcao == "15":
            editar_cookies()
            input("\nPressione Enter para voltar...")

        elif opcao == "16":
            atualizar_script()
            
        elif opcao == "17":
            baixar_spotify_deezer()
            input("\nPressione Enter para voltar...")

        else:
            print("\033[1;31m[!] Opção inválida\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    main()
