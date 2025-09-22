FROM python:3.12.11-slim

RUN apt-get update

RUN apt-get install libreoffice inkscape ffmpeg xvfb -y

RUN apt-get install poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl ghostscript libsecret-1-0 zlib1g-dev libjpeg-dev imagemagick libmagic1 webp -y

RUN apt-get install curl -y

RUN DRAWIO_VERSION="15.7.3" && curl -LO https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-x86_64-${DRAWIO_VERSION}.AppImage && mv drawio-x86_64-${DRAWIO_VERSION}.AppImage /usr/local/bin/drawio

WORKDIR /opt/fps

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]