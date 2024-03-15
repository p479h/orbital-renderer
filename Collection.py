from Imports import *

class Collection:

    def __init__(self, name = "str") -> None:
        self.name = name

    def create_collection(self) -> "BlenderCollection":
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.collection.create(name = self.name)
        bpy.context.scene.collection.children.link(self.collection)
        return self.collection

    @property
    def collection(self) -> "BlenderCollection":
        if bpy.data.collections.get(self.name):
            return bpy.data.collections.get(self.name)
        return self.create_collection()

    def add_obj(self, obj: "Bobject") -> None:
        self.unlink_collections(obj)
        self.collection.objects.link(obj.obj)

        if hasattr(obj, "__iter__"):
            for o in obj:
                self.add_obj(o)

    def add_group(self, g: "BGroup") -> None:
        for obj in g:
            self.add_obj(obj)
        self.add_obj(g)

    @staticmethod
    def unlink_collections(obj: "Bobject") -> None:
        for c in obj.obj.users_collection:
            c.objects.unlink(obj.obj)
