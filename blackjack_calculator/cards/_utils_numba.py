from functools import partial

import numpy as np
from numba import njit


@njit
def fill_hard_geq_eleven(
    lbound: int,
    p_arr: np.ndarray,
    hard_cache: np.ndarray,
) -> None:
    """fills array in place, equivalent to fill soft"""
    _p_idx = np.arange(11)
    for i in range(16, lbound - 1, -1):
        if hard_cache[:, i].any():
            break
        hard_cache[:, i] = (p_arr * hard_cache[:, _p_idx + i]).sum(axis=1)


@njit
def fill_hard_le_eleven(
    lbound: int,
    p_arr: np.ndarray,
    hard_cache: np.ndarray,
    soft_cache: np.ndarray,
) -> None:
    """fills array in place"""
    ace_p = p_arr[1]
    p_arr[1] = 0
    _p_idx = np.arange(11)
    for i in range(11, lbound - 1, -1):
        if hard_cache[:, i].any():
            break
        hard_cache[:, i] = (p_arr * hard_cache[:, _p_idx + i]).sum(
            axis=1
        ) + ace_p * soft_cache[:, i + 11]


@njit
def _fill_exact(
    lbound: int,
    ubound: int,
    p_arr: np.ndarray,
    hard_cache: np.ndarray,
    hard_cache_ace: np.ndarray,
    hard_cache_two: np.ndarray,
    hard_cache_three: np.ndarray,
    hard_cache_four: np.ndarray,
    hard_cache_five: np.ndarray,
    hard_cache_six: np.ndarray,
    hard_cache_seven: np.ndarray,
    hard_cache_eight: np.ndarray,
    hard_cache_nine: np.ndarray,
    hard_cache_ten: np.ndarray,
):
    _p_idx = np.arange(11)
    for i in range(ubound, lbound - 1, -1):
        if hard_cache[:, i].any():
            break
        hard_cache[:, i] = (
            p_arr[1] * hard_cache_ace[:, i + 1]
            + p_arr[2] * hard_cache_two[:, i + 2]
            + p_arr[3] * hard_cache_three[:, i + 3]
            + p_arr[4] * hard_cache_four[:, i + 4]
            + p_arr[5] * hard_cache_five[:, i + 5]
            + p_arr[6] * hard_cache_six[:, i + 6]
            + p_arr[7] * hard_cache_seven[:, i + 7]
            + p_arr[8] * hard_cache_eight[:, i + 8]
            + p_arr[9] * hard_cache_nine[:, i + 9]
            + p_arr[10] * hard_cache_ten[:, i + 10]
        )


fill_exact_geq_eleven = partial(_fill_exact, ubound=16)
fill_exact_le_eleven = partial(_fill_exact, ubound=11)
