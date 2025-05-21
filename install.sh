#!/data/data/com.termux/files/usr/bin/bash

# Cores ANSI
green="\033[1;32m"
red="\033[1;31m"
yellow="\033[1;33m"
blue="\033[1;34m"
cyan="\033[1;36m"
reset="\033[0m"

# Banner COMPLETO (comece com aspas duplas, termine só com aspas duplas na linha final)
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

# Função barra de progresso colorida
progress_bar() {
  local task="$1"
  local cmd="$2"
  local color="$3"
  local cols=30
  local i=0
  local delay=0.08

  echo -e "${color}${task}...${reset}"

  bash -c "$cmd" &> /dev/null &
  local pid=$!

  while kill -0 $pid 2> /dev/null; do
    i=$(( (i+1) % (cols+1) ))
    local filled=$i
    local empty=$((cols - filled))
    local bar="$(printf '%0.s█' $(seq 1 $filled))$(printf '%0.s-' $(seq 1 $empty))"
    printf "\r[${green}%s${reset}] %3d%%" "$bar" $((i*100/cols))
    sleep $delay
  done

  wait $pid
  local status=$?
  if [ $status -eq 0 ]; then
    printf "\r[${green}$(printf '%0.s█' $(seq 1 $cols))${reset}] 100%% ${green}[Sucesso]${reset}\n"
  else
    printf "\r[${red}$(printf '%0.s█' $(seq 1 $cols))${reset}] 100%% ${red}[Falha]${reset}\n"
    exit 1
  fi
}

clear
echo -e "${cyan}$banner${reset}"
echo -e "${yellow}Iniciando instalação das dependências do Wolf no Termux...${reset}"

progress_bar "Atualizando pacotes" "pkg update -y && pkg upgrade -y" "$blue"
progress_bar "Instalando Python" "pkg install python -y" "$yellow"
progress_bar "Instalando FFmpeg" "pkg install ffmpeg -y" "$yellow"
progress_bar "Instalando wget, git e aria2" "pkg install wget git aria2 -y" "$yellow"
progress_bar "Instalando yt-dlp (pip)" "pip install --upgrade yt-dlp" "$green"
progress_bar "Instalando requests (pip)" "pip install --upgrade requests" "$green"

echo -e "${blue}Configurando permissão de armazenamento (termux-setup-storage)...${reset}"
termux-setup-storage
echo -e "${green}Permissão de armazenamento configurada. Por favor, conceda permissão se solicitado.${reset}"

echo -e "${green}Todas as dependências foram instaladas com sucesso!${reset}"
echo -e "${cyan}Agora execute: ${yellow}python3 wolf-9.0.py${reset}"
