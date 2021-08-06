#!/Local/tmp/bin/anaconda3/bin/python
import xml.etree.ElementTree as ET
import argparse
import numpy as np
import os
from shutil import copyfile

def parse_stuff():
    parser = argparse.ArgumentParser(description='Scaling fleur files')

    parser.add_argument("--mis", type=float, default=0.95, help="minimal scale")
    parser.add_argument("--mas", type=float, default=1.05, help="maximal scale")
    parser.add_argument("-n", type=int, default = 7, help="number of steps")
    parser.add_argument("--infol", type=str, default="", help="input folder")
    parser.add_argument("--outfol", type=str, default="", help="output folder")
    parser.add_argument("--itmax", type=int, default=99, help="itmax in fleur")

    args = parser.parse_args()
    
    return args

p = parse_stuff()

scale = np.linspace(p.mis, p.mas, p.n)

if(len(p.infol) == 0 or p.infol[-1] == "/"):
    infol = p.infol
else:
    infol = p.infol + "/"

if(len(p.outfol) == 0 or p.outfol[-1] == "/"):
    outfol = p.outfol
else:
    outfol = p.outfol + "/"

has_sym = os.path.isfile(infol + "sym.out")

tree = ET.parse(infol + "inp.xml")
root = tree.getroot()

for scfloop in root.iter("scfLoop"):
    scfloop.attrib["itmax"] = str(p.itmax)


for s in scale:
    for bulklat in root.iter("c"):
        bulklat.attrib["scale"] = str(s)
    
    scale_fol = "{}scale={:6.4f}/".format(outfol, s)
    try:
        os.mkdir(scale_fol)
    except:
        print("creation of {} failed".format(scale_fol))
    
    if(has_sym):
        copyfile("sym.out", "{}sym.out".format(scale_fol))
    
    tree.write("{}inp.xml".format(scale_fol))
