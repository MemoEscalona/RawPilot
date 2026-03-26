# core/raw_loader.py
from pathlib import Path
from typing import Dict, Any, Optional

import rawpy
import numpy as np
import cv2

from utils.metadata_utils import extract_exif_metadata
from domain.models import LoadedImage

SUPPORTED_RAW_EXTENSIONS = {
    ".cr2", 
    ".cr3", 
    ".nef", 
    ".arw", 
    ".dng", 
    ".raf", 
    ".rw2", 
    ".orf"
}

def load_raw(path:str, working_max_size: int = 2048) -> LoadedImage:
    """
    Carga un archivo RAW, extrae metadata
    básica y genera:
    -rgb_image: preview RGB principal
    -working_image: imagen optimizada para análisis

    Args:
        path: ruta al archivo RAW
        working_max_size: tamaño máximo para la imagen de trabajo (mantiene proporción) 
    
    Returns:
        LoadedImage: dataclass con imágenes y metadata
    """
    _validate_raw_path(path)

    try:
        exif_metadata = extract_exif_metadata(path)
        with rawpy.imread(path) as raw:
            technical_metadata = _extract_basic_metadata(raw, path)
            
            metadata={
                **exif_metadata, 
                **technical_metadata
            }
            rgb_image = _generate_rgb_preview(raw)
            height, width = rgb_image.shape[:2]
            working_image= _resize_for_analysis(
                rgb_image, 
                max_size=working_max_size
            )

            return LoadedImage(
                file_path=str(path),
                rgb_image=rgb_image,
                working_image=working_image,
                width=width,
                height=height,
                camera_model=metadata.get("camera_model"),
                camera_make=metadata.get("camera_make"),
                lens_model=metadata.get("lens_model"),
                iso=metadata.get("iso"),
                shutter_speed=metadata.get("shutter_speed"),
                aperture=metadata.get("aperture"),
                focal_length=metadata.get("focal_length"),
                datetime_original=metadata.get("datetime_original"),
                color_description=metadata.get("color_description"),
                black_level_per_channel=metadata.get("black_level_per_channel"),
                white_level=metadata.get("white_level"),
                raw_pattern=metadata.get("raw_pattern"),
                metadata=metadata 
            )
    except Exception as e:
        raise RuntimeError(f"Error cargando RAW '{path}': {e}") from e

def _validate_raw_path(path: str) -> None:
    """
    Valida que el archivo exista y 
    tenga una extensión RAW soportada.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    if not file_path.is_file():
        raise ValueError(f"La ruta no apunta a un archivo válido: {path}")

    if file_path.suffix.lower() not in SUPPORTED_RAW_EXTENSIONS:
        raise ValueError(
            f"Extensión no soportada: {file_path.suffix}. "
            f"Soportadas: {sorted(SUPPORTED_RAW_EXTENSIONS)}"
        )

def _extract_basic_metadata(raw: rawpy.RawPy, path: str) -> Dict[str, Any]:
    """
    Extrae metadata útil desde rawpy.
    Nota: rawpy no expone EXIF completo como lo haría exiftool,
    pero sí varios datos técnicos valiosos.
    """
    metadata: Dict[str, Any] = {
        "file_name": Path(path).name,
        "color_description": _safe_decode(getattr(raw, "color_desc", None)),
        "camera_whitebalance": _safe_to_list(
            getattr(raw, "camera_whitebalance", None)
        ),
        "black_level_per_channel": _safe_to_list(
            getattr(raw, "black_level_per_channel", None)
        ),
        "white_level": getattr(raw, "white_level", None),
        "raw_pattern": _safe_to_list(getattr(raw, "raw_pattern", None)),
        "num_colors": getattr(raw, "num_colors", None),
        "sizes": _extract_sizes(raw),
    }

    return metadata

def _extract_sizes(raw: rawpy.RawPy) -> Dict[str, Optional[int]]:
    """
    Extrae tamaños relevantes del RAW.
    """
    try:
        sizes = raw.sizes
        return {
            "raw_width": getattr(sizes, "raw_width", None),
            "raw_height": getattr(sizes, "raw_height", None),
            "width": getattr(sizes, "width", None),
            "height": getattr(sizes, "height", None),
            "iwidth": getattr(sizes, "iwidth", None),
            "iheight": getattr(sizes, "iheight", None),
            "pixel_aspect": getattr(sizes, "pixel_aspect", None),
        }
    except Exception:
        return {}
    
def _safe_to_list(value: Any) -> Optional[list]:
    """
    Convierte arrays/tuplas/valores numéricos a lista serializable.
    """
    if value is None:
        return None

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, list):
        return value

    return [value]

def _safe_decode(value: Any) -> Optional[str]:
    """
    Convierte bytes u otros valores a string seguro.
    """
    if value is None:
        return None

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="ignore")
        except Exception:
            return str(value)

    if isinstance(value, np.ndarray):
        try:
            return "".join(chr(x) for x in value if x > 0)
        except Exception:
            return str(value)

    return str(value)

def _generate_rgb_preview(raw: rawpy.RawPy) -> np.ndarray:
    """
    Genera una imagen RGB utilizable para análisis visual.
    """
    rgb = raw.postprocess(
        use_camera_wb=True,
        no_auto_bright=True,
        output_bps=8,
        demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
        gamma=(2.222, 4.5),
        user_flip=0,
    )

    return rgb

def _resize_for_analysis(image: np.ndarray, max_size: int = 1600) -> np.ndarray:
    """
    Redimensiona la imagen para análisis, preservando proporción.
    """
    h, w = image.shape[:2]
    longest_side = max(h, w)

    if longest_side <= max_size:
        return image.copy()

    scale = max_size / longest_side
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )
    return resized