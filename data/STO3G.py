from collections import defaultdict
from typing import Mapping
import numpy as np
import json
import re
import os
import time

QN2STO = {
    #n  l  m:  #n  l  m
    (1, 0, 0): (0, 0, 0), #S
    (2, 0, 0): (0, 0, 0), #S
    (2, 1, -1): (0, 1, 0), #Py
    (2, 1, 0): (0, 0, 1),#Pz
    (2, 1, 1): (1, 0, 0),#Px
    }



def to_dict(d: Mapping) -> Mapping:
    for k, v in d.items():
        if type(v) in (defaultdict, dict):
            d[k] = to_dict(v)
    return dict(d)

def to_type(d: Mapping, t: "Type") -> Mapping:
    for k, v in d.items():
        if type(v) in (defaultdict, dict):
            d[k] = to_dict(v)
        else:
            d[k] = t(v)
    return dict(d)

def print_dict(d: Mapping, c: int = 0) -> None:
    if c == 0:
        print("{", end=  "")
    for k, v in d.items():
        if c > 0:
            print("\t"*c, end = "", sep ="")
        print(k, ":{", sep = "")
        if type(v) == dict:
            print_dict(v, c+1)
        else:
            print("\t"*(c+1), end = "")
            print(v)
        if c > 0:
            print("\t"*c, end = "}\n", sep ="")
    if c == 0:
        print("}")

def recdd() -> defaultdict:
    return defaultdict(recdd)

this_dir = os.path.dirname(__file__)
# datapath = os.path.join(this_dir, "STO3G.txt")
data2path = os.path.join(this_dir, "sto-3g.1.json")
name_data_path = os.path.join(this_dir, "atoms.json")


# def load_STO3G_DATA(datafile: str = datapath):
#     pat = re.compile(r"([A-Z][a-z]?)[ \t]*" + r"(\d,\d)[ \t]*" + r"([-]*\d+\.\d+)[ \t]*"*6)
#     d = defaultdict(recdd)
#
#     with open(datafile, "r") as f:
#         f.readline() #Skip first line
#         for l in f.readlines():
#             atom, nl, a1, c1, a2, c2, a3, c3 = pat.findall(l)[0]
#             d[atom][nl]["a"] = np.array([a1, a2, a3], dtype=float)
#             d[atom][nl]["c"] = np.array([c1, c2, c3], dtype=float)
#
#     return to_dict(d)

# STO3G_DATA = load_STO3G_DATA()
STO3G_DATA2 = json.load(open(data2path))
name_data = json.load(open(name_data_path))

def load_ac(atom_number: str):
    atom_data = STO3G_DATA2["elements"][str(atom_number)]["electron_shells"]
    shells = []
    nums = [f"{n},{l}" for n in range(1,5) for l in range(n)]
    data = {}
    counter = 0
    for shell in atom_data:
        alpha = np.array(shell["exponents"], dtype = float)
        for c in shell["coefficients"]:
            c = np.array(c, dtype = float)
            data[nums[counter]] = {"a": alpha, "c": c}
            counter+=1
    return data

dummy = {}
names = list(name_data["id"].keys())
values = list(name_data["id"].values())
for i in range(1, 20):
    name = names[values.index(i)]
    dummy[name] = load_ac(str(i))
STO3G_DATA = dummy

# if __name__ == "__main__":
    # print_dict(STO3G_DATA)
    # print(QN2STO[(1,0,0)])
    #print(STO3G_DATA2)
