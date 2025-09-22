# file-preview-service

## Build & run

```bash
docker build -t file-preview-service .
docker run -v ./data/:/opt/fps_data/ -p 8000:8000 -it file-preview-service
```