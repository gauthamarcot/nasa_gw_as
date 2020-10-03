__author__ = 'David Rankin, David@rankinstudio.com'

"""
Various tools required by the other modules
"""

import numpy as np
from astropy.modeling.functional_models import Linear1D
from astropy.modeling.fitting import LevMarLSQFitter, LinearLSQFitter
from matplotlib import pyplot as plt
import warnings
import random
import string
import os, re
import requests
from bs4 import BeautifulSoup
import subprocess
import shlex
from decimal import *

warnings.filterwarnings('ignore', category=UserWarning, append=True)
#GET CONFIG FILE
root_path = os.path.dirname(os.path.realpath(__file__))


def deg2sec(arcsec):
    return Decimal(3600 * arcsec)

def sec2deg(arcsec):
    #3600arcsec per degree
    return 0.000277778 * arcsec

#SOLVE ASTEROID RESIDUALS
def solve_residuals(data, showplot, confirmreal):

    resids = []
    data2 = []

    def linear(x, slope=1, intercept=0):
        return slope * x + intercept

    for i in data:
        if i[0] == 'dummy':
            continue
        else:
            data2.append(i)

    data2 = np.array(data2, dtype=np.float)

    def degree_to_arcsec(degree):
        return  degree * 3600

    # AstroPy
    fitter1 = LevMarLSQFitter() # This will give "warning"
    l_init = Linear1D(slope=1, intercept=0) # default values
    l_fit1 = fitter1(l_init, data2[:,0], data2[:,1])

    residual_astropy = data2[:, 1] - l_fit1(data2[:, 0])

    #CONFIRMREAL COEMS FROM DS9 REQUEST
    if(confirmreal):
        print("\n###### RESIDUALS ######")
    #print("### RESIDUALS ###")
    for residual in residual_astropy:
        positive = False
        resids.append(abs(round(degree_to_arcsec(residual), 2)))
        if(confirmreal):
            dispresid= round(degree_to_arcsec(residual),2)
            if dispresid > 0:
                positive = True
            dispresid = "{:.2f}".format(dispresid)
            if(positive):
                dispresid = "+"+dispresid
            print(dispresid)

    meanResid = sum(resids) / float(len(resids))
    meanResid = round(meanResid, 2)

    if(showplot):
        plt.close()
        f, ax = plt.subplots(1, 1)

        ax.plot(data2[:, 0], data2[:, 1], 'r+')
        ax.plot(data2[:, 0], l_fit1(data2[:, 0]), 'r-')

        ax.set_xlabel('RA')
        ax.set_ylabel('DEC', color='r')
        ax.tick_params('y', colors='r')

        plt.tight_layout()
        plt.show(block=False)

    return meanResid



#CONVERT DATE OBS TO MPC FORMAT
def timeToMPC(time):

    #EX date needed: 2018 01 24.242712
    #EX date in: 2018-01-24 04: 30:55.114

    #Conversion ratios
    hoursinday = 1/24
    minutesinday = 1/1440
    secinday = 1/86400

    yymmdd = time.split("T")[0]
    hhmmss = time.split("T")[-1]

    yy = yymmdd.split("-")[0]
    mo = yymmdd.split("-")[1]
    dd = yymmdd.split("-")[2]

    hh = float(hhmmss.split(":")[0])
    mm = float(hhmmss.split(":")[1])
    ss = float(hhmmss.split(":")[2])

    decTime = round(hh * hoursinday + mm * minutesinday + ss * secinday, 6)

    #Format with trailing 0s if needed
    decTime = '%07.6f' % decTime

    finalTime = yy + " " + mo + " " + dd + "." + str(decTime).split(".")[-1]

    return finalTime


#GENERATE ID
def id_generator(size=4, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):

    newdesig = False

    desig = ''.join(random.choice(chars) for _ in range(size))
    desig = "DR"+desig

    #Check the current desig for a match
    with open(root_path + "/desigused.txt", "r") as ins:
        for line in ins:
            if desig in line:
                print(line, " Used!")
                newdesig = True

    if(newdesig):
        print("Desig already used, generating new..")
        id_generator()
    else:
        #Writing Designations
        desigfile = open(root_path+"/desigused.txt", "a")
        desigfile.write(desig + "\n")
        desigfile.close()
        return desig

#CLEAN COORDINATES FOR REPORT
def clean_coords(coords):
    #Format sent in
    #06h23m05.4041s +29d16m40.5865s

    hms = coords.split(" ")[0]
    dms = coords.split(" ")[-1]

    hms = hms.replace("h", " ")
    hms = hms.replace("m", " ")
    hms = hms.replace("s", "")

    dms = dms.replace("d", " ")
    dms = dms.replace("m", " ")
    dms = dms.replace("s", "")

    rahh = hms.split(" ")[0]
    ramm = hms.split(" ")[1]

    dechh = dms.split(" ")[0]
    decmm = dms.split(" ")[1]

    rass = round(float(hms.split(" ")[-1]), 2)
    rass = '%05.2f' % rass
    decss = round(float(dms.split(" ")[-1]), 2)
    decss = '%04.1f' % decss

    coordsClean = rahh+" "+ramm+" "+str(rass)+" "+dechh+" "+decmm+" "+str(decss)

    return coordsClean


#PARSE MPC
def find_desig(obs):

    print("\nSearching MPC, please wait..\n")

    url = "https://cgi.minorplanetcenter.net/cgi-bin/mpcheck.cgi?year=&month=&day=&ra=&decl=&which=obs&radius=1&limit=24.0&oc=&sort=d&mot=h&tmot=s&pdes=p&needed=f&ps=n&type=1&TextArea="+obs+""

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        respText = soup.pre.get_text()
        respText = respText.split("\n")
        Eph = re.compile(r'0.0\D\s*0.0\D')
        for line in respText:
            idObject = Eph.findall(line)
            if idObject != []:
                return line

    except:
        return "Error, could not parse MPC"

#YES AND NO
def yes_no(answer):
    # try:
    yes = set(['yes', 'y',])
    no = set(['no', 'n', ''])
    exit = set(['stop','exit', 'x'])
    prev = set(['p'])

    while True:
        choice = input(answer).lower()
        if choice is None:
            return False
        if choice in yes:
            return True
        if choice in no:
            return False
        if choice in exit:
            return "stop"
        else:
            print
            "Please respond with 'yes' or 'no'\n"

#SCORE ROCK
def score_rock(dir):
    if os.path.isfile(dir + "/digest2temp.txt"):
        score_command = "digest2 "+dir+"/digest2temp.txt"
        os.chdir((root_path+"/digest2"))
        my_env = os.environ.copy()
        my_env["PATH"] = root_path+"/digest2/:" + my_env["PATH"]
        print("############################################")
        print("#####    OBJECT PROBABILITIES BELOW    #####")
        print("############################################")
        score = subprocess.Popen(shlex.split(score_command), env=my_env)
        score.wait()

#BETTER SORTING
def natural_sort(arr):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(arr, key=alphanum_key)
