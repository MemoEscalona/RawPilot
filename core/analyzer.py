import cv2
import numpy as np
from typing import Dict, Any

def analyze_image(image: np.ndarray) -> Dict[str, Any]:
    """
    Analiza una imagen RGB de trabajo y devuelve métricas visuales
    útiles para la toma de decisiones de edición.

    + interpretación tonal/fotográfica inicial.
    
    Args:
        image: Imagen RGB optimizada para análisis (numpy array)
    
    Returns:
        Diccionario con métricas visuales.
    """
    #metricas consolidades
    brightness = _analyze_brightness(image)
    contrast = _analyze_contrast(image)
    color_bias= _analyze_color_bias(image)
    saturation = _analyze_saturation(image)
    tonal_distribution = _analyze_highlights_shadows(image)

    metrics = {
        **brightness,
        **contrast,
        **color_bias,
        **saturation,
        **tonal_distribution
    }

    #clasificacion fotográfica
    tonal_profile= _clasify_tonal_profile(metrics)
    contrast_profile= _clasify_contrast_profile(metrics)
    scene_feel= _clasify_scene_feel(metrics, tonal_profile, contrast_profile)

    return {
        **metrics,
        "tonal_profile": tonal_profile,
        "contrast_profile": contrast_profile,
        "scene_feel": scene_feel
    }


def _analyze_brightness(image: np.ndarray) -> Dict[str, Any]:
    """
    Calcula el brillo promedio y exposición general aproximada.
    """
    gray= cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mean_brightness = float(np.mean(gray))

    if mean_brightness < 70:
        exposure = "underexposed"
    elif mean_brightness > 180:
        exposure = "overexposed"
    else:
        exposure = "balanced"

    return {
        "brightness_mean": mean_brightness,
        "exposure_label": exposure
    }

def _analyze_contrast(image: np.ndarray) -> Dict[str, Any]:
    """
    Calcula el contraste usando la desviación estándar de los valores de píxeles.
    """
    gray= cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    contrast_std = float(np.std(gray))

    if contrast_std < 35:
        contrast_label = "low"
    elif contrast_std > 80:
        contrast_label = "high"
    else:
        contrast_label = "medium"
    return {
        "contrast_std": contrast_std,
        "contrast_label": contrast_label
    }

def _analyze_color_bias(image: np.ndarray) -> Dict[str, Any]:
    """
    Detecta la tendencia de temperatura Cálida/fria basada en promedios RGB.
    """
    # Calcular promedios por canal
    mean_r = float(np.mean(image[:, :, 0]))
    mean_g = float(np.mean(image[:, :, 1]))
    mean_b = float(np.mean(image[:, :, 2]))

    rb_diff= mean_r - mean_b
    # Evaluar tendencia de temperatura
    if rb_diff > 12:
        temperature = "warm"
    elif rb_diff < -12:
        temperature = "cool"
    else:
        temperature = "neutral"

    return {
        "mean_r": round(mean_r, 2),
        "mean_g": round(mean_g, 2),
        "mean_b": round(mean_b, 2),
        "temperature": temperature,
        "rb_diff": round(rb_diff, 2)
    }

def _analyze_saturation(image: np.ndarray) -> Dict[str, Any]:
    """
    Calcula la saturación promedio en espacio HSV.
    
    H: Hue (tono) - es el color en si (rojo, verde, azul, etc.). Se mide en grados 
       en un círculo cromático (0-360°), 
       donde 0° es rojo, 120° es verde y 240° es azul.
    S: Saturation (saturación) - es la pureza o intensidad del color. 
       Se mide en porcentaje (0-100%), 
       donde 0% es completamente desaturado (gris) y 100% es el color más puro.

    V: Value (valor o brillo) - es la luminosidad del color. 
       Un valor bajo es oscuro y uno alto es brillante. 
    """
    hsv=cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    saturation_channel= hsv[:, :, 1]
    saturation_mean= float(np.mean(saturation_channel))

    if saturation_mean < 50:
        saturation_label = "low"
    elif saturation_mean > 140:
        saturation_label = "high"
    else:
        saturation_label = "medium"

    return {
        "saturation_mean": saturation_mean,
        "saturation_label": saturation_label
    }

def _analyze_highlights_shadows(image: np.ndarray) -> Dict[str, Any]:
    """
    Estima proporción de sombras profundas y altas luces.    
    """
    gray= cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    total_pixels = gray.size

    shadow_pixels = np.sum(gray < 25)
    highlight_pixels = np.sum(gray > 245)

    shadow_ratio= float(shadow_pixels/total_pixels)
    highlight_ratio= float(highlight_pixels/total_pixels)

    return{
        "shadow_ratio": round(shadow_ratio, 4),
        "highlight_ratio": round(highlight_ratio, 4)
    }

def _clasify_tonal_profile(metrics: Dict[str, Any]) -> str:
    """
    Clasifica la imagen como clave alta, clave baja o equilibrada
    """
    brightness=metrics["brightness_mean"]
    shadows=metrics["shadow_ratio"]
    highlights=metrics["highlight_ratio"]

    if brightness > 155 and highlights > 0.08:
        tonal_profile = "high_key"
    elif brightness < 95 and shadows > 0.18 and highlights < 0.05:
        tonal_profile = "low_key"
    else:
        tonal_profile = "balanced"

    return tonal_profile

def _clasify_contrast_profile(metrics: Dict[str, Any]) -> str:
    """
    Clasifica el carácter del contraste
    """
    contrast_std = metrics["contrast_std"]

    if contrast_std < 35:
        contrast_profile = "flat"
    elif contrast_std > 80:
        contrast_profile = "high_contrast"
    else:
        contrast_profile = "normal_contrast"

    return contrast_profile

def _clasify_scene_feel(
        metrics: Dict[str,Any],
        tonal_profile: str,
        contrast_profile: str) -> str:
    """
    Da una lectura fotográfica general de la imagen
    """
    if tonal_profile == "high_key" and contrast_profile != "high_contrast":
        scene_feel="airy"
    elif tonal_profile == "low_key" or contrast_profile == "high_contrast":
        scene_feel="dramatic"
    else:
        scene_feel="neutral"
    return scene_feel
