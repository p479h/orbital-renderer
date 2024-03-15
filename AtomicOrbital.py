from Imports import *
from Mesh import Mesh
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from BGroup import BGroup
from Atom import Atom
from Material import Material
from Orbital import Orbital

class AtomicOrbital(Orbital):

    def __init__(self,
                qnumber: Vector = [3, 2, 0],
                atom: "Atom" = None,
                STO: bool = False):
        super().__init__(qnumber, atom, STO)

    @property
    def name(self) -> "str":
        return f"{self.qnumber}_AO"

    def plot_blender(self,
             R: Number = 10, #diameter of domain
             n: int = 30, #number of subdivisions
             isovalue: float = None,
             collection: "Collection" = None,
             material_dictp: Mapping[str, Any] = None,
             material_dictn: Mapping[str, Any] = None) -> "Mesh":

        if not isovalue:
            isovalue = find_isovalue(self.wavefunction,R)
        scalarfield = self.gen_scalarfield(R, n, self.atom.location, self.atom.location)

        return self._plot_blender(
            R = R,
            n = n,
            isovalue = isovalue,
            center = self.atom.location,
            scalarfield = scalarfield,
            collection = collection,
            material_dictp = material_dictp,
            material_dictn = material_dictn)

    def plot_mpl(self,
                R: Number = 2, #diameter of domain
                n: int = 30, #number of subdivisions
                isovalue: float = None
                ) -> None:
        if not isovalue:
            isovalue = find_isovalue(self.wavefunction, R)
        scalarfield = self.gen_scalarfield(R, n, self.atom.location, self.atom.location)
        self._plot_mpl(R, n, isovalue, self.atom.location, scalarfield)


if __name__ == "__main__":
    # AtomicOrbital([3, 2, 2]).plot_mpl(R=20, n = 50)
    a = Atom("C", [0, 0, 0])
    AtomicOrbital([3, 1, 0], a, STO = False).plot_mpl(R=20, n = 20)
