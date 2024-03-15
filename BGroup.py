from Imports import *
from Bobject import Bobject

class BGroup(Bobject):
    """
        Object (Empty), which parents objs and makes them follow it.
        Overrides the need for Joining meshes.
    """
    def __init__(self, objs: Iterable["Bobject"],
                    name: str = "G", location  = None) -> None:
        if location is None:
            location = np.mean([obj.location for obj in objs], axis = 0)
            if len(location) == 0:
                location = [0, 0, 0]
        self.name = name
        self.objs = []
        self.create_obj(location)
        self.add_objs(objs)
        self.assign_collection()

    def assign_collection(self) -> None:
        self.collection = self.objs[0].collection

    def flip_normals(self) -> None:
        for o in self:
            o.flip_normals()

    @property
    def locations(self) -> Matrix:
        return np.array([o.location for o in self.objs])

    def shade_smooth(self) -> None:
        for obj in self:
            obj.shade_smooth()

    def create_obj(self, location: Vector = [0, 0, 0]) -> "BlenderObject":
        bpy.ops.object.empty_add(type='PLAIN_AXES', location = location)
        o = bpy.context.view_layer.objects.active
        o.name = self.name

    def add_obj(self, obj: "Bobject") -> None:
        self.objs.append(obj)
        obj.parent = self

    def add_objs(self, objs: Iterable["Bobject"]) -> None:
        [self.add_obj(o) for o in objs]

    def for_each(self, func: callable) -> None:
        [func(o) for o in self]

    def delete_all(self) -> None:
        for o in self:
            if type(o) == type(self):
                o.delete_all()
                continue
            o.delete()
        self.delete()

    def __len__(self) -> int:
        return len(self.objs)

    def __iter__(self) -> Iterable["Bobject"]:
        for o in self.objs:
            yield o
