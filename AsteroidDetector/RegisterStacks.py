__author__ = 'David Rankin, David@rankinstudio.com'

"""
Image registration module.
"""

import os
import glob
import subprocess
import shlex
from CalibrateFits import calibrate_fits
from AstToolBox import natural_sort

def register_stacks(dir, subBack):

    root_path = os.path.dirname(os.path.realpath(__file__))

    try:
        with open(root_path + "/obsconfig.txt", "r") as obsf:
            for line in obsf:
                if "PP Path" in line:
                    ppPath = line.split(":")[-1].strip()
                if "PP Register Command" in line:
                    ppreg_command = line.split(":")[-1].strip()
                if "PP Photometry Command" in line:
                    ppphot_command = line.split(":")[-1].strip()
                if "PP Calibrate Command" in line:
                    ppcal_command = line.split(":")[-1].strip()
    except:
        print("\nConfiguration file obsconfig.txt not found, exiting..\n")
        return

    fits = glob.glob(dir + "/*.fits")

    fits = natural_sort(fits)
    os.chdir(dir)

    imgs = ""
    fitsf2 = []

    stacksFound = 0

    for file in fits:
        if "Stack" in file:
            stacksFound += 1
            img = file.split('/')[-1]
            print(img)
            fitsf2.append(file)
            imgs = imgs + img + " "

    if stacksFound < 4:
        print("Not enough stacks, images register correctly?")
        return "Error"

   ########################### REENABLE #############################
    if(subBack):
        print("\nPerforming background calibrations..\n")
        for imagefile in fitsf2:
            calibrate_fits('stack',"None",imagefile)


    ppprep_commandF = "pp_prepare " + imgs
    ppreg_commandF = ppreg_command +" " + imgs
    ppphot_commandF = ppphot_command+ " " + imgs #minarea 3 snr 1.8
    ppcal_commandF = ppcal_command+" " + imgs

    my_env = os.environ.copy()
    my_env["PATH"] = "" + ppPath + ":" + my_env["PATH"]
    my_env["PHOTPIPEDIR"] = ppPath

    print("Registering Stacks ... \n")

    prep = subprocess.Popen(shlex.split(ppprep_commandF), env=my_env)
    prep.wait()

    prepare = subprocess.Popen(shlex.split(ppreg_commandF), env=my_env)
    prepare.wait()

    phot = subprocess.Popen(shlex.split(ppphot_commandF), env=my_env)
    phot.wait()

    cal = subprocess.Popen(shlex.split(ppcal_commandF), env=my_env)
    cal.wait()

    print("\nDone registering image stacks, now search for asteroids.\n")
    return "\nDone registering stacks, now search for asteroids.\n"

#dir = "/home/david/Desktop/C4-7"
#register_stacks(dir, True)
