from Imports import *
from Mesh import Mesh
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from BGroup import BGroup
from Material import Material
from Atom import Atom
from Collection import Collection


class Orbital:

    def __init__(self, qnumber: Vector = [3, 2, 0],
                       atom: "Atom" = Atom("C"),
                       STO: bool = False) -> None:
        self.atom = atom
        self.qnumber = qnumber
        self.STO = STO


    @property
    def wavefunction(self) -> Tensor:
        if self.STO:
            return from_quantum_numbers(*self.qnumber, self.atom.atom_name)
        else:
            return from_quantum_numbers(*self.qnumber)

    def gen_scalarfield(self,
                    R: Number = 2, #diameter of domain
                    n: int = 30, #number of subdivisions of domain
                    center: Vector = [], #Grid (coordinate)
                    origin: Vector = [] #Origin of scalarfield (ATOM POSITION)
                    #ALL ADDED SCALARFIELDS MUST SHARE SAME ORIGIN
                    ) -> Tensor:
        if not len(center):
            center = [0]*3
        if not len(origin):
            origin = [0]*3
        r, theta, phi = generate_grid(r = R, n = n,
                origin = origin, eucledian = False,
                center = center) #misc
        SCALARFIELD = self.wavefunction(r, theta, phi)
        del r, theta, phi
        return SCALARFIELD

    def make_mesh(self, #Plot in blender
            R: Number = 2, #diameter of domain
            n: int = 30, #number of subdivisions
            center: Vector = [0, 0, 0],
            isovalue: Number = None,
            scalarfield: Tensor = None
            ) -> Tuple[Tensor, Matrix, Tensor, Matrix]:

        if scalarfield is None:
            scalarfield = self.gen_scalarfield(R, n, center, center)

        if isovalue is None:
            isovalue = find_isovalue_mo(scalarfield)

        # Positive and negative isovalues
        vertsp, facesp = mesh_from_scalarfield(scalarfield, isovalue, R, n)
        vertsn, facesn = mesh_from_scalarfield(scalarfield, -isovalue, R, n)
        return ((vertsp, facesp), (vertsn, facesn))

    def _plot_blender(self,
             R: Number = 10, #diameter of domain
             n: int = 30, #number of subdivisions
             isovalue: float = None,
             center: Vector = [0, 0, 0],
             scalarfield: Tensor = None,
             collection: "Collection" = None,
             material_dictp: Mapping[str, Any] = {},
             material_dictn: Mapping[str, Any] = {}
             ) -> "Mesh":

        ((vp, fp), (vn, fn)) = self.make_mesh(R, n, center, isovalue, scalarfield) # +- meshes

        positive_mesh = Mesh.from_data(
                        name = self.name+"_+",
                        vertices = vp, faces = fp)
        negative_mesh = Mesh.from_data(
                        name = self.name+"_-",
                        vertices = vn, faces = fn)
        positive_mesh.flip_normals()

        positive_mesh += center
        negative_mesh += center

        #Grouping and adding materials
        g = BGroup((positive_mesh, negative_mesh), self.name, center)
        positive_mesh.material = self.build_orbital_material("+", material_dictp)
        negative_mesh.material = self.build_orbital_material("-", material_dictn)

        g.shade_smooth()

        #Adding to blender collection
        if collection:
            collection.add_group(g)
        else:
            Collection("MO").add_group(g)
        return g

    def _plot_mpl(self,
                R: Number = 10, #diameter of domain
                n: int = 30, #number of subdivisions
                isovalue: float = None,
                center: Vector = [0, 0, 0],
                scalarfield: Tensor = None
                ) -> None:

        ((vp, fp), (vn, fn)) = self.make_mesh(R, n, center, isovalue, scalarfield)
        v = np.vstack((vp[fp],vn[fn]))
        Np, Nn = len(fp), len(fn) #Number of faces
        del vp, fp, vn, fn

        # Positioning orbital:
        v = v + center

        #Plotting orbital
        mpl_obj = Poly3DCollection(
                v, facecolors = ["cornflowerblue"]*Np+["tomato"]*Nn,
                edgecolors = "lightgray", linewidths = .3
            )
        fig = plt.figure()
        ax = fig.add_subplot(111, projection = "3d")
        ax.add_collection3d(mpl_obj)
        ax.set(xlim=(-R, R), ylim=(-R, R), zlim=(-R, R))
        ax.set_box_aspect((1, 1, 1))
        for label in "x y z".split():
            getattr(ax, f"set_{label}label")(label)
        ax.set_title("nlm$={}$".format("ORBITAL"))
        plt.show()

    def build_orbital_material(self, sign: str, dict: Mapping[str, Any] = None) -> "Material":
        if dict is None:
            dict = self.build_material_dict(sign)
        m = Material(sign)
        m.build_material(dict)
        return m

    def build_material_dict(self, sign: str) -> Mapping[str, Any]:
        return {**ORBITAL_DATA[sign],**ORBITAL_DATA["+-"]}


if __name__ == "__main__":
    # Below we use this script to generate data for another script, not this one
    import sys
    sys.path.append(r'C:\Users\phfer\OneDrive\Desktop\exercises\projection')
    from Mesh import Mesh
    
    R = 10
    n = 20
    wavefunction = from_quantum_numbers(*[2,1,0])
    isovalue = find_isovalue(wavefunction, R)
    r, theta, phi = generate_grid(r = R, n = n,
                origin = [0]*3, eucledian = False,
                center = [0]*3) #misc
    scalarfield = wavefunction(r, theta, phi)
    vertsp, facesp = mesh_from_scalarfield(scalarfield, isovalue, R, n)
    vertsn, facesn = mesh_from_scalarfield(scalarfield, -isovalue, R, n)
    pmesh = Mesh(vertsp, facesp)
    nmesh = Mesh(vertsn, facesn)
    pmesh.save(r"C:\Users\phfer\OneDrive\Desktop\exercises\projection\pmesh.mesh")
    nmesh.save(r"C:\Users\phfer\OneDrive\Desktop\exercises\projection\nmesh.mesh")
