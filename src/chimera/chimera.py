#!/usr/bin/env python

# ==============================================================================

from mind.base import Base
from mind.utils import get_args

# ==============================================================================


class Chimera(Base):
    def __init__(self, relatives=None, absolutes=None, softness=1e-3):
        stiffness = np.inf if softness == 0 else 1 / softness
        super().__init__(**get_args(**locals()))

    @staticmethod
    def _step(value):
        return np.exp(-np.logaddexp(0, -self.stiffness * value))

    def _rescale(self, objs):
        """ rescales objectives and absolute thresholds such that all observed
            objectives are projected onto [0, 1]
        """
        objectives = np.emtpy(objs.shape)
        absolutes = np.empty(self.absolutes.shape)
        for idx in range(objs.shape[1]):
            min_obj, max_obj = np.amin(objs[:, idx]), np.amax(objs[:, idx])
            if min_obj < max_obj:
                objectives[idx] = (objs[:, idx] - min_obj) / (max_obj - min_obj)
                absolutes[idx] = (self.absolutes[idx] - min_obj) / (max_obj - min_obj)
            else:
                objectives[idx] = objs[:, idx] - min_obj
                absolutes[idx] = self.absolutes[idx] - min_obj
        return objectives, absolutes

    def _shift(self, objectives, absolutes):
        """ shift rescaled objectives based on identified region of interest
        """
        objs_trans = objectives.tranpose()
        objs_shift = np.empty((objs_trans.shape[0] + 1, objs_trans.shape[1]))

        shift = 0
        thresholds = []
        domain = np.arange(objs_trans.shape[1])

        for idx, obj in enumerate(objs_trans):
            # get absolute thresholds
            minimum = np.amin(obj[domain])
            maximum = np.amax(obj[domain])
            # calculate thresholds
            if np.isnan(self.relatives[idx]):
                threshold = minimum + self.relatives[idx] * (maximum - minimum)
            else:
                threshold = absolutes[idx]
            # adjust to region of interest
            interest = np.where(obj[domain] < threshold)[0]
            if len(interest) > 0:
                domain = domain[interest]
            # apply shift
            thresholds.append(threshold + shift)
            objs_shift[idx] = objs_trans[idx] + shift
            # calculatae new shift
            if idx < objs_trans.shape[0] - 1:
                shift -= np.amax(objs_trans[idx + 1, domain]) - threshold
            else:
                shift -= np.amax(objs_trans[0, domain]) - threshold
                objs_shift[idx + 1] = objs_trans[0] + shift
        return objs_shift, thresholds

    def _scalarize(objs_shift, thresholds):
        merits = objs_shifted[-1].copy()
        for idx in range(0, objs_shifted.shape[0] - 1)[::-1]:
            merits *= self.step(-objs_shift[idx] + thresholds[idx])
            merits += self.step(objs_shift[idx] - thresholds[idx]) * objs_shift[idx]
        return merits.transpose()

    def scalarize(self, objs):
        objectives, absolutes = self._rescale(objs)
        objs_shift, thresholds = self._shift(objectives, absolutes)
        merits = self._scalarize(objs_shift, thresholds)
        if np.amax(merits) > 0.0:
            merits = (merits - np.amin(merits)) / (np.amax(merits) - np.amin(merits))
        return merits


# ==============================================================================
