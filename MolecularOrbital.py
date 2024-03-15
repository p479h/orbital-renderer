from Imports import *
from Mesh import Mesh
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from BGroup import BGroup
from Material import Material
from Atom import Atom
from Collection import Collection
from Orbital import Orbital

class MolecularOrbital(Orbital):

    def __init__(self, qnumbers: Matrix = [[3, 2, 0]],
                       atoms: Iterable["Atom"] = [Atom("C")],
                       name: str = "MO", coeff: Vector = [],
                       STO: bool = False) -> None:
        self.atoms = atoms
        self.qnumbers = qnumbers
        self.orbitals = [Orbital(q,a,STO) for q, a in zip(qnumbers,atoms)]
        self.name = name
        self.coeff = coeff

    @property
    def wavefunctions(self) -> Tensor:
        return [o.wavefunction for o in self.orbitals]


    def gen_scalarfield(self,
                        R: Number = 2, #diameter of domain
                        n: int = 30, #number of subdivisions of domain)
                        center: Vector = [] #Origin of scalrfield
                        ) -> Tensor:
        n_atoms = len(self.atoms)
        locations = np.array(list(map(lambda a: a.location, self.atoms)))
        SCALARFIELD = np.full((n_atoms, n, n, n), 0.0)
        coeff = self.coeff
        if not len(coeff):
            coeff = np.full((n_atoms,), 1/np.sqrt(n_atoms))
        for i, (p,c) in enumerate(zip(locations, coeff)):
            r, theta, phi = generate_grid(r = R, n = n,
                    origin = p, eucledian = False, center = center) #misc
            SCALARFIELD[i, ...] = self.wavefunctions[i](r, theta, phi)*c
        del r, theta, phi
        return SCALARFIELD.sum(axis = 0)


    def plot_blender(self,
             R: Number = 10, #diameter of domain
             n: int = 30, #number of subdivisions
             isovalue: float = None,
             collection: "Collection" = None,
             material_dictp: Mapping[str, Any] = {},
             material_dictn: Mapping[str, Any] = {}
             ) -> "Mesh":

        locations = np.array(list(map(lambda a: a.location, self.atoms)))
        origin = locations.mean(axis = 0)
        scalarfield = self.gen_scalarfield(R, n, origin)
        if not isovalue:
            isovalue = find_isovalue_mo(scalarfield)
        return self._plot_blender(
            R = R,
            n = n,
            isovalue = isovalue,
            center = origin,
            scalarfield = scalarfield,
            collection = collection,
            material_dictp = material_dictp,
            material_dictn = material_dictn)

    def plot_mpl(self,
                R: Number = 10, #diameter of domain
                n: int = 30, #number of subdivisions
                isovalue: float = None
                ) -> None:
        locations = np.array(list(map(lambda a: a.location, self.atoms)))
        origin = locations.mean(0)
        scalarfield = self.gen_scalarfield(R, n, origin)
        if not isovalue:
            isovalue = find_isovalue_mo(scalarfield)
        return self._plot_mpl(R, n, isovalue, origin, scalarfield)

    @classmethod
    def from_molecule(cls, mol: "Molecule", **kwargs) -> None:
        atoms = [a for a in mol.atoms \
                        for _ in range(len(ATOM_DATA["orbitals"][a.atom_name]))]
        qnumbers = [o for a in [a for a in mol.atoms] \
                        for o in ATOM_DATA["orbitals"][a.atom_name]]
        return cls(qnumbers, atoms, f"MO_{mol.name}", **kwargs)


if __name__ == "__main__":
    a1, a2 = Atom("C", [0, 0, 0]), Atom("C", [5, 0, 0])
    qnumbers = [(2, 1, 1), (2, 1, 0)]
    MolecularOrbital(qnumbers, (a1,a2), coeff = (1,1), STO = True).plot_mpl(R=20, n = 40)
    #MolecularOrbital(qnumbers, (a1,), coeff = (1,), STO = False).plot_mpl(R=10, n = 40)
