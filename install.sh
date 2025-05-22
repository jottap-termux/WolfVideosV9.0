#!/data/data/com.termux/files/usr/bin/bash

# Cores ANSI
green="\033[1;32m"
red="\033[1;31m"
yellow="\033[1;33m"
blue="\033[1;34m"
cyan="\033[1;36m"
reset="\033[0m"

# Banner COMPLETO (exatamente como no original)
banner="

              ⢶                                   ⡾⡀
             ⢰⣄⢷⡀                               ⢀⡾⣡⠇
             ⢰⠙⣦⡙⢦⡀      ⡀⣄⡀ ⡴⠸⣄ ⣠⠎⢦ ⢀⣠⢀      ⢀⡴⢋⣴⠏⡆
             ⣾ ⠘⢯⣦⣉⡳⠦⣄⡾⠶⠄⠛⢄⠉⣙⠁⣆⣌⠶⢃⣰⠈⢛⠉⠠⠚⠢⠶⠿⣠⠤⠞⣋⢴⡿⠋ ⣷
             ⣿⢠ ⠈⢻⡻⣽⣶⣦⣄⠠⣄⠕⣤⣢⣞⣷⡜⣿⣶⣿⢧⣾⣷⣗⣤⠪⢀⠄⣠⣴⣶⣟⣟⡟⠁ ⢠⣿
            ⢠⡿⡸⡂  ⠓⠘⢦ ⠁⠁⠘⣦⢪⢿⣿⣿⠻⣿⣿⣿⠟⣿⣿⣿⡵⣴⠃⠘⠉⠐⡵⠋⠞  ⢀⢇⣻⡆
            ⢸⡇⣧⡀   ⠄⠘⣧   ⠸⣿⣿⣿⣿⣇⠘⣿⠃⣸⣿⣿⣿⣿⠇   ⣼⠃    ⠘⢼⡸⡇
            ⢸⠁⢿⡳     ⠘⣧⡘⣦⣷⣻⢿⡿⣿⣿⣧ ⣰⣿⣿⢿⡿⣿⣼⣴⣇⣼⠃    ⢀⠞⣿ ⡇
          ⢀⡀⢸⡀⡈⢷⠄  ⠄⣲⣶⣾⡿⠿⢝⠿⢷⡕⠸⡿⣿⢷⣿⣯⡏⢪⡾⠫⣻⠿⢿⣷⣶⣖⠢   ⡾⢃ ⡇⢀⡀
          ⠈⢯⡛⠁⠘    ⡴⣖⣚⣿⣧⣄⠠⡀ ⠹⣆⢳⠉ ⠉⡞⣠⠏ ⢀⠄⣠⣼⣿⣓⣒⠦    ⠂⡈⠛⡿⠁
          ⢀⡴⢋⣤⣤⡖⠋⠁ ⣠⣴⣟⢿⡿⣿⣿⣽⣦⣄⠈⠎⠣ ⠘⠱⠁⢠⣴⣯⣿⣿⢿⡿⣿⣦⣄ ⠈⠛⣶⣦⣄⡘⢦⡀
         ⠠⢟⡖⢀⣤⡤⠔⠂⠠⠼⢿⡡⠌⠁⠈⡀⠻⣝⣿⣿⣆⡆   ⢠⣴⣿⣿⢿⠟⢁⠁⠈ ⢉⡿⠷⠄⠐⠢⠤⣤⡀⢲⡛⠄
          ⡞⠐⡻⠉    ⣀⡬  ⡤⡀⠻⣦⡀⠙⣿⡿⠇   ⠸⢿⣿⠃⢁⣴⡟⢀⣤  ⢥⣄    ⠉⢝⠂⢻
         ⢰⢇⣼⣧⢾⣽⡂⢠⣾⠿⢿⣿⣧⣝⣿⣦⣄    ⠠⣴⣀⣦⡤    ⣀⣴⣟⣫⣴⣿⣿⠿⣷⣄⢀⢮⡷⢮⣧⡘⣇
        ⢀⣿⡚⠉⠐⣩⡯⠖⢀⣤⢆⡀ ⠉⠛⢻⡭  ⠲⢮⣽⣦⠸⣿⠏⣴⣏⡽⠖  ⢹⡟⠛⠋  ⡰⣤⡄⠰⢽⣍⠂⠉⢛⣿⡄
        ⠉⠉⣠ ⢚⡭⠂ ⢉⣾⡿⠉   ⢠⡶⢿⣷⣿⣦⠸⠿⠳⠉⠞⠿⠏⣴⣿⣾⡿⢶⣄   ⠨⢿⣷⡍ ⠐⢮⡓⠄⣄⠉⠉
          ⡏⡴⢋⣔⠄  ⡟ ⡴⣾  ⡏ ⢰⣿⢿⡇⠐⠊⠻⣿⠟⠉⠂⢹⣿⣿⡞ ⠸⡄ ⢳⢦ ⢻  ⠠⡢⡙⢦⣹
         ⢀⠟⡀⢸⣿⠊  ⠃ ⠁⡏⡆  ⠐⢌⠻⣟⣧⡀     ⢀⣼⣳⡟⡡⠂  ⢰⢿⠈⠂⠈  ⠑⣽⡇⢀⠻⡀
           ⡇⢸⡧  ⡀   ⠁⢟⣆  ⠠⡓⢽⡿⡗⠆   ⠠⢾⢟⡿⢊⠅ ⢠⣸⡻⠈   ⢀  ⢾⡇⢸
           ⡇⠈⣠⡎⣾⠄⠰⡁⠄  ⠈⢻⡀  ⠁         ⠈⡀ ⢀⡾⠁   ⣀⠆ ⣳⢰⣄⠁⢸
           ⢹⣰⠋⣧⠟⢀⢀⣿⡔⢰⠇  ⠁  ⣿ ⡇⢰⢠ ⡆⡆⢸ ⣷⠁ ⠈  ⠐⡆⢢⣻⡀⡀⠻⣸⠙⣆⡞
           ⠘⠇ ⠸⡄⡾⣆⠻⡇⠘ ⢀   ⢀⠹         ⠏    ⡀ ⠃⢸⠟⣰⣿⢀⠏ ⠸⠃
               ⢻⠁⣿ ⣴ ⢸⢺   ⠘ ⢸       ⡇ ⡇   ⢳⡄ ⣶ ⢹⠈⡟
                 ⢸⡜⠹⠳⣌⣿⡄  ⢇ ⢻⢠     ⡄⡯ ⢰  ⢠⣿⢡⠞⠏⢧⡏
                  ⠁  ⠈⠫⢳⣔⢠  ⡌⠈⠋⠃⠂⠘⠉⠁⢁  ⡄⣤⡞⠝⠁  ⠈
                        ⠙⢶⡆⣦⠈⠓⠒⠒⠒⠒⠒⠚⠁⣰⢠⣵⠋
                          ⠙⠘⢧⡈⢾⣴⣾⣦⠶⢃⡼⠃⠋
                             ⠙⢦⡈⠛⢃⡴⠋
                               ⠙⢶⠋


                ⣰⣦⡀       ⢠⡄  ⡰⣶⣲⣤  ⢰⡶ ⣠⣴⣶⣶⣴⣒
                ⢻⣿⡇  ⣤⣷   ⣼⡇ ⡟⡟⠉⠉⢻⣆ ⢸⡇ ⣿⣿⡇
                ⢨⣿⣇  ⢻⣿  ⢀⣿⠁⢸⡯   ⢸⣿ ⣺⡇ ⠸⣿⣿⡿⠿⠛
                 ⢿⣿⡀⢀⣾⢿⣦ ⣼⡇ ⠸⡇   ⣸⡿ ⣺⠅  ⣿⡇
                 ⠈⣿⣇⣾⠇⠈⣿⣿⡟   ⠯⢶⣶⠾⠟⠁ ⢿⣦⡶⠄⢹⠇    𓃦ᨒꨄ︎ 🐾
                  ⠘⢿⠏  ⠈⠛⠁


        ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓█▓▒░
        ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░  ░▒▓█▓▒░
