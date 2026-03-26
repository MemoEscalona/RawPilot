from typing import Dict, Any, List


def build_edit_decisions(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traduce el análisis visual de la imagen en ajustes base de revelado.

    Returns:
        {
            "settings": {...},
            "decision_notes": [...],
            "decision_log": [...]
        }
    """
    notes: List[str] = []
    decision_log: List[Dict[str, Any]] = []

    settings = {
        "Exposure2012": 0.0,
        "Contrast2012": 0,
        "Highlights2012": 0,
        "Shadows2012": 0,
        "Whites2012": 0,
        "Blacks2012": 0,
        "Temp": 5500,
        "Tint": 0,
        "Vibrance": 0,
        "Saturation": 0,
    }

    _decide_exposure_and_tones(settings, analysis, notes, decision_log)
    _decide_contrast(settings, analysis, notes, decision_log)
    _decide_color(settings, analysis, notes, decision_log)
    _decide_saturation(settings, analysis, notes, decision_log)

    return {
        "settings": settings,
        "decision_notes": notes,
        "decision_log": decision_log,
    }


def _decide_exposure_and_tones(
    settings: Dict[str, Any],
    analysis: Dict[str, Any],
    notes: List[str],
    decision_log: List[Dict[str, Any]]
) -> None:
    brightness = analysis.get("brightness_mean", 128)
    tonal_profile = analysis.get("tonal_profile", "balanced")
    shadow_ratio = analysis.get("shadow_ratio", 0.0)
    highlight_ratio = analysis.get("highlight_ratio", 0.0)

    # Exposure
    if tonal_profile == "low_key":
        _apply_adjustment(
            settings, decision_log,
            parameter="Exposure2012",
            delta=0.15,
            reason="Preservar atmósfera low key con ajuste leve de exposición.",
            source_metric={
                "tonal_profile": tonal_profile,
                "brightness_mean": brightness
            }
        )
        notes.append("Imagen low_key detectada; se preserva atmósfera con ajuste leve de exposición.")

    elif tonal_profile == "high_key":
        _apply_adjustment(
            settings, decision_log,
            parameter="Exposure2012",
            delta=-0.10,
            reason="Evitar sobreexposición adicional en imagen high key.",
            source_metric={
                "tonal_profile": tonal_profile,
                "brightness_mean": brightness
            }
        )
        notes.append("Imagen high_key detectada; se evita sobreexposición adicional.")

    else:
        if brightness < 85:
            _apply_adjustment(
                settings, decision_log,
                parameter="Exposure2012",
                delta=0.35,
                reason="Brillo promedio bajo; se incrementa exposición.",
                source_metric={"brightness_mean": brightness}
            )
            notes.append("Brillo bajo detectado; se incrementa exposición.")

        elif brightness > 175:
            _apply_adjustment(
                settings, decision_log,
                parameter="Exposure2012",
                delta=-0.30,
                reason="Brillo promedio alto; se reduce exposición.",
                source_metric={"brightness_mean": brightness}
            )
            notes.append("Brillo alto detectado; se reduce exposición.")

        else:
            notes.append("Exposición general considerada balanceada; no se realizan cambios agresivos.")

    # Highlights
    if highlight_ratio > 0.03:
        _apply_adjustment(
            settings, decision_log,
            parameter="Highlights2012",
            delta=-35,
            reason="Recuperar altas luces por presencia significativa de highlights.",
            source_metric={"highlight_ratio": highlight_ratio}
        )
        notes.append("Altas luces presentes; se recuperan highlights.")

    elif highlight_ratio > 0.01:
        _apply_adjustment(
            settings, decision_log,
            parameter="Highlights2012",
            delta=-18,
            reason="Reducir ligeramente altas luces por presencia moderada.",
            source_metric={"highlight_ratio": highlight_ratio}
        )

    # Shadows
    if shadow_ratio > 0.20:
        _apply_adjustment(
            settings, decision_log,
            parameter="Shadows2012",
            delta=28,
            reason="Abrir sombras por alta proporción de zonas oscuras profundas.",
            source_metric={"shadow_ratio": shadow_ratio}
        )
        notes.append("Sombras profundas elevadas; se abren shadows.")

    elif shadow_ratio > 0.10:
        _apply_adjustment(
            settings, decision_log,
            parameter="Shadows2012",
            delta=15,
            reason="Abrir ligeramente sombras por presencia moderada.",
            source_metric={"shadow_ratio": shadow_ratio}
        )

    # Whites / Blacks
    if tonal_profile == "high_key":
        _apply_adjustment(
            settings, decision_log,
            parameter="Whites2012",
            delta=10,
            reason="Refuerzo de blancos para sostener look high key.",
            source_metric={"tonal_profile": tonal_profile}
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Blacks2012",
            delta=-5,
            reason="Anclar negros ligeramente para conservar estructura tonal.",
            source_metric={"tonal_profile": tonal_profile}
        )

    elif tonal_profile == "low_key":
        _apply_adjustment(
            settings, decision_log,
            parameter="Whites2012",
            delta=4,
            reason="Levantar blancos sutilmente sin romper look low key.",
            source_metric={"tonal_profile": tonal_profile}
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Blacks2012",
            delta=-12,
            reason="Profundizar negros para sostener dramatismo low key.",
            source_metric={"tonal_profile": tonal_profile}
        )

    else:
        _apply_adjustment(
            settings, decision_log,
            parameter="Whites2012",
            delta=6,
            reason="Ajuste base de blancos para imagen balanceada.",
            source_metric={"tonal_profile": tonal_profile}
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Blacks2012",
            delta=-6,
            reason="Ajuste base de negros para imagen balanceada.",
            source_metric={"tonal_profile": tonal_profile}
        )


def _decide_contrast(
    settings: Dict[str, Any],
    analysis: Dict[str, Any],
    notes: List[str],
    decision_log: List[Dict[str, Any]]
) -> None:
    contrast_profile = analysis.get("contrast_profile", "normal_contrast")
    contrast_std = analysis.get("contrast_std", None)

    if contrast_profile == "flat":
        _apply_adjustment(
            settings, decision_log,
            parameter="Contrast2012",
            delta=18,
            reason="Incrementar contraste por imagen plana.",
            source_metric={
                "contrast_profile": contrast_profile,
                "contrast_std": contrast_std
            }
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Blacks2012",
            delta=-6,
            reason="Refuerzo adicional de negros para dar profundidad a imagen plana.",
            source_metric={
                "contrast_profile": contrast_profile,
                "contrast_std": contrast_std
            }
        )
        notes.append("Imagen plana detectada; se incrementa contraste.")

    elif contrast_profile == "high_contrast":
        _apply_adjustment(
            settings, decision_log,
            parameter="Contrast2012",
            delta=-8,
            reason="Moderar contraste global por imagen ya contrastada.",
            source_metric={
                "contrast_profile": contrast_profile,
                "contrast_std": contrast_std
            }
        )
        notes.append("Contraste alto detectado; se modera contraste global.")

    else:
        _apply_adjustment(
            settings, decision_log,
            parameter="Contrast2012",
            delta=5,
            reason="Pequeño refuerzo de contraste para imagen de contraste medio.",
            source_metric={
                "contrast_profile": contrast_profile,
                "contrast_std": contrast_std
            }
        )
        notes.append("Contraste medio detectado; se aplica refuerzo moderado.")


def _decide_color(
    settings: Dict[str, Any],
    analysis: Dict[str, Any],
    notes: List[str],
    decision_log: List[Dict[str, Any]]
) -> None:
    color_bias = analysis.get("color_bias", "neutral")
    rb_diff = analysis.get("rb_diff", 0)
    base_temp = 5500

    if color_bias == "warm":
        if rb_diff > 20:
            _set_absolute_value(
                settings, decision_log,
                parameter="Temp",
                new_value=base_temp - 400,
                reason="Enfriar balance de blancos por dominante cálida fuerte.",
                source_metric={"color_bias": color_bias, "rb_diff": rb_diff}
            )
            notes.append("Dominante cálida fuerte detectada; se enfría balance de blancos.")
        else:
            _set_absolute_value(
                settings, decision_log,
                parameter="Temp",
                new_value=base_temp - 200,
                reason="Enfriar ligeramente temperatura por dominante cálida.",
                source_metric={"color_bias": color_bias, "rb_diff": rb_diff}
            )
            notes.append("Dominante cálida detectada; se enfría ligeramente temperatura.")

    elif color_bias == "cool":
        if rb_diff < -20:
            _set_absolute_value(
                settings, decision_log,
                parameter="Temp",
                new_value=base_temp + 400,
                reason="Calentar balance de blancos por dominante fría fuerte.",
                source_metric={"color_bias": color_bias, "rb_diff": rb_diff}
            )
            notes.append("Dominante fría fuerte detectada; se calienta balance de blancos.")
        else:
            _set_absolute_value(
                settings, decision_log,
                parameter="Temp",
                new_value=base_temp + 200,
                reason="Calentar ligeramente temperatura por dominante fría.",
                source_metric={"color_bias": color_bias, "rb_diff": rb_diff}
            )
            notes.append("Dominante fría detectada; se calienta ligeramente temperatura.")

    else:
        notes.append("Balance de color considerado neutral.")


def _decide_saturation(
    settings: Dict[str, Any],
    analysis: Dict[str, Any],
    notes: List[str],
    decision_log: List[Dict[str, Any]]
) -> None:
    saturation_label = analysis.get("saturation_label", "medium")
    saturation_mean = analysis.get("saturation_mean", None)

    if saturation_label == "low":
        _apply_adjustment(
            settings, decision_log,
            parameter="Vibrance",
            delta=18,
            reason="Incrementar vibrance por saturación general baja.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Saturation",
            delta=4,
            reason="Refuerzo leve de saturación para imagen apagada.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        notes.append("Saturación baja detectada; se refuerza color.")

    elif saturation_label == "high":
        _apply_adjustment(
            settings, decision_log,
            parameter="Vibrance",
            delta=-6,
            reason="Reducir vibrance por saturación alta.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Saturation",
            delta=-4,
            reason="Reducir saturación global por imagen ya intensa.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        notes.append("Saturación alta detectada; se modera intensidad de color.")

    else:
        _apply_adjustment(
            settings, decision_log,
            parameter="Vibrance",
            delta=8,
            reason="Refuerzo suave de vibrance para imagen de saturación media.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        _apply_adjustment(
            settings, decision_log,
            parameter="Saturation",
            delta=1,
            reason="Pequeño ajuste de saturación para imagen equilibrada.",
            source_metric={
                "saturation_label": saturation_label,
                "saturation_mean": saturation_mean
            }
        )
        notes.append("Saturación media detectada; se aplica refuerzo suave.")


def _apply_adjustment(
    settings: Dict[str, Any],
    decision_log: List[Dict[str, Any]],
    parameter: str,
    delta: float,
    reason: str,
    source_metric: Dict[str, Any]
) -> None:
    """
    Aplica un cambio incremental a un parámetro y lo registra.
    """
    previous = settings.get(parameter, 0)
    new_value = previous + delta
    settings[parameter] = new_value

    decision_log.append({
        "parameter": parameter,
        "operation": "delta",
        "previous": previous,
        "new": new_value,
        "delta": delta,
        "reason": reason,
        "source_metric": source_metric,
    })


def _set_absolute_value(
    settings: Dict[str, Any],
    decision_log: List[Dict[str, Any]],
    parameter: str,
    new_value: float,
    reason: str,
    source_metric: Dict[str, Any]
) -> None:
    """
    Asigna un valor absoluto a un parámetro y lo registra.
    """
    previous = settings.get(parameter, None)
    settings[parameter] = new_value

    decision_log.append({
        "parameter": parameter,
        "operation": "absolute",
        "previous": previous,
        "new": new_value,
        "delta": None,
        "reason": reason,
        "source_metric": source_metric,
    })