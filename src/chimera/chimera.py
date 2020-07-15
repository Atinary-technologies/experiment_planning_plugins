#!/usr/bin/env python 

#==============================================================================

from mind.base import Base
from mind.utils import get_args

#==============================================================================

class Chimera(Base):

    def __init__(self, relatives=None, absolutes=None, softness=1e-3):
        stiffness = np.inf if softness == 0 else 1 / softness 
        super().__init__(**get_args(**locals()))

    @staticmethod
    def _step(value):
        return np.exp( - np.logaddexp(0, - self.stiffness * value))


