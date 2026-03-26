from pathlib import Path
from typing import Dict, Any, Optional
import xml.etree.ElementTree as ET


def generate_xmp(raw_path: str, settings: Dict[str, Any]) -> Optional[str]:
    """
    Genera un archivo .xmp compatible con Lightroom si no existe ya.

    Args:
        raw_path: Ruta al archivo RAW original.
        settings: Ajustes generados por decision_engine.

    Returns:
        Ruta del XMP generado si fue creado.
        None si el archivo ya existía.
    """
    raw_file = Path(raw_path)
    xmp_path = raw_file.with_suffix(".xmp")

    if xmp_path.exists():
        return None

    xmp_root = _build_xmp_tree(settings)
    tree = ET.ElementTree(xmp_root)
    tree.write(xmp_path, encoding="utf-8", xml_declaration=True)

    return str(xmp_path)


def _build_xmp_tree(settings: Dict[str, Any]) -> ET.Element:
    """
    Construye el árbol XML base del archivo XMP.
    """
    ET.register_namespace("x", "adobe:ns:meta/")
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace("crs", "http://ns.adobe.com/camera-raw-settings/1.0/")

    xmpmeta = ET.Element("{adobe:ns:meta/}xmpmeta")
    rdf = ET.SubElement(
        xmpmeta,
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
    )

    description = ET.SubElement(
        rdf,
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description",
        attrib={
            "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about": "",
            "{http://ns.adobe.com/camera-raw-settings/1.0/}Version": "15.0",
            "{http://ns.adobe.com/camera-raw-settings/1.0/}ProcessVersion": "11.0",
            "{http://ns.adobe.com/camera-raw-settings/1.0/}HasSettings": "True",
            "{http://ns.adobe.com/camera-raw-settings/1.0/}WhiteBalance": "Custom",
        }
    )

    # Settings base del motor
    for key, value in settings.items():
        description.set(
            f"{{http://ns.adobe.com/camera-raw-settings/1.0/}}{key}",
            _format_xmp_value(value)
        )

    return xmpmeta


def _format_xmp_value(value: Any) -> str:
    """
    Convierte valores Python a string compatible con atributos XMP.
    """
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)