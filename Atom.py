#Import ATOM_DATA
from Imports import *
from Object import Object
from Bobject import Bobject
from Material import Material

class Atom(Object):

    def __init__(self,
                 atom: str = "C",
                 location: Vector = [0, 0, 0]
                 ) -> None:
        super().__init__(atom, np.array(location))
        self.atom_name = atom

    @property
    def color(self) -> "hex_str":
        return ATOM_DATA["colors"][self.atom_name]

    @property
    def Z(self) -> int:
        return ATOM_DATA["id"][self.atom_name]

    @property
    def r(self) -> float:
        return ATOM_DATA["radii"][self.atom_name]

    @property
    def material(self) -> "BlenderMaterial":
        return self.build_material(ATOM_DATA["material_settings"])

    def plot_blender(self, material_dict: Mapping[str, Any] = {}) -> "Bobject":
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius = self.r,
            location = self.location,
            segments = 32
        )
        # Retrieve and name object
        blender_obj = bpy.context.active_object
        blender_obj.name = self.name

        obj = Bobject(blender_obj.name)
        obj.shade_smooth()
        obj.material = self.build_material(ATOM_DATA["material_settings"],
                                            material_dict)
        return obj

    def build_material(self, default_dict: Mapping[str,Any],
                             material_dict: Mapping[str, Any] = {}) -> "Material":
        dict = {"Base Color": self.color, **default_dict}
        for k, v in material_dict.keys():
            dict[k] = v
        return Material(self.atom_name, dict)




if __name__ == "__main__":
    a = Atom()
    print(a.location)
    print(a.color)
