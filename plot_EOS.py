#!/Local/tmp/bin/anaconda3/bin/ipython3
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import sys
import os

def get_totalE(fol):
    if(fol[-1] == "/"):
        outfile = "{}out.xml".format(fol)
    else:
        outfile = "{}/out.xml".format(fol)

    tree = ET.parse(outfile)
    root = tree.getroot()
    
    for E in root.iter("totalEnergy"):
        energy = float(E.attrib["value"])

    try:
        return energy
    except:
        print("couldn't find totalE in {}".format(fol))

def get_xc_E(fol):
    if(fol[-1] == "/"):
        outfile = "{}out.xml".format(fol)
    else:
        outfile = "{}/out.xml".format(fol)

    tree = ET.parse(outfile)
    root = tree.getroot()
    
    for E in root.iter("chargeDenXCDenIntegral"):
        energy = float(E.attrib["value"])

    try:
        return energy
    except:
        print("couldn't find totalE in {}".format(fol))

def get_XCs(fol):
    folders = glob("{}/scale=*/".format(fol))
    scales = np.array([float(fol.split("=")[-1][:-1]) for fol in folders])
    Es     = np.array([get_xc_E(fol) for fol in folders])

    sort = np.argsort(scales)
    scales = scales[sort]
    Es     = Es[sort]

    return scales, Es


def get_EOS(fol):
    folders = glob("{}/scale=*/".format(fol))
    scales = np.array([float(fol.split("=")[-1][:-1]) for fol in folders])
    Es     = np.array([get_totalE(fol) for fol in folders])

    sort = np.argsort(scales)
    scales = scales[sort]
    Es     = Es[sort]

    return scales, Es


def fit_poly_and_min(scale, E):
    try:
        p    = np.polyfit(scale, E, 2)
    except Exception as ex:
        print("Fit failed: ")
        print("E     = {}".format(E))
        print("scale = {}".format(scale))
        print(ex)
        sys.exit("failed polyfit")
    dp   = np.polyder(p)
    mini = np.roots(dp)

    return p, mini

def get_bravis_mtx(inpfile):
    tree = ET.parse(inpfile)
    root = tree.getroot()


    for bravM in root.iter("bravaisMatrix"):
        M = np.zeros((3,3))
        for i, row in enumerate(bravM):
            nums = row.text.split()
            for j, n in enumerate(nums):
                M[i,j] = float(n)
        return M

    return None

def plot_EOS(ax):
    for c_num_cont, fol in enumerate(sys.argv[1:]):
        c_num = c_num_cont % 8
        M = get_bravis_mtx("{}/inp.xml".format(fol))
        if(M is not None):
            latt_scale = np.max(M)
        else:
            latt_scale = 1.0

        scale, Es = get_EOS(fol)
        angstr_fac = 2.0 * latt_scale * 0.529177211
        angstr = scale * angstr_fac

        poly, mini = fit_poly_and_min(scale, Es)
        mini=mini[0]

        print("\n{:>15} ||  scale min = {:8.6f}".format(fol, mini))
        if(M is not None):
            print("{:>15} ||  Amin      = {:8.6f}".format(fol, mini*angstr_fac))

        xs = np.linspace(np.min(scale), np.max(scale), 300)
        Ep = np.polyval(poly, xs)

        Es -= np.min(Ep)
        Ep -= np.min(Ep)
        
        if("inbuild" in fol or "LO" in fol or "cut_0.0" in fol):
            ax.plot(xs, Ep, 'C{}-.'.format(c_num),lw=3, label='{} = {:8.6f}'.format(fol, mini))
        else:
            ax.plot(xs, Ep, 'C{}'.format(c_num), label='{} = {:8.6f}'.format(fol, mini))


        if("inbuild" in fol or "LO" in fol or "cut_0.0" in fol):
            ax.plot(scale, Es, 'C{}.'.format(c_num), label=f"{fol} data")
        else:
            ax.plot(scale, Es, 'C{}s'.format(c_num), label=f"{fol} data")
        if(mini < np.max(scale) and mini > np.min(scale)):
            ax.axvline(mini, color='C{}'.format(c_num))

    ax.set_xlabel("scale")
    ax.set_ylabel("E in Hartree")
    ax.legend()

    if(M is not None):
        s_min, s_max = ax.get_xlim()
        A_min = s_min * angstr_fac
        A_max = s_max * angstr_fac

        clone = ax.twiny()
        clone.set_xlim(s_min, s_max)
        ax.set_title(os.getcwd())

def plot_xc(ax):
    for c_num, fol in enumerate(sys.argv[1:]):
        scale, exc = get_XCs(fol)
        exc -= np.min(exc)
        if("cut_0.0" in fol):
            print("using dashed")
            ax.plot(scale, exc, f'C{c_num}.--', label=f'{fol}')
        else:
            ax.plot(scale, exc, f'C{c_num}.-', label=f'{fol}')
        ax.legend()


f, ax1 = plt.subplots(1,1, figsize=(8,6))

plot_EOS(ax1)
#plot_xc(ax2)

plt.savefig("EOS.pdf")
plt.show()
