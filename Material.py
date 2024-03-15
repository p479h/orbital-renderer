from Imports import *

class Material:

    def __init__(self, name: str, dict: Mapping[str, Any] = {}) -> None:
        self.name = name
        self.create_material(dict)

    def create_material(self, dict: Mapping[str, Any] = {}) -> "BlenderMaterial":
        if bpy.data.materials.get(self.name):
            return bpy.data.materials.get(self.name)
        mat = bpy.data.materials.new(name = self.name)
        mat.use_nodes = True
        if len(dict):
            self.build_material(dict)
        return mat

    @property
    def mat(self) -> "BlenderMaterial":
        return bpy.data.materials.get(self.name)

    @property
    def nodes(self) -> "BlenderNode":
        return self.mat.node_tree.nodes

    @property
    def inputs(self) -> "BlenderMaterialInputs":
        return self.nodes["Principled BSDF"].inputs

    def get_input(self, input: str) -> "BlenderMaterialInput":
        return self.inputs.get(input)

    def set_input(self, input: str, value: Any) -> None:
        self.get_input(input).default_value = value

    def build_material(self, mat_dict: Mapping[str,Any]) -> None:
        for key, value in dict(mat_dict).items():
            if (type(value) == str) and (key in ["Base Color", "Emission"]):
                value = hex_to_rgb(value)
            if (key in ["Base Color", "Emission"]):
                self.set_input(key, value)
                self.mat.diffuse_color = value
                continue
            self.set_input(key, value)

    @classmethod
    def Random(cls, name: str, material_dict: dict) -> "Material":
        m = cls(name, {**material_dict, "Base Color": (*np.random.rand(3),1)})
        return m
