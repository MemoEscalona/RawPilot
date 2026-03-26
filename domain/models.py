from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class LoadedImage:
    file_path: str
    rgb_image: np.ndarray
    working_image:np.ndarray
    width: int
    height: int

    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    iso: Optional[int] = None
    shutter_speed: Optional[str] = None
    aperture: Optional[float] = None
    focal_length: Optional[str] = None
    datetime_original: Optional[str] = None

    color_description: Optional[str] = None
    black_level_per_channel: Optional[list] = None
    white_level: Optional[int] = None
    raw_pattern: Optional[list] = None

    metadata: Dict[str, Any] = field(default_factory=dict)