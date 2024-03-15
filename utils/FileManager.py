import sys, re, os
import numpy as np
from typing import Tuple, Iterable, Union

Number = Union[float, int]
Vector = Iterable[Number]
Matrix = Iterable[Vector]

class FileManager:
    @classmethod
    def from_file(cls, path):
        ending =  os.path.splitext(path)[-1].strip(".")
        return getattr(cls, f"read_{ending}")(path)

    @classmethod
    def read_smol(cls, path: str) -> Tuple[Vector, Matrix, Matrix]:
        atoms = []
        positions = []
        bonds = []
        with open(path, "r") as f:
            found_bonds = False
            for l in f.readlines():
                if len(l.split()) == 4:
                    found_bonds = True
                    l = l.split()
                    atoms.append(l[3])
                    positions.append([float(i) for i in l[:3]])
                elif found_bonds:
                    bonds.append([int(l[:3])-1, int(l[3:6])-1])
        return atoms, positions, bonds

    @classmethod
    def read_mol(cls, path) -> Tuple[Vector, Matrix, Matrix, Vector]:
        """ Reads mol files and outputs atoms, positions, bonds, orders

        Example:
        >>> filepath = os.path.join("..", "data", "Molecules", "benzene.mol")
        >>> atoms, positions, bonds, orders = FileManager.from_file(filepath)
        >>> positions
        [[0.1641, -1.3726, -0.0002], [-1.1066, -0.8284, 0.0001], [-1.2707, 0.5442, -0.0], [-0.1641, 1.3726, 0.0], [1.1066, 0.8284, 0.0006], [1.2707, -0.5442, -0.0007], [0.2923, -2.4449, 0.0044], [-1.9712, -1.4756, 0.0], [-2.2635, 0.9693, -0.0005], [-0.2923, 2.4449, -0.0008], [1.9712, 1.4756, -0.0001], [2.2635, -0.9693, 0.0002]]
        >>> atoms
        ['C', 'C', 'C', 'C', 'C', 'C', 'H', 'H', 'H', 'H', 'H', 'H']
        >>> bonds
        [[0, 1], [0, 5], [0, 6], [1, 2], [1, 7], [2, 3], [2, 8], [3, 4], [3, 9], [4, 5], [4, 10], [5, 11]]
        >>> orders
        [2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1]
        """
        mol_pattern = re.compile(r"[\t ]*(\-?\d+\.\d+)"*3 + r"[\t ]*([A-Z][a-z]?)")
        mol_bonds_pattern = re.compile(r"\n"+r"[\t ]*(\d+)"*3)
        with open(path, "r") as f:
            text = f.read()
        lines = mol_pattern.findall(text)
        atoms = list(map(lambda a:a[-1], lines))
        positions = list(map(lambda a: [float(i) for i in a[:-1]], lines))
        line_bonds = mol_bonds_pattern.findall(text)[1:] # First skip
        bonds = list(map(lambda a: [int(i)-1 for i in a[:-1]], line_bonds))
        orders = list(map(lambda a: int(a[-1]), line_bonds))
        return atoms, positions, bonds, orders

    @classmethod
    def read_xyz(cls, path: str) -> Tuple[Vector, Matrix]:
        """Reads xyz file and outputs names and positions of atoms

        Example:
        >>> filepath = os.path.join("..", "data", "Molecules", "benzene.xyz")
        >>> atoms, positions = FileManager.from_file(filepath)
        >>> positions
        [[0.694477, -1.195267, 0.0], [-0.687846, -1.199031, 0.0], [-1.382323, -0.003768, 0.0], [-0.694477, 1.195267, 0.0], [0.687846, 1.199031, 0.0], [1.382323, 0.003768, 0.0], [1.237016, -2.129029, 0.0], [-1.225283, -2.135813, 0.0], [-2.462302, -0.006786, 0.0], [-1.237016, 2.129029, 0.0], [1.225283, 2.135813, 0.0], [2.462302, 0.006786, 0.0]]
        >>> atoms
        ['C', 'C', 'C', 'C', 'C', 'C', 'H', 'H', 'H', 'H', 'H', 'H']
        """
        xyz_pattern = re.compile(r"([A-Z][a-z]?)"+r"[\t ]+(\-?\d+\.\d+)"*3)
        with open(path, "r") as f:
            text = f.read()
        lines = xyz_pattern.findall(text)
        atoms = list(map(lambda a:a[0], lines))
        positions = list(map(lambda a: [float(i) for i in a[1:]], lines))
        return atoms, positions

if __name__ == "__main__":
    from doctest import testmod
    testmod()
