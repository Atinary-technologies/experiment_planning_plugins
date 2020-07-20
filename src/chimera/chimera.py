#!/usr/bin/env python

# ==============================================================================

import numpy as np

# ==============================================================================


class Chimera:
    def __init__(self, relatives=None, absolutes=None, softness=1e-3):
        self.softness = softness
        self.stiffness = np.inf if softness == 0 else 1 / softness
        self.absolutes = (
            absolutes if absolutes is not None else np.zeros(len(relatives)) * np.nan
        )
        self.relatives = (
            relatives if relatives is not None else np.zeros(len(absolutes)) * np.nan
        )

    def _step(self, value):
        return np.exp(-np.logaddexp(0, -self.stiffness * value))

    def _rescale(self, objs):
        """ rescales objectives and absolute thresholds such that all observed
            objectives are projected onto [0, 1]
        """
        objectives = np.empty(objs.shape)
        absolutes = np.empty(self.absolutes.shape)
        for idx in range(objs.shape[1]):
            min_obj, max_obj = np.amin(objs[:, idx]), np.amax(objs[:, idx])
            if min_obj < max_obj:
                objectives[:, idx] = (objs[:, idx] - min_obj) / (max_obj - min_obj)
                absolutes[idx] = (self.absolutes[idx] - min_obj) / (max_obj - min_obj)
            else:
                objectives[:, idx] = objs[:, idx] - min_obj
                absolutes[idx] = self.absolutes[idx] - min_obj
        return objectives, absolutes

    def _shift(self, objectives, absolutes):
        """ shift rescaled objectives based on identified region of interest
        """
        objs_trans = objectives.transpose()
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
                threshold = absolutes[idx]
            else:
                threshold = minimum + self.relatives[idx] * (maximum - minimum)
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

    def _scalarize(self, objs_shift, thresholds):
        merits = objs_shift[-1].copy()
        for idx in range(0, objs_shift.shape[0] - 1)[::-1]:
            step = self._step(-objs_shift[idx] + thresholds[idx])
            merits *= step
            merits += (1 - step) * objs_shift[idx]
        return merits.transpose()

    def scalarize(self, objs):
        objectives, absolutes = self._rescale(objs)
        objs_shift, thresholds = self._shift(objectives, absolutes)
        merits = self._scalarize(objs_shift, thresholds)
        max_merits = np.amax(merits)
        if max_merits > 0.0:
            min_merits = np.amin(merits)
            merits = (merits - min_merits) / (max_merits - min_merits)
        return merits


# ==============================================================================
