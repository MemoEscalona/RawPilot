from typing import Dict, Any

def print_photo_summary(exif_metadata: Dict[str, Any]) -> None:
    """
    Imprime resumen general de la foto.
    """
    print("=== DATOS GENERALES DE LA FOTO ===")
    print(f"Cámara: {exif_metadata.get('camera_model', 'N/A')}")
    print(f"Lente: {exif_metadata.get('lens_model', 'N/A')}")
    print(f"ISO: {exif_metadata.get('iso', 'N/A')}")
    print(f"Shutter Speed: {exif_metadata.get('shutter_speed', 'N/A')}")
    print(f"Aperture: {exif_metadata.get('aperture', 'N/A')}")
    print(f"Focal Length: {exif_metadata.get('focal_length', 'N/A')}")
    print(f"Datetime Original: {exif_metadata.get('datetime_original', 'N/A')}")
    print(f"White Balance Mode: {exif_metadata.get('white_balance_mode', 'N/A')}")
    print(f"Flash: {exif_metadata.get('flash', 'N/A')}")
    print()

def print_analysis_summary(analysis: Dict[str, Any]) -> None:
    print("=== ANÁLISIS FOTOGRÁFICO ===")
    print(f"Perfil tonal: {_translate_tonal_profile(analysis.get('tonal_profile'))}")
    print(f"Contraste: {_translate_contrast_profile(analysis.get('contrast_profile'))}")
    print(f"Lectura general: {_translate_scene_feel(analysis.get('scene_feel'))}")
    print(f"Exposición estimada: {_translate_exposure_label(analysis.get('exposure_label'))}")
    print(f"Dominante de color: {_translate_color_bias(analysis.get('temperature'))}")
    print(f"Saturación: {_translate_saturation_label(analysis.get('saturation_label'))}")
    print()

    print("=== MÉTRICAS TÉCNICAS ===")
    print(f"Brillo promedio: {analysis.get('brightness_mean')}")
    print(f"Contraste (std): {analysis.get('contrast_std')}")
    print(f"Sombras profundas: {analysis.get('shadow_ratio')}")
    print(f"Altas luces: {analysis.get('highlight_ratio')}")
    print(f"Promedio R: {analysis.get('mean_r')}")
    print(f"Promedio G: {analysis.get('mean_g')}")
    print(f"Promedio B: {analysis.get('mean_b')}")
    print(f"RB Diff: {analysis.get('rb_diff')}")
    print(f"Saturación promedio: {analysis.get('saturation_mean')}")
    print()

def print_decision_log(decisions: Dict[str, Any]) -> None:
    """
    Imprime el detalle técnico de cada ajuste aplicado.
    """
    print("=== LOG DETALLADO DE DECISIONES ===")

    for item in decisions.get("decision_log", []):
        print(f"\nParámetro: {item['parameter']}")
        print(f"  Operación: {item['operation']}")
        print(f"  Valor anterior: {item['previous']}")
        print(f"  Valor nuevo: {item['new']}")
        print(f"  Delta: {item['delta']}")
        print(f"  Razón: {item['reason']}")
        print(f"  Métrica origen: {item['source_metric']}")

    print()

def print_decision_summary(decisions: Dict[str, Any]) -> None:
    """
    Imprime un resumen legible de las decisiones de edición tomadas por el motor.
    """
    settings = decisions.get("settings", {})
    notes = decisions.get("decision_notes", [])

    print("=== DECISIONES DE EDICIÓN ===")
    _print_setting(settings, "Exposure2012", "Exposure")
    _print_setting(settings, "Contrast2012", "Contrast")
    _print_setting(settings, "Highlights2012", "Highlights")
    _print_setting(settings, "Shadows2012", "Shadows")
    _print_setting(settings, "Whites2012", "Whites")
    _print_setting(settings, "Blacks2012", "Blacks")
    _print_setting(settings, "Temp", "Temperature")
    _print_setting(settings, "Tint", "Tint")
    _print_setting(settings, "Vibrance", "Vibrance")
    _print_setting(settings, "Saturation", "Saturation")
    print()

    print("=== JUSTIFICACIÓN GENERAL ===")
    for note in notes:
        print(f"- {note}")
    print()


def _print_setting(settings: Dict[str, Any], key: str, label: str) -> None:
    """
    Imprime un parámetro si existe dentro del diccionario de settings.
    """
    value = settings.get(key, None)
    if value is not None:
        print(f"{label}: {value}")

def _translate_tonal_profile(value: str) -> str:
    mapping = {
        "high_key": "Clave Alta",
        "low_key": "Clave Baja",
        "balanced": "Balanceada",
    }
    return mapping.get(value, "Desconocido")

def _translate_contrast_profile(value: str) -> str:
    mapping = {
        "flat": "Plano / Suave",
        "normal_contrast": "Normal",
        "high_contrast": "Alto",
    }
    return mapping.get(value, "Desconocido")

def _translate_scene_feel(value: str) -> str:
    mapping = {
        "airy": "Ligera / Aireada",
        "dramatic": "Dramática",
        "neutral": "Neutral",
    }
    return mapping.get(value, "Desconocido")


def _translate_exposure_label(value: str) -> str:
    mapping = {
        "underexposed": "Subexpuesta",
        "balanced": "Balanceada",
        "overexposed": "Sobreexpuesta",
    }
    return mapping.get(value, "Desconocido")


def _translate_color_bias(value: str) -> str:
    mapping = {
        "warm": "Cálida",
        "cool": "Fría",
        "neutral": "Neutral",
    }
    return mapping.get(value, "Desconocido")


def _translate_saturation_label(value: str) -> str:
    mapping = {
        "low": "Baja",
        "medium": "Media",
        "high": "Alta",
    }
    return mapping.get(value, "Desconocido")