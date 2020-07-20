#!/usr/bin/env python

import numpy as np

from chimera import Chimera

# ==============================================================================


def test_chimera_absolutes():
    chim = Chimera(absolutes=np.zeros(2))
    assert len(chim.absolutes) == 2
    assert np.sum(chim.absolutes) == 0
    assert len(chim.relatives) == 2
    assert np.isnan(chim.relatives[0])


def test_chimera_relatives():
    chim = Chimera(relatives=np.zeros(2))
    assert len(chim.absolutes) == 2
    assert np.isnan(chim.absolutes[0])
    assert len(chim.relatives) == 2
    assert np.sum(chim.relatives) == 0


def test_chimera_scalarize():
    chim = Chimera(relatives=np.zeros(2) + 0.1)
    np.random.seed(100691)
    merits = chim.scalarize(np.random.uniform(low=0, high=1, size=(3, 2)))
    assert len(merits) == 3
    assert np.abs(merits[0] - 1.00000) < 1e-4
    assert np.abs(merits[1] - 0.76011) < 1e-4
    assert np.abs(merits[2] - 0.00000) < 1e-4


# ==============================================================================

if __name__ == "__main__":
    test_chimera_scalarize()
