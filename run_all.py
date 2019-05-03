#!/Local/tmp/bin/anaconda3/bin/ipython3
import subprocess as sp
import sys
import os
from termcolor import colored

def run_fleur():
    fleur = '/Users/redies/fleur/build/fleur_MPI'
    ret_code = sp.call([fleur, "-trace"])
    print("ret_code = {}".format(ret_code))

head_fol = os.getcwd()

for fol in sys.argv[1:]:
    print(colored("Running {}".format(fol), 'green' ))
    os.chdir(fol)
    run_fleur()
    os.chdir(head_fol)
    
