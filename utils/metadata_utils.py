from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import json
import shutil


def is_exiftool_available() -> bool:
    """
    Verifica si ExifTool está disponible en el entorno.
    """
    return shutil.which("exiftool") is not None


def get_exiftool_version() -> Optional[str]:
    """
    Devuelve la versión de ExifTool si está disponible.
    """
    if not is_exiftool_available():
        return None

    try:
        result = subprocess.run(
            ["exiftool", "-ver"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except Exception:
        return None


def extract_exif_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extrae metadata fotográfica rica desde un archivo RAW usando ExifTool.

    Args:
        file_path: Ruta al archivo RAW.

    Returns:
        Diccionario normalizado con metadata útil.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    if not is_exiftool_available():
        print("[WARN] ExifTool no está disponible en el entorno.")
        return {}

    try:
        result = subprocess.run(
            ["exiftool", "-j", str(path)],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        if not data:
            return {}

        raw_meta = data[0]
        return _normalize_exiftool_metadata(raw_meta)

    except subprocess.CalledProcessError as e:
        print(f"[WARN] Error ejecutando ExifTool: {e.stderr}")
        return {}

    except json.JSONDecodeError as e:
        print(f"[WARN] Error parseando JSON de ExifTool: {e}")
        return {}

    except Exception as e:
        print(f"[WARN] Error inesperado extrayendo metadata: {e}")
        return {}


def debug_exiftool_read(file_path: str) -> Dict[str, Any]:
    """
    Devuelve la salida RAW completa de ExifTool para debugging.
    Útil cuando queremos inspeccionar campos disponibles del archivo.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    if not is_exiftool_available():
        raise RuntimeError("ExifTool no está disponible en el entorno.")

    result = subprocess.run(
        ["exiftool", "-j", str(path)],
        capture_output=True,
        text=True,
        check=True
    )

    data = json.loads(result.stdout)

    if not data:
        return {}

    return data[0]


def _normalize_exiftool_metadata(raw_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza la metadata devuelta por ExifTool a un esquema interno consistente.
    """
    return {
        "camera_make": raw_meta.get("Make"),
        "camera_model": raw_meta.get("Model"),
        "lens_model": raw_meta.get("LensModel") or raw_meta.get("LensID"),
        "iso": raw_meta.get("ISO"),
        "shutter_speed": raw_meta.get("ExposureTime"),
        "aperture": raw_meta.get("FNumber"),
        "focal_length": raw_meta.get("FocalLength"),
        "datetime_original": raw_meta.get("DateTimeOriginal"),
        "software": raw_meta.get("Software"),
        "white_balance_mode": raw_meta.get("WhiteBalance"),
        "exposure_compensation": raw_meta.get("ExposureCompensation"),
        "metering_mode": raw_meta.get("MeteringMode"),
        "flash": raw_meta.get("Flash"),
        "orientation": raw_meta.get("Orientation"),
        "color_space": raw_meta.get("ColorSpace"),
    }