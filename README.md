# RawPilot

RawPilot es un pipeline de preprocesamiento y analisis para archivos RAW fotograficos.
Toma una imagen RAW, extrae metadata, analiza caracteristicas visuales y genera un archivo `.xmp` con ajustes base compatibles con Lightroom/Camera Raw.

## Objetivo

- Automatizar un punto de partida de revelado para fotos RAW.
- Traducir metricas de imagen en decisiones editables.
- Reducir trabajo repetitivo antes del ajuste creativo final.

## Flujo de trabajo

1. Carga de RAW (`core/raw_loader.py`)
2. Extraccion de metadata EXIF via ExifTool (`utils/metadata_utils.py`)
3. Analisis visual de imagen (`core/analyzer.py`)
4. Motor de decisiones de edicion (`core/decision_engine.py`)
5. Generacion de archivo XMP (`core/xmp_generator.py`)
6. Impresion de resumenes en consola (`utils/report_utils.py`)

## Estructura principal

```text
.
|-- main.py
|-- core/
|   |-- raw_loader.py
|   |-- analyzer.py
|   |-- decision_engine.py
|   `-- xmp_generator.py
|-- domain/
|   `-- models.py
|-- utils/
|   |-- metadata_utils.py
|   `-- report_utils.py
|-- Dockerfile
|-- docker-compose.yml
`-- requirements.txt
```

## Requisitos

- Python 3.11+
- Dependencias Python:
  - rawpy
  - numpy
  - opencv-python
  - exifread
- ExifTool instalado en el sistema (recomendado para metadata rica)

Nota: si ExifTool no esta disponible, el pipeline sigue funcionando pero con metadata mas limitada.

## Instalacion local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracion de entrada

En `main.py` actualmente se usa una ruta fija:

```python
raw_file = "/data/raws/IMG_4080.CR3"
```

Antes de ejecutar, asegurate de que ese archivo exista o cambia la ruta a tu RAW.

## Ejecucion local

```bash
python main.py
```

## Ejecucion con Docker

Construir y levantar contenedor:

```bash
docker compose up --build
```

Segun `docker-compose.yml`, el volumen de RAW esta mapeado a `/data/raws` dentro del contenedor.
Revisa y ajusta ese mapping a una carpeta valida en tu equipo.

## Salida esperada

- Resumen en consola de:
  - Metadata fotografica
  - Analisis tonal/color/contraste
  - Decisiones de edicion
- Archivo `.xmp` junto al RAW original (si no existe uno previo)

Si el `.xmp` ya existe, no se sobrescribe.

## Parametros de edicion generados

El motor produce ajustes base como:

- `Exposure2012`
- `Contrast2012`
- `Highlights2012`
- `Shadows2012`
- `Whites2012`
- `Blacks2012`
- `Temp`
- `Tint`
- `Vibrance`
- `Saturation`

## Notas de desarrollo

- `core/analyzer.py` clasifica la escena en perfiles como `high_key`, `low_key`, `balanced`.
- `core/decision_engine.py` transforma analisis en reglas de ajuste con trazabilidad (`decision_log`).
- `core/xmp_generator.py` serializa ajustes como atributos `crs:*` en XML XMP.

## Mejoras recomendadas

- Permitir ruta RAW por argumento CLI en vez de hardcode en `main.py`.
- Agregar tests unitarios para analizador y motor de decisiones.
- Soportar procesamiento por lotes de una carpeta completa.
- Agregar configuracion externa de reglas (por ejemplo YAML/JSON).

## Licencia

Define aqui la licencia del proyecto (por ejemplo MIT, Apache-2.0, etc.).