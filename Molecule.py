from Imports import *
from Atom import Atom
from BGroup import BGroup
from Bond import Bond
from Collection import Collection

class Molecule:
    """
        This class unites many atoms, allowing them to bond and be rendered together
        Here each atom becomes associated to an index in the arrays with info about the molecule
        """
    __slots__ = ("name", "atoms", "bonds", "atom_names", "bond_indices", "bond_orders")
    def __init__(self, name: str, atoms: Iterable[str], locations: Matrix,
                    bonds: Matrix, bond_orders: Vector = None) -> None:
        self.name = name
        self.atoms = [Atom(a,l) for a,l in zip(atoms, locations)]
        self.bonds = [Bond(*[self.atoms[i] for i in b]) for b in bonds]
        self.atom_names = atoms
        self.bond_indices = bonds
        self.bond_orders = bond_orders

    @property
    def atom_colors(self) -> str:
        return [a.color for a in self.atoms]

    @property
    def atom_locations(self) -> Matrix:
        return np.array([a.location for a in self.atoms])

    @property
    def atom_radii(self) -> Vector:
        return np.array([a.r for a in self.atoms])

    def plot_atoms_blender(self) -> Iterable["Bobject"]:
        return [a.plot_blender() for a in self.atoms]

    def plot_bonds_blender(self) -> Iterable["BGroup"]:
        return [b.plot_blender() for b in self.bonds]

    def plot_blender(self, collection: "Collection" = None,
                     plot_bonds: bool = True) -> "BGroup":
        atoms = self.plot_atoms_blender()
        if plot_bonds:
            bonds = self.plot_bonds_blender()
            g = BGroup(atoms + bonds, self.name, self.location)
        else:
            g = BGroup(atoms, self.name, self.location)
        if collection:
            collection.add_group(g)
        else:
            Collection("Molecules").add_group(g)
        return g

    @property
    def location(self) -> Vector:
        return self.atom_locations.mean(axis = 0)

    def plot_mpl(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection ="3d")
        for b in np.array(self.bond_indices):
            ax.plot(*(self.atom_locations[b]).T, c = "black")

        for a in set(self.atom_names):
            indices = np.array([i for i, n in enumerate(self.atom_names) if n == a])
            points = self.atom_locations[indices]
            color =  hex_to_rgb(self.atom_colors[indices[0]])
            r = self.atom_radii[indices[0]]
            ax.scatter(*points.T, c = color, s = r*80)
        R = np.linalg.norm(self.atom_locations, axis=-1).max()*1.2
        ax.set(xlim=(-R, R), ylim=(-R, R), zlim=(-R, R))
        ax.set_box_aspect((1, 1, 1))
        plt.show()

    @classmethod
    def from_file(cls, filepath: str) -> "Molecule":
        filename = os.path.basename(filepath)
        molecule_name, ext = os.path.splitext(filename)
        if ext == ".xyz":
            Atom_ = namedtuple("Atom_", "name location")
            atoms, locations = FileManager.read_xyz(filepath)
            bonds = cls.detect_bonds_xyz(
                [Atom_(a, l) for a, l in zip(atoms, locations)])
            orders = np.full(len(atoms), 1, dtype = int)
        elif ext == ".mol":
            atoms, locations, bonds, orders = FileManager.read_mol(filepath)
        else:
            print("Unsuported filetype")
        return cls(molecule_name, atoms, locations, bonds, orders)


    @classmethod # I got this from ivo. Not sure where these exact numbers come from, but it works well on xyz files.
    def detect_bonds_xyz(cls, atoms):
        #First we set the limits for each kind of bond
        distances = np.full((86, 86), 3.0)
        for i in range(0, 86):
            distances[i][1] = 1.4
            distances[1][i] = 1.4

            if i > 20:
                for j in range(2,20):
                    distances[i][j] = 2.8
                    distances[j][i] = 2.8
            else:
                for j in range(2,20):
                    distances[i][j] = 2.0
                    distances[j][i] = 2.0

        bonds = []
        for i, a1 in enumerate(atoms[:-1]):
            for j, a2 in enumerate(atoms[i+1:]):
                a1id = ATOM_DATA["id"][a1.name]
                a2id = ATOM_DATA["id"][a2.name]
                a1id, a2id = sorted([a1id, a2id])
                d = np.linalg.norm(np.array(a1.location) - a2.location)
                if d < distances[a1id, a2id]:
                    bonds.append([i, j+i+1])
        return np.array(bonds, dtype = int)



    @staticmethod # I also got this function from Ivo
    def write_xyz(names, vertices, outfile):
        # output results
        f = open(outfile, 'w')
        f.write("%i\n\n" % len(names))
        for n, v in zip(names, vertices):
            f.write('%s  %12.6f  %12.6f  %12.6f\n' % (n, *v))
        f.close()

    def __imatmul__(self, m: Matrix) -> None:
        for a in self.atoms:
            a.location = (np.array(m)@np.array([*a.location[:3], 1]))[:3]
        return self


if __name__ == "__main__":
    name = "benzene"
    filepath = os.path.join(*f"data Molecules {name}.xyz".split())
    m = Molecule.from_file(filepath)
    m@=mathutils.Matrix.Rotation(np.pi/2, 4, [0, 1, 0])
    m.plot_mpl()
