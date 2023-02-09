
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BoundingBox:
    left: float
    top: float
    right: float
    bottom: float
    category: int

    @property
    def width(self) -> float:
        return self.right - self.left
    
    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def xywh(self) -> Tuple[float, float, float, float]:
        return (self.left, self.top, self.width, self.height)
    
    @property
    def xyxy(self) -> Tuple[float, float, float, float]:
        return (self.left, self.top, self.right, self.bottom)
    
    @property
    def area(self) -> float:
        return self.width * self.height

@dataclass
class PearSide:
    file_name: str
    bboxes: List[BoundingBox]

@dataclass
class Pear:
    pear_id: int
    shape_type_id: int
    graiding_id_deterioration: int
    pear_sides: List[PearSide]

