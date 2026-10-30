"""Strict log-space metric used by the independent House Prices evaluator."""
import numpy as np


def positive_vector(values):
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or not array.size or not np.isfinite(array).all() or not (array > 0).all():
        raise ValueError('Expected a nonempty one-dimensional vector of finite positive values')
    return array


def log_rmse(observed, predicted):
    observed, predicted = positive_vector(observed), positive_vector(predicted)
    if observed.shape != predicted.shape:
        raise ValueError('Observed and predicted shapes differ')
    return float(np.sqrt(np.mean((np.log(observed) - np.log(predicted)) ** 2)))


def constant_log_prediction(development_labels):
    return float(np.exp(np.mean(np.log(positive_vector(development_labels)))))
