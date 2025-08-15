from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class Color:
    r: float
    g: float
    b: float

    def to_list(self) -> List[float]:
        return [self.r, self.g, self.b]


@dataclass
class Stroke:
    color: Color
    width: int


@dataclass
class Shadow:
    enabled: bool
    color: Color
    distance: int
    softness: int
    opacity: int
    direction: int


@dataclass
class Plate:
    enabled: bool
    shape: str  # "rounded-rect" | "rect"
    size: Dict[str, int]
    radius: int
    color: Color
    opacity: int
    stroke_width: int
    stroke_color: Color


@dataclass
class Comp:
    width: int
    height: int
    fps: int
    duration: int


@dataclass
class TelopStyle:
    text: Optional[str]
    font_name: str
    font_size: int
    tracking: int
    position: Dict[str, int]
    fill: Dict[str, Any]
    strokes: List[Dict[str, Any]]
    shadow: Dict[str, Any]
    plate: Dict[str, Any]
    comp: Comp
    template_name: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(data: str) -> "TelopStyle":
        obj = json.loads(data)
        return TelopStyle(**obj)
