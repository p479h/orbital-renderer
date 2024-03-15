from DataTypes import *
import numpy as np
from scipy.special import assoc_laguerre, lpmv, sph_harm
from math import factorial
from skimage import measure
from collections import deque
from collections import Counter
import sys, os
sys.path.append(os.path.join("..", "data"))
from STO3G import STO3G_DATA, QN2STO

NAME_DATA = Counter()
def gen_name(name: str = "Obj", precision: int = 3) -> str:
    """ Has to be used in a namespace containing a variable Counter"""
    NAME_DATA[name] += 1
    return f"{name}_%0{precision}i" % (NAME_DATA[name] - 1)

def isiterable(v: Iterable) -> bool:
    """Checks if variable v is iterable"""
    try:
        iter(v)
        return True
    except:
        return False

def isnumeric(v: Number) -> bool:
    """Checks if a variable is numeric"""
    try:
        float(v)
        return True
    except:
        return False

def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def complementary_hex(c: str) -> str:
    color = int(c, 16)
    comp_color = 0xFFFFFF ^ color
    comp_color = "%06X" % comp_color
    return comp_color

def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "%02x%02x%02x" % (r,g,b)

def hex_to_rgb(h,alpha=1):
    h = int("0x"+h.strip("#").replace("0x", ""),16)
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])

def generate_grid(r: float, n: int, eucledian: bool = False,
                origin: Vector = [0, 0, 0], center: Vector = [0, 0, 0]) -> np.ndarray:
    """
        returns 4d grid with points inside square of side length 2r and n points along each dimension (x,y,z)
        indexing follows (x, y, z, [x,y,z])
        -> r, theta, phi
        origin: of the atom
        center: of the grid in blender
    """
    grids = np.meshgrid(*[np.linspace(-r, r, n) for i in range(3)], indexing = "ij")
    grids = [i[..., None] for i in grids]
    p = np.concatenate(grids, axis = 3).astype(float) + (np.array(center) - origin)
    if eucledian:
        return p
    r = np.linalg.norm(p, axis = -1)
    theta = np.arccos(p[..., 2]/r)
    phi = np.arctan2(p[..., 1], p[..., 0])
    del grids, p
    return r, theta, phi

def mesh_from_scalarfield(
                        scalarfield: Tensor, #nxnxn tensor
                        isovalue: float,
                        R: float, #diameter of domain
                        n: int #number of subdivisions
                        )-> Tuple[Tensor, Matrix]:
    spacing = np.full(3, R*2/(n-1))
    try:
        verts, faces, _, _ = \
            measure.marching_cubes(scalarfield, level = isovalue, spacing = spacing)
        verts -= [R, R, R]
    except ValueError as e:
        verts, faces = np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0]]), np.array([[0, 1, 2]])
        print("NEED TO LOWER ISOVALUE")
    return verts, faces

def find_isovalue(qnumbers: Vector, R: float) -> float:
    """Finds isovalue on cube by taking maximum in sphere"""
    r, theta, phi = fibonacci_sphere(10000, R)
    return np.abs(from_quantum_numbers(*qnumbers)(r, theta, phi)).max()

def find_isovalue(f: callable, R: float) -> float:
    """Finds isovalue on cube by taking maximum in sphere"""
    r, theta, phi = fibonacci_sphere(10000, R)
    return np.abs(f(r, theta, phi)).max()


def find_isovalue_mo(scalarfield: Tensor, leverage: float = 1.0) -> float:
    front = deque(tuple([0]) + (slice(None, None),)*2, 3)
    back = deque(tuple([-1]) + (slice(None, None),)*2, 3)
    sides = [[i.copy(),i.rotate(1)][0] for i in [front, back] for _ in range(3)]
    values = [p for s in sides for p in scalarfield[tuple(s)]]
    return np.abs(values).max()*leverage

def fibonacci_sphere(samples: int =100, R: float = 1):
    """ Creates evenly spread points in sphere """
    goldenRatio = (1 + 5**0.5)/2
    i = np.arange(0, samples)
    theta = 2 *np.pi * i / goldenRatio
    phi = np.arccos(1 - 2*(i+0.5)/samples)
    r = theta*0+1
    return r*R, theta, phi

