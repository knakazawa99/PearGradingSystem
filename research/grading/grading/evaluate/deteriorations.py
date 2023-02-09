from dataclasses import dataclass
from enum import Enum


class Deterioration(Enum):
    ALTERNALIA = 'an'
    CHEMICAL = 'ch'
    INJURY = 'in'
    PLANE = 'pl'
    SPECKLE = 'sp'


class DeteriorationGroup(Enum):
    AN = ['an']
    CH_PL = ['ch', 'pl']
    SP_IN = ['sp', 'in']

class DeteriorationAreaRate(Enum):
    ALTERNALIA = 0.452
    CHEMICAL = 0.539
    INJURY = 0.357
    PLANE = 0.351
    SPECKLE = 0.439

@dataclass
class DeteriorationBySingleBBox:
    pixels: int
