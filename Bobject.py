from Imports import *

#TODO Add collection support

class Bobject:
    """ Collection to wrap BLENDER objects and make them easier to use."""

    def __init__(self,
                name: str) -> None:
        self.name = name

    def _update_transform(func) -> None:
        """Transformation is not applied unless matrix_world is changed.
        This function updates the world matrix based on loation scale
        and rotation."""
        def inner(self, arg: Union[Number, Vector]) -> None:
            func(self, arg) #Update quantity and then the matrix
            T = mathutils.Matrix.Translation(self.location)
            R = self.rotation.to_matrix().to_4x4()
            S = mathutils.Matrix.Diagonal(self.scale).to_4x4()
            self.matrix_local = T@R@S # The matrix world is automatically updated
        return inner

    def shade_smooth(self, use_auto_smooth: bool = True) -> None:
        self.select()
        bpy.ops.object.shade_smooth()
        self.use_auto_smooth = use_auto_smooth

    def apply_scale(self) -> None:
        self.apply(scale = True)

    def apply_rotation(self) -> None:
        self.apply(rotation=True)

    def apply_location(self) -> None:
        self.apply(location=True)

    def apply(self,
            location: bool = False,
            rotation: bool = False,
            scale: bool = False) -> None:
        Mat = mathutils.Matrix
        mw = Mat(self.matrix_local)
        mb = Mat(self.matrix_basis)
        loc, rot, scale = mb.decompose()

        T = Mat.Translation(loc)
        R = rot.to_matrix().to_4x4()
        S = Mat.Diagonal(scale).to_4x4()
        left_overs = Mat.Identity(4)
        if hasattr(self.obj, "data"):
            for transform, BOOL in zip([S,R,T], [scale, rotation, location]):
                if not BOOL:
                    left_overs = transform@left_overs
                    continue
                self.obj.data.transform(transform)
        self.obj.matrix_basis = left_overs

    def gen_name(self, extra: str = "") -> str:
        """ Adds to the part of the name between name and extension """
        n = os.path.splitext(self.name)
        return "".join([n[0], extra, n[1]])

    @property
    def parent(self) -> "BlenderObject":
        return self.obj.parent

    @property
    def collection(self) -> "BlenderCollection":
        return self.obj.users_collection[0]

    @collection.setter
    def collection(self, c: "Collection") -> None:
        if type(c) == Bobject:
            c = c.collection
        self.collection.objects.unlink(self.obj)
        c.objects.link(self.obj)

    @parent.setter
    def parent(self, p: "Bobject") -> None:
        self.deselect_all()
        self.select()
        p.select()
        bpy.ops.object.parent_set(type="OBJECT")


    @property
    def context(self) -> "BlenderContext":
        return bpy.context

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if hasattr(self, "_name"):
            self.obj.name = name
        self._name = name

    @property
    def mesh(self) -> "BlenderMesh":
        return self.obj.data #Meshes are not "owned" by objects

    @property
    def data(self) -> "BlenderMesh":
        return self.mesh

    @property
    def use_auto_smooth(self) -> bool:
        return self.mesh.use_auto_smooth

    @use_auto_smooth.setter
    def use_auto_smooth(self, b: bool) -> None:
        self.mesh.use_auto_smooth = b

    @property
    def material(self) -> "BlenderMaterial":
        return self.obj.active_material

    @material.setter
    def material(self, m: Union["Material", "BlenderMaterial"]) -> None:
        if not type(m) is bpy.types.Material:
            m = m.mat
        self.data.materials.clear()
        self.data.materials.append(m)
        self.obj.active_material = m

    @property
    def matrix_basis(self) -> Matrix:
        return self.obj.matrix_basis

    @matrix_basis.setter
    def matrix_basis(self, m: Matrix) -> None:
        self.obj.matrix_basis = mathutils.Matrix(m)

    @property
    def matrix_local(self) -> Matrix:
        return self.obj.matrix_local

    @matrix_local.setter
    def matrix_local(self, m: Matrix) -> None:
        self.obj.matrix_local = M = mathutils.Matrix(m)
        if self.parent:
            M = self.parent.matrix_world@m
        self.matrix_world = M

    @property
    def scene(self) -> "Scene":
        return bpy.data.scenes["Scene"]

    @property
    def dimensions(self) -> Vector:
        return self.obj.dimensions

    @dimensions.setter
    @_update_transform
    def dimensions(self, d: Vector) -> None:
        if not isiterable(d):
            d = [d]*3
        d = mathutils.Vector(d)
        self.obj.dimensions = d

    @property
    def obj(self) -> "BlenderObject":
        return bpy.data.objects.get(self.name)

    @property
    def R(self) -> Matrix:
        """ 3x3 scale matrix"""
        _, R, _ = self.obj.matrix_local.decompose()
        return R.to_matrix().to_4x4()

    @property
    def T(self) -> Matrix:
        T, _, _ = self.obj.matrix_local.decompose()
        return mathutils.Matrix.Translation(T)

    @property
    def S(self) -> Matrix:
        _, _, S = self.obj.matrix_local.decompose()
        return mathutils.Matrix.Diagonal(S).to_4x4()

    @property
    def rotation(self) -> "BlenderRotation":
        if self.obj.rotation_mode == "QUATERNION":
            return self.obj.rotation_quaternion
        return self.obj.rotation_euler

    @rotation.setter
    @_update_transform
    def rotation(self, r: "BlenderRotation") -> None:
        if type(r).__name__ == "Euler":
            self.obj.rotation_euler = r
        elif type(r).__name__ == 'QUATERNION':
            self.obj.rotation_quaternion = r
        else:#Assume euler
            if not isiterable(r):
                r = mathutils.Vector([r, r, r])
            r = mathutils.Vector(r)
            self.obj.rotation_euler = mathutils.Euler(r, order = "XYZ")

    @property
    def location(self) -> Vector:
        return self.obj.location

    @location.setter
    @_update_transform
    def location(self, v: Vector) -> None:
        self.obj.location = mathutils.Vector(v)

    @property
    def scale(self) -> Vector:
        return self.obj.scale

    @scale.setter
    @_update_transform
    def scale(self, scale: Union[Number, Vector]) -> None:
        if isiterable(scale):
            self.obj.scale = mathutils.Vector(scale)
        else:
            self.obj.scale = mathutils.Vector(np.ones(3)*scale)

    def get_face_vertices(self, face: int = 1) -> Matrix:
        mesh = self.data
        faces = mesh.polygons[:]
        positions = faces[face].vertices[:]
        M = self.matrix_world
        vertices = mathutils.Matrix([M@mesh.vertices[i].co for i in positions])
        return vertices

    @property
    def matrix_world(self) -> Matrix:
        return self.obj.matrix_world


    @matrix_world.setter
    def matrix_world(self, m: Matrix) -> None:
        m = mathutils.Matrix(m)
        self.obj.matrix_world = m

    @property
    def properties(self) -> dict:
        """ To be implemented by child classes"""
        properties = ["location"]
        return {attr:getattr(self,attr) for attr in properties}

    @property
    def active(self) -> bool:
        return (self.obj is self.__class__.active_obj())

    @property
    def selected(self) -> bool:
        return self.obj in self.context.selected_objects

    def select(self) -> None:
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj

    def deselect(self) -> None:
        self.obj.select_set(False)
        if self.active:
            bpy.context.view_layer.objects.active = None

    @staticmethod
    def active_obj() -> bool:
        return bpy.context.view_layer.objects.active

    @classmethod
    def deselect_all(cls) -> None:
        bpy.ops.object.select_all(action="DESELECT")

    def to_origin(self, type: str = "GEOMETRY_ORIGIN") -> None:
        self.deselect_all()
        self.select()
        bpy.ops.object.origin_set(type = "GEOMETRY_ORIGIN")

    def rotate(self, angle: float, mode: str = "rad", axis: str = "Z") -> None:
        assert mode in ("rad", "deg")
        if mode == "deg":
            angle*=np.pi/180
        rotation_matrix = mathutils.Matrix.Rotation(angle, 4, axis.upper())
        for obj in self.objs:
            obj@=rotation_matrix

    def delete(self) -> None:
        objs = bpy.data.objects
        obj = self.obj
        try:
            mesh = self.mesh
        except: # We probably have a curve OR empty object
            None
        objs.remove(obj, do_unlink = True)
        try:
            meshes = bpy.data.meshes
            meshes.remove(mesh)
        except:
            None
        #bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        #bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

    def render(self,
                path: str,
                name: str = None,
                ext: str = "PNG",
                rx: Number = 540,
                ry: Number = 540,
                res_percentage: Number = 100,
                color_mode: str = "RGBA",
                counter: str = "", #Added to the end of the name
                ) -> None:
        #Ens\ture destination exists
        if name is None:
            name = self.name
        path = os.path.join(os.getcwd(), path, name + counter+"."+ext)
        parent_directory = os.path.dirname(path)

        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)

        #Set rendering parameters
        self.scene.render.filepath = path
        self.scene.render.resolution_x = int(rx*res_percentage/100)
        self.scene.render.resolution_y = int(ry*res_percentage/100)
        self.scene.render.image_settings.file_format = ext.replace(".", "")
        self.scene.render.image_settings.color_mode = color_mode
        bpy.ops.render.render(use_viewport = False, write_still = True)

    def __repr__(self) -> str:
        return self.name + ": "+"\n{\n\t"+",\n\t".join([f"{k}: {v}" for k, v in self.properties.items()])+"\n}\n"

    def __imatmul__(self, M: Matrix) -> None:
        """ Applies transformation to the matrix world of object """
        self.matrix_local= self@M
        return self

    def __matmul__(self, M: Matrix) -> Matrix:
        """ Returns transformed matrix world """
        M = np.array(M)
        if M.shape[0] < 4:
            m = M.copy()
            M = np.eye(4)
            M[:m.shape[-1],:m.shape[-1]] = m[:]
        M = mathutils.Matrix(M)
        return M@self.matrix_local

    def __mul__(self, v: Union[Number, Vector]) -> Vector:
        if not isiterable(v):
            v = mathutils.Vector([1, 1, 1])*v
        v = mathutils.Vector(v)
        return self.scale*v

    def __imul__(self, v: Union[Vector, Number]) -> "Bobject":
        self.scale = self*v
        return self


    def __add__(self, V: Union[Number, Vector]) -> "Bobject":
        if not isiterable(V):
            V = mathutils.Vector([1, 1, 1])*V
        V = mathutils.Vector(V)
        return self.location + V

    def __iadd__(self, V: Union[Number, Vector]) -> "Bobject":
        self.location = self + V
        return self
