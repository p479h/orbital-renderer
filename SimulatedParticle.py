from Imports import *
from Bobject import Bobject
from Collection import Collection
from Material import Material

class SimulatedParticle(Bobject):
    def __init__(self, name, data: dict):
        self.dat = data
        self.name = name
        self.x = np.array(data["x"])
        if not self.obj:
            self.draw_blender()
            self.shade_smooth()
            self.location = self.x[0]
        self.add_keyframes()

    def draw_blender(self):
        if "radius" in self.dat.keys():
            r = self.dat["radius"]
        else:
            r = 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius = r,
            location = (0, 0, 0),
            segments = 32
        )
        blender_obj = bpy.context.active_object
        blender_obj.name = self.name
        Collection("Particles").add_obj(self)
        #self.material = Material("particle")

    def add_keyframes(self):
        self.deselect_all()
        self.select()
        for i, p in enumerate(self.x):
            self.location = p
            self.obj.keyframe_insert(data_path="location", frame=i)
        self.linearize_interpolation()

    def linearize_interpolation(self):
        fc = self.obj.animation_data.action.fcurves
        for index in range(3):
            loc_curve = fc.find('location', index=index)
            for k in loc_curve.keyframe_points:
                k.interpolation = "LINEAR"

    @classmethod
    def from_file(cls, filepath): #Several particles from similation
        with open(filepath, "r") as f:
            particle_data = json.load(f)
        SIMDATA = particle_data.pop("simdata")#parameters used in simulation
        particles = {"simdata": SIMDATA}
        for pname, pdata in particle_data.items():
            particles[pname] = \
                cls(pname, pdata)
        return particles
