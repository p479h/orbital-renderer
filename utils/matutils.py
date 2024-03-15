import numpy as np
from DataTypes import *


class Matrix:
    def __init__(self, arr: np.ndarray) -> None:
        self.arr = arr

    @classmethod
    def to_nxn(cls, mat: np.ndarray, n: int) -> np.ndarray:
        I = np.eye(n)
        if mat.shape[0] == n:
            return mat
        elif mat.shape[0] < n:
            I[:mat.shape[0], :mat.shape[0]] = mat[:]
            return I
        else:
            return mat[:n, :n]

    @classmethod
    def Rotation(cls, angle: float, n: int = 3,
                 axis: Union[str, np.ndarray] = [0, 0, 1]) -> np.ndarray:
        if type(axis) == str:
            axis = {k:v for k, v in zip(list("xyz"), np.eye(3))}[axis.lower()]
        u = np.array(axis)/np.linalg.norm(axis)
        uu = np.einsum("i,j->ij", u, u)
        ux_sin = np.cross(u, np.identity(3) * -1)*np.sin(angle)
        cos = np.cos(angle)
        I = np.eye(3, dtype = float)
        R = cos*I + ux_sin + uu*(1-np.cos(angle))
        return cls.to_nxn(R, n)

    @classmethod
    def Translation(cls, d: np.ndarray) -> np.ndarray:
        I = np.eye(4)
        I[:3, -1] = d[:]
        return I

    @classmethod
    def Scale(cls, factor: float, n: int = 3) -> np.ndarray:
        return cls.to_nxn(np.eye(3)*factor, n)
