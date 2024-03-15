# General libraries
import os
import re
import sys
import json
import time
import numpy as np
from collections import namedtuple
from collections import Counter
from importlib import reload as reload_module

this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir,"utils"))
sys.path.append(os.path.join(this_dir,"data"))

#Blender imports
try:
    import bpy
except:
    print("bpy not imported")
try:
    import mathutils
except:
    print("mathutils not imported")
    print("imported matutils instead")
    import matutils as mathutils
try:
    import matplotlib.pyplot as plt
except:
    print("matplotlib not imported")

# NAME_DATA #from MiscFunctions could be defined here as well

# Data for blender materials
ATOM_DATA_PATH = os.path.join("data","atoms.json")
ORBITAL_DATA_PATH = os.path.join("data", "orbital_material.json")
ATOM_DATA = json.load(open(ATOM_DATA_PATH, "r"))
ORBITAL_DATA = json.load(open(ORBITAL_DATA_PATH, "r"))
from color_combinations import COLOR_COMBINATIONS
from STO3G import STO3G_DATA, QN2STO

# Own modules
import BlenderPresets, DataTypes, MiscFunctions, FileManager, matutils,\
        color_combinations, STO3G
to_reload = [BlenderPresets, DataTypes, MiscFunctions, FileManager, matutils,
        color_combinations, STO3G]
for module in to_reload:
    reload_module(module)
from BlenderPresets import *
from DataTypes import *
from MiscFunctions import *
from FileManager import FileManager
from color_combinations import COLOR_COMBINATIONS
from STO3G import STO3G_DATA, QN2STO