"

# Função para verificar conexão com a internet
check_internet() {
  echo -e "${yellow}Verificando conexão com a internet...${reset}"
  if ! ping -c 1 google.com &> /dev/null; then
    echo -e "${red}Erro: Sem conexão com a internet!${reset}"
    echo -e "${yellow}Por favor, conecte-se à internet e tente novamente.${reset}"
    exit 1
  fi
}

# Função barra de progresso melhorada
progress_bar() {
  local task="$1"
  local cmd="$2"
  local color="$3"
  local cols=30
  local i=0
  local delay=0.08

  echo -ne "${color}${task}...${reset}"

  bash -c "$cmd" &> /dev/null &
  local pid=$!

  while kill -0 $pid 2> /dev/null; do
    i=$(( (i+1) % (cols+1) ))
    printf "\r${color}${task}... [%s] %3d%%" \
           "$(printf '%0.s█' $(seq 1 $i))$(printf '%0.s░' $(seq $((i+1)) $cols))" \
           $((i*100/cols))
    sleep $delay
  done

  wait $pid
  local status=$?

  if [ $status -eq 0 ]; then
    printf "\r${color}${task}... [$(printf '%0.s█' $(seq 1 $cols))] 100%% ${green}sucesso [✔]${reset}\n"
  else
    printf "\r${color}${task}... [$(printf '%0.s█' $(seq 1 $cols))] 100%% ${red}falhou [✘]${reset}\n"
    echo -e "${red}Erro no comando: ${cmd}${reset}"
    exit 1
  fi
}

# Função principal
main() {
  clear
  echo -e "${cyan}$banner${reset}"
  echo -e "${yellow}Iniciando instalação das dependências do Wolf no Termux...${reset}"

  check_internet

  # Atualizar e instalar pacotes
  progress_bar "Atualizando pacotes" "pkg update -y && pkg upgrade -y" "$green"
  progress_bar "Instalando Python" "pkg install python -y" "$green"
  progress_bar "Instalando FFmpeg" "pkg install ffmpeg -y" "$green"
  progress_bar "Instalando utilitários" "pkg install wget git aria2 -y" "$green"
  progress_bar "Instalando yt-dlp" "pip install --upgrade yt-dlp" "$green"
  progress_bar "Instalando requests" "pip install --upgrade requests" "$green"

  # Configurar armazenamento
  echo -e "\n${blue}Configurando permissão de armazenamento...${reset}"
  if termux-setup-storage; then
    echo -e "${green}Permissão concedida com sucesso!${reset}"
  else
    echo -e "${yellow}Aviso: Não foi possível configurar o armazenamento automaticamente${reset}"
    echo -e "${yellow}Você pode tentar manualmente depois executando: termux-setup-storage${reset}"
  fi

  # Mensagem final
  echo -e "\n${green}Todas as dependências foram instaladas com sucesso!${reset}"
  echo -e "${cyan}Agora você pode executar o Wolf com: ${yellow}python3 wolf-9.0.py${reset}"
  echo -e "${blue}🐺 Divirta-se com o Wolf! ${reset}"
}

# Executa a função principal
main
