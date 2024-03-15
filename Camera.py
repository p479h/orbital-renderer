from Imports import *
from Bobject import Bobject

class Camera(Bobject):
    def __init__(self,
                 name: str = "Camera" #Camera name
                 ) -> None:
        super().__init__(name)

    @property
    def image_settings(self) -> "BlenderSettings":
        return self.scene.render.image_settings

    @property
    def file_format(self) -> str:
        return self.image_settings.file_format

    @file_format.setter
    def file_format(self, format: str = "PNG") -> None:
        """
        Available formats:
            PNG...
            """
        self.image_settings.file_format = format

    @property
    def ortho_scale(self) -> float:
        return self.camera.ortho_scale

    @ortho_scale.setter
    def ortho_scale(self, s: float) -> None:
        self.camera.ortho_scale = s

    @property
    def type(self) -> str: #self.obj is used for geometry and self.camera for camera paramters
        return self.camera.type

    @type.setter
    def type(self, type_: str) -> None:
        self.camera.type = type_

    def set_ortho(self) -> None:
        self.type = "ORTHO"

    def set_persp(self) -> None:
        self.type = "PERSP"

    @property
    def c(self) -> Vector: #Returns camera location
        return np.array(self.obj.location)

    @property
    def camera(self) -> "BlenderCamera":
        return bpy.data.cameras[self.name]

    @property
    def f(self) -> float: #RETURNS IN Meter
        if self.type  == "PERSP":
            return self.camera.lens * 1e-3 #comes in mm
        elif self.type == "ORTHO":
            return np.Inf
        else:
            return print("NO Support for panoramic")

    @f.setter
    def f(self, v: float) -> None: #V is in mm
        if self.type == "PERSP":
            self.camera.lens = v
            return
        print("NOT ALLOWED TO SET FOCAL LENGTH ON THIS CAMERA TYPE")

    @property
    def d(self) -> float:
        return self.camera.sensor_width *1e-3 #comes in mm

    @property
    def res(self) -> Vector:
        return (np.array([
            self.scene.render.resolution_x,
            self.scene.render.resolution_y])*self.scene.render.resolution_percentage/100).astype(int)

    @property
    def resx(self) -> int:
        return int(self.res[0])

    @property
    def resy(self) -> int:
        return int(self.res[1])


    def projection_matrix(self, point: Vector) -> Matrix:
        ez = 2*self.f/self.d
        C = self.T@self.R
        C_inv = C.inverted()
        a = point.copy()
        a.resize_4d()
        d = C_inv@a
        dz = d[2]
        W = self.ortho_scale
        if self.type == "PERSP":
            diag = np.array([1, 1, 1/ez, dz/ez])*ez/dz
        else:
            diag = np.array([1, 1, 1, W/2])*2/W
        return mathutils.Matrix.Diagonal(diag.tolist())@C_inv


    @property
    def inverted_world_matrix(self) -> Matrix:
        M = self.matrix_world
        loc, rot, scale = M.decompose() #Scale of camera is irrelevant to projection
        return np.array((loc@scale).inverted())

    @property
    def clip_start(self) -> float:
        return self.camera.clip_start

    @clip_start.setter
    def clip_start(self, clip: float) -> None:
        # Best value at 0.0001m
        self.camera.clip_start = clip
