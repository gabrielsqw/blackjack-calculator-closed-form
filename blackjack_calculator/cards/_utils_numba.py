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
    for i in range(16, lbound - 1, -1):
        if hard_cache[:, i].any():
            break
        hard_cache[:, i] = (
                (p_arr * hard_cache[:, _p_idx + i]).sum(axis=1)
                + ace_p & soft_cache[:, i + 11]
        )
