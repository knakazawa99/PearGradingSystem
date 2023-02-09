from dataclasses import dataclass
from enum import Enum


class DeteriorationCategory(Enum):
    ALTERNALIA = 'an'
    CHEMICAL = 'ch'
    INJURY = 'in'
    PLANE = 'pl'
    SPECKLE = 'sp'

@dataclass
class Deterioration:
    category: DeteriorationCategory
    bbox_area: float
    bbox_count: int

@dataclass
class DeteriorationInPear:
    alternaria: Deterioration
    chemical: Deterioration
    injury: Deterioration
    plane: Deterioration
    speckle: Deterioration


class DeteriorationAreaRate(Enum):
    ALTERNALIA = 0.452
    CHEMICAL = 0.539
    INJURY = 0.357
    PLANE = 0.351
    SPECKLE = 0.439
    
class DeteriorationGroup(Enum):
    AN = ['an']
    CH_PL = ['ch', 'pl']
    SP_IN = ['sp', 'in']

