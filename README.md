Wolf Video Downloader 9.0

Wolf é um script completo para baixar vídeos e músicas de diversas plataformas (YouTube, Spotify, Deezer, etc), com suporte a playlists, múltiplos formatos, progresso visual e player integrado. Ideal para uso no Termux, mas compatível com sistemas Linux em geral.

Recursos

Download de vídeos em 4K, 1080p, 720p, 480p ou 360p.

Conversão para MP3, AAC, FLAC, M4A, OPUS e MP3 com capa.

Player integrado para visualizar e ouvir arquivos diretamente.

Suporte a playlists do YouTube e Spotify com retomada de progresso.

Download em lote com múltiplas URLs.

Suporte a cookies atualizados automaticamente.

Uso de aria2c para download acelerado (opcional).

Modo gráfico em terminal com menus interativos.

Instalação automática via install.sh.


Instalação (via Termux)

•pkg update && pkg upgrade -y

•pkg install git -y

•git clone https://github.com/jottap-termux/wolf

•cd wolf

•chmod +x install.sh

•bash install.sh

Execução

python3 wolf-9.0.py

Menu principal

O script apresenta um menu com as seguintes opções:

Baixar vídeo (melhor qualidade)

Escolher qualidade específica

Converter para áudio

Baixar playlists (vídeo ou áudio)

Baixar múltiplos links

Atualizar cookies ou dependências

Editar cookies manualmente

Player de mídia integrado

Retomar downloads interrompidos


Requisitos

Python 3

yt-dlp

ffmpeg

requests

aria2c (opcional, para acelerar downloads)

termux-api (para player no Termux)


As dependências são instaladas automaticamente pelo script.

Pasta de Downloads

Os arquivos são salvos em:

/sdcard/WolfVideos

Essa pasta pode ser alterada nas configurações do script.

Atualização

Para atualizar o script:

python3 wolf-9.0.py
# Escolha a opção "Atualizar script"

Ou use manualmente:

wget -O wolf-9.0.py https://raw.githubusercontent.com/jottap-termux/wolf/main/wolfv8.5.py

Autor

Criado por: Jottap_62

Instagram: @jottap_62

![17477353053098062051895840781719](https://github.com/user-attachments/assets/12feb846-3692-450b-b697-ddd9ec06eecb)