##Now we do some ivo stuff
def from_quantum_numbers(n: int, l: int, m: int, atom: str = None) -> Callable:
    """
    Construct the wave function. If atom is provided, STO-3g basis is used.

    Example:
    --------
    >>> from scipy.integrate import solve_ivp, tplquad
    >>> qnumbers = 3, 2, -1
    >>> n, l, m = qnumbers
    >>> f = from_quantum_numbers(*qnumbers)
    >>> func = lambda phi, theta, r: f(r, theta, phi)**2*r**2* np.sin(theta)
    >>> print(tplquad(func, 0, np.inf, 0, np.pi, 0, 2*np.pi)[0])
    0.9999999999999996
    """
    if atom is None:
        return lambda r, theta, phi: radial(n,l,r) * angular(l,m, -phi, theta)
    return STO((n, l, m), atom)

def STO(qnumbers: Vector, atom: str) -> Callable:
    N,L,_ = qnumbers
    a = STO3G_DATA[atom][f"{N},{L}"]["a"]
    c = STO3G_DATA[atom][f"{N},{L}"]["c"]
    n, l, m = QN2STO[tuple(qnumbers)]
    def inner(r: Tensor, theta: Tensor, phi: Tensor) -> Tensor:
        nonlocal a, c
        if isiterable(r):
            shape = (slice(None, None),) + (None,)*r.ndim
            a, c = a[shape], c[shape]
        x = np.sin(theta)*np.cos(phi)*r
        y = np.sin(theta)*np.sin(phi)*r
        z = np.cos(theta)*r
        N = np.sqrt(
        (8*a)**(l+n+m) * factorial(l)*factorial(m)*factorial(n)/\
        (factorial(2*l)*factorial(2*m)*factorial(2*n))
        )
        return  x**n * y**l * z**m * np.sum(N*c*(2*a/np.pi)**(3/4)*np.exp(-a*r**2), axis = 0)
    return lambda r, theta, phi: inner(r, theta, phi)

def angular(l,m,theta,phi):
    """
    Construct the angular part of the wave function
    """
    # see: https://en.wikipedia.org/wiki/Spherical_harmonics#Real_form
    #
    # this create so-called Tesseral spherical harmonics
    #
    if m == 0:
        return np.real(sph_harm(m,l,theta,phi))
    elif m > 0:
        return np.real(sph_harm(-m,l,theta,phi) + (-1)**m * sph_harm(m,l,theta,phi)) / np.sqrt(2.0)
    return np.imag(sph_harm(m,l,theta,phi) - (-1)**m * sph_harm(-m,l,theta,phi)) / np.sqrt(2.0)

def radial(n,l,r):
    """
    This is the formulation for the radial wave function as encountered in
    Griffiths "Introduction to Quantum Mechanics 3rd edition"
    """
    a = 1.0
    rho = 2.0 * r / (n * a)
    val =  np.sqrt((2.0 / (n * a))**3) * \
           np.sqrt(factorial(n - l - 1) / (2 * n * factorial(n + l))) * \
           np.exp(-0.5 * rho) * \
           rho**l * \
           assoc_laguerre(rho, n-l-1, 2*l+1)
    return val

def azimuthal(m, phi):
    """
    Construct azimuthal part of the angular wave function
    """
    pre = 1.0 / np.sqrt(4.0 * np.pi)
    if m == 0:
        return pre
    if(m > 0):
        return pre * np.cos(m * phi)
    return pre * np.sin(-m * phi)

def polar(l,m,theta,phi):
    """
    Construct polar part of the angular wave function
    """
    pre = np.sqrt((2 * l + 1) * factorial(l - np.abs(m)) /\
                  factorial(l + np.abs(m)))
    return pre * lpmv(np.abs(m), l, np.cos(theta))



if __name__ == "__main__":
    import doctest
    from scipy.integrate import tplquad, solve_ivp
    import matplotlib.pyplot as plt
    # doctest.testmod()
    atom = "B"
    qnumbers = 2, 1, -1
    wavefunction = from_quantum_numbers(*qnumbers, atom)
    wavefunction0 = from_quantum_numbers(*qnumbers, atom)
    wavefunction1 = from_quantum_numbers(*qnumbers)
    def rho(r, theta, phi):
        return wavefunction(r, theta, phi)**2

    def dI(phi, theta, r):
        return rho(r, theta, phi)*np.sin(theta)*r**2

    r = tplquad(dI, 0, 100, 0, np.pi, 0, np.pi*2)
    print(r)
    #Implies result must be multiplied by 4pi

    r = np.linspace(0, 100, 1000)
    psi0 = wavefunction0(r, 0, 0)
    psi1 = wavefunction1(r, 0, 0)
    plt.plot(r, psi0, label = "sto")
    plt.plot(r, psi1, label = "qnumbers")
    plt.legend()
    plt.show()
