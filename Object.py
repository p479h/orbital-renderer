from Imports import *
from matutils import Matrix

Translation = Matrix.Translation
Rotation = Matrix.Rotation
Scale = Matrix.Scale

class Object:
    """ Class for storing geometric and transformational data of objects """

    def __init__(self, name: str = "Obj", location: Vector = [0, 0, 0]) -> None:
        self.name = gen_name(name)
        self.matrix_local = self.build_matrix_local(location)

    def build_matrix_local(self, location: Vector, rotation_angle: float = 0,
                     rotation_axis: Vector = [1, 0, 0], scale: float = 1) -> Matrix:
        T = Translation(location)
        R = Rotation(rotation_angle, 4, rotation_axis)
        S = Scale(scale, 4)
        return T@R@S

    @property
    def location(self) -> Vector:
        return self.matrix_local[:3, -1]

    @location.setter
    def location(self, p: Vector) -> Vector:
        self.matrix_local[:3, -1] = p[:]

    @property
    def scale(self) -> float:
        return np.linalg.norm(self.matrix_local, axis = 0)[0]

    @scale.setter
    def scale(self, s: float) -> None:
        self.matrx_local = self.matrx_local/ \
                    self.scale*np.array([s]*3+[1], dtype = float)

    def rotate(self, angle: float, axis: Union[Vector, str]) -> None:
        R = Rotation(angle, 4, axis)
        self.matrix_local = R@self.matrix_local

    def __repr__(self) -> "str":
        properties = "\n".join([f"{p}: {getattr(self, p)}" \
                        for p in "name location scale".split()])
        return "{\n" + properties + "\n}\n"

    def __add__(self, v: Vector) -> Vector:
        return self.location + v

    def __iadd__(self, v: Vector) -> Vector:
        self.location = self.location + v
        return self

    def __mul__(self, factor: float) -> Matrix:
        return np.diag([factor]*3+[1])@self.matrix_local

    def __imul__(self, factor: float) -> "Object":
        self.matrix_local = self*factor
        return self

    def __matmul__(self, mat: Matrix) -> Matrix:
        return np.array(mat)@self.matrix_local

    def __imatmul__(self, mat: Matrix) -> "Object":
        self.matrix_local = self@mat
        return self


if __name__ == "__main__":
    a = Object(location = [0, 0, 0])
    a.rotate(np.pi/2, [1, 1, 0])
    print(a.matrix_local)
    print(a)
