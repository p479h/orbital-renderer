from Imports import *
from Bobject import Bobject

class Mesh(Bobject):
    def __init__(self,
                 name: str) -> None:
        super().__init__(name)


    def flip_normals(self) -> None:
        self.deselect_all()
        self.select()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.editmode_toggle()
        self.deselect_all()


    @property
    def mesh(self) -> "BlenderMesh":
        return bpy.data.meshes.get(self.name)

    @property
    def data(self) -> "BlenderMesh":
        return self.mesh


    @classmethod
    def from_data(cls, name, vertices, faces, edges = [], collection: str = "Collection") -> "BlenderMesh":
        new_mesh = bpy.data.meshes.new(name)
        if type(faces) != list:
            faces = faces.tolist()
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        new_object = bpy.data.objects.new(name, new_mesh)
        collection_ = bpy.data.collections.get(collection)
        collection_.objects.link(new_object)
        return cls(name)
