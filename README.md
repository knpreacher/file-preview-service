# File Preview Service (FPS)

## Description

[**File preview service**](https://github.com/knpreacher/file-preview-service.git) - generating previews from source files. This service is intended to be used in conjunction with a web application to provide preview images for files uploaded by users.

## Build & run

```bash
docker build -t file-preview-service .
docker run -v ./data/:/opt/fps_data/ -p 8000:8000 -it file-preview-service
```

## Environment variables


### `FPS_DEBUG`
- **Type**: Boolean (`true` / `false`)
- **Default**: `false`
- **Description**: Enables or disables debug mode. When set to `true`, FPS will output verbose logs and diagnostic information to assist with troubleshooting.
- **Example**:
  ```bash
  FPS_DEBUG=true
  ```

---

### `FPS_DOCUMENT_ROOT`
- **Type**: Filesystem Path (String)
- **Required**: Yes
- **Description**: Specifies the root directory where source documents are stored and served from. FPS will scan and generate previews for files under this path.
- **Example**:
  ```bash
  FPS_DOCUMENT_ROOT=/opt/fps_data/docs
  ```

---

### `FPS_CACHE_ROOT`
- **Type**: Filesystem Path (String)
- **Required**: Yes
- **Description**: Defines the directory where FPS stores generated preview files and other cached assets to improve performance and reduce redundant processing.
- **Example**:
  ```bash
  FPS_CACHE_ROOT=/opt/fps_data/cache
  ```

---

### `FPS_WATERMARK_LIGHT_PATH`
- **Type**: Filesystem Path (String)
- **Optional**: Yes
- **Description**: Path to the watermark image used for light-themed previews (e.g., white or bright backgrounds). Typically a dark logo for contrast.
- **Example**:
  ```bash
  FPS_WATERMARK_LIGHT_PATH=/opt/fps_data/logo_black.png
  ```

---

### `FPS_WATERMARK_DARK_PATH`
- **Type**: Filesystem Path (String)
- **Optional**: Yes
- **Description**: Path to the watermark image used for dark-themed previews (e.g., black or dark backgrounds). Typically a light/white logo for contrast.
- **Example**:
  ```bash
  FPS_WATERMARK_DARK_PATH=/opt/fps_data/logo_white.png
  ```

---

### `FPS_WATERMARK_PATH` *(Deprecated / Optional)*
- **Type**: Filesystem Path (String)
- **Optional**: Yes
- **Description**: Legacy or fallback watermark path. If `FPS_WATERMARK_LIGHT_PATH` or `FPS_WATERMARK_DARK_PATH` are not provided, this path may be used as a default watermark for all themes. Currently commented out in default config.
- **Example**:
  ```bash
  # FPS_WATERMARK_PATH=/opt/fps_data/logo_default.png
  ```

---

## Example Configuration

```bash
FPS_DEBUG=true
FPS_DOCUMENT_ROOT=/opt/fps_data/docs
FPS_CACHE_ROOT=/opt/fps_data/cache
FPS_WATERMARK_LIGHT_PATH=/opt/fps_data/logo_black.png
FPS_WATERMARK_DARK_PATH=/opt/fps_data/logo_white.png
```

> 💡 **Note**: Ensure all specified directories and files exist and are readable by the FPS process. Missing paths may cause runtime errors or skipped features (e.g., no watermark applied).

---

## Best Practices

- Set `FPS_DEBUG=false` in production to avoid performance overhead and log flooding.
- Use absolute paths for all filesystem variables.
- Ensure watermark images are optimized for transparency and appropriate sizing.
- Regularly clean `FPS_CACHE_ROOT` to manage disk usage if previews are frequently regenerated.
