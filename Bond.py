from Imports import *
from Bobject import Bobject
from BGroup import BGroup

class Bond(Bobject):
    __slots__ = ("atoms","name")
    COUNTER = 0
    def __init__(self, a1: "Atom", a2: "Atom") -> None:
        self.atoms = a1, a2
        self.name = f"{a1.name}-{a2.name}"

    def plot_blender(self) -> "Bobject":
        m1, m2 = self.build_meshes()
        m1.material = self.atoms[0].material
        m2.material = self.atoms[1].material
        return BGroup((m1, m2), self.name, self.location)

    def build_meshes(self) -> Tuple["Bobject", "Bobject"]:
        a1, a2 = self.atoms
        x1, x2 = np.array(a1.location), np.array(a2.location)
        x12 = x2 - x1
        middle = self.location
        r = self.get_radius(a1.r, a2.r)
        mesh1 = self.make_cylinder_between(x1,middle-x12*1e-6, r)
        mesh2 = self.make_cylinder_between(middle+x12*1e-6,x2, r)
        return mesh1, mesh2

    @property
    def location(self) -> Vector:
        a1, a2 = self.atoms
        x1, x2 = np.array(a1.location), np.array(a2.location)
        x12 = (x2-x1)/np.linalg.norm(x2-x1)
        return  (x1 + x12*(a1.r - a2.r) + x2 )/2

    # Get a not too thick, not too thin radius
    def get_radius(self, r1:float, r2:float) -> float:
        rad = np.array([r1,r2], dtype = float)
        r = rad.mean()/2.3
        if any(r > rad/2):
            r = min(rad)/2
        return r

    #Adding the cylinders
    def make_cylinder_between(self, x1: Vector, x2: Vector , r: float) -> "Bobject": #this can be made shorter with numpy. But it is more readable this way.
      dx = x2-x1
      dist = np.linalg.norm(dx)
      bpy.ops.mesh.primitive_cylinder_add(
          radius = r,
          depth = dist,
          location = x1+dx/2
      )
      phi = np.arctan2(dx[1], dx[0])
      theta = np.arccos(dx[2]/dist)
      blender_obj = bpy.context.active_object
      blender_obj.name = self.name + ("<-" if self.COUNTER % 2 == 0 else "->")
      self.__class__.COUNTER += 1
      blender_obj.rotation_euler[1] = theta
      blender_obj.rotation_euler[2] = phi
      o = Bobject(blender_obj.name)
      o.shade_smooth()
      o.use_auto_smooth = True
      return o
