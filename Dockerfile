FROM python:3.12.11-slim@sha256:47ae396f09c1303b8653019811a8498470603d7ffefc29cb07c88f1f8cb3d19f

RUN apt-get update

RUN apt-get install \
libreoffice inkscape ffmpeg xvfb poppler-utils \
libfile-mimeinfo-perl libimage-exiftool-perl ghostscript \
libsecret-1-0 zlib1g-dev libjpeg-dev imagemagick \
libmagic1 webp curl -y

RUN DRAWIO_VERSION="15.7.3" && curl -LO https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-x86_64-${DRAWIO_VERSION}.AppImage && mv drawio-x86_64-${DRAWIO_VERSION}.AppImage /usr/local/bin/drawio

RUN rm -rf /var/lib/apt/lists/*

WORKDIR /opt/fps

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9311"]
CMD ["python3", "main.py"]