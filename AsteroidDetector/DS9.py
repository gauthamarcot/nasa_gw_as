__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module for displaying the asteroids in DS9 via pyds9, conformation, and report building
"""

import pyds9
import pickle
import glob
from datetime import datetime
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u
import os
from AstToolBox import solve_residuals, id_generator, clean_coords, find_desig, yes_no, score_rock
import pyperclip
import math
from tkinter import ttk
from tkinter import *

#GET CONFIG FILE
root_path = os.path.dirname(os.path.realpath(__file__))

"""
Example measurement to recreate
     DR0212  KC2018 01 14.18409405 28 41.14 +37 20 53.7          19.7 G      V03

Data structure in asteroid object
                         1         2        3          4           5
 cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
"""



def launch_ds9(dir, tree, overwrite):

    #LOAD CONFIG
    try:
        with open(root_path + "/obsconfig.txt", "r") as obsf:
            for line in obsf:
                if "Observatory Code" in line:
                    obscode = line.split(":")[-1].strip()
                if "Name" in line:
                    obsname = line.split(":")[-1].strip()
                if "Observer" in line:
                    observer = line.split(":")[-1].strip()
                if "Measurer" in line:
                    measurer = line.split(":")[-1].strip()
                if "Telescope" in line:
                    telescope = line.split(":")[-1].strip()
                if "Email" in line:
                    email = line.split(":")[-1].strip()
                if "Initials" in line:
                    initials = line.split(":")[-1].strip()
                if "DS9 Text Color" in line:
                    ds9Color = line.split(":")[-1].strip()
                if "DS9 Font Size" in line:
                    ds9FontSize = line.split(":")[-1].strip()
                if "Invert images?" in line:
                    invertImages = False
                    if line.split(":")[-1].strip() == "yes":
                        invertImages = True
                if "Blink Inverval" in line:
                    ds9BlinkInterval = line.split(":")[-1].strip()
    except:
        print("\nConfiguration file obsconfig.txt not found, exiting..\n")
        return

    try:
        with open (dir + '/asteroids', 'rb') as fp:
            asteroids = pickle.load(fp)

        with open (dir + '/midpoints', 'rb') as fp:
            midpoints = pickle.load(fp)

        with open(dir + '/totaltime', 'rb') as fp:
            totalTime = pickle.load(fp)

    except:
        print("\nAsteroids file or Midpoints file missing\n")
        return

    findDesig = True
    reportClosed = False

    ##### ADD REPORT DATE #####
    ut = Time(datetime.utcnow(), scale='utc')
    ut = str(ut)

    yymmdd = ut.split(" ")[0]
    hhmmss = ut.split(" ")[-1]
    yy = yymmdd.split("-")[0]
    mo = yymmdd.split("-")[1]
    dd = yymmdd.split("-")[2]
    hh = hhmmss.split(":")[0]
    mm = hhmmss.split(":")[1]
    ss = hhmmss.split(":")[2]
    ss = ss.split(".")[0]

    reportDate = yy+"."+mo+"."+dd+" "+hh+":"+mm+":"+ss

    #### CHECK FOR REPORT FILE AND ASK TO REPLACE? ###
    replacereport = overwrite

    if(replacereport):
        reportfile = open(dir + "/report.txt", "w")
        reportfile.write("COD "+obscode+"\n")
        reportfile.write("CON "+obsname+" ["+email+"]\n")
        reportfile.write("OBS "+observer+"\n")
        reportfile.write("MEA "+measurer+"\n")
        reportfile.write("TEL "+telescope+"\n")
        reportfile.write("ACK MPCReport file updated "+reportDate+"\n") #ADD UTC DATE TIME
        reportfile.write("AC2 "+email+"\n")
        reportfile.write("NET Gaia DR1\n")

    #Output to user
    print("\nLaunching DS9 to confirm asteroids..\nAnswer y or n\n")

    #Initiate DS9
    d = pyds9.DS9(target='DS9:*', start=True, wait=15, verify=False)

    #Clear out any previous runs in DS9
    d.set("blink no")
    d.set("frame delete all")

    fitsfiles = glob.glob(dir + "/*.fits")

    #Check for only "Stack" fits
    for file in fitsfiles:
        if "Stack" in file:
            continue
        else:
            fitsfiles.remove(file)

    #Sort by name
    fitsfiles.sort()

    #Load frames into DS9
    for i in range(len(fitsfiles)):
        #print(fitsfiles[i])
        d.set("frame "+str(i+1))
        d.set("fits " + fitsfiles[i])
        if(invertImages):
            d.set("cmap invert yes")


    #set locks and scale
    d.set("scale squared")
    d.set("scale zscale")
    d.set("scale match yes")
    d.set("frame lock wcs")
    d.set("lock colorbar yes")
    d.set("lock scalelimits yes")
    d.set("blink interval "+ ds9BlinkInterval)
    d.set("zoom 4")

    astnum = 0
    astLength = len(asteroids)

    def close_out():
        print("\nFinished processing asteroids for this sequence.\n")
        if(replacereport):
            reportfile.write("----- end -----")
            reportfile.close()
        d.set("blink no")
        #tree.destroy()
        # CLEAR OUT TREE
        tree.delete(*tree.get_children())

    #for asteroid in asteroids:
    def show_asteroid(event):

        curItem = tree.focus()

        if tree.item(curItem)["text"]=="END":
                print("Enter to close sequence")
                d.set("blink no")
                return

        astindex = int(tree.item(curItem)["text"])
        asteroid = asteroids[astindex]


        print("Asteroid ",astindex+1,"/", astLength)

        def displayAst(ast):
            d.set("blink no")
            if ast[0][0] == 'dummy':
                d.set("frame 1")
                d.set("regions delete all")
                #pass
            else:
                d.set("frame 1")
                d.set("regions delete all")
                d.set('regions','image; circle('+ast[0][4]+' '+ast[0][5]+' 9")# color='+ds9Color+' font="times'+ds9FontSize+'" text={'+ast[0][2]+'V ' +ast[0][3]+' FWHM }')

            d.set("frame 2")
            d.set("regions delete all")
            d.set('regions','image; circle('+ast[1][4]+' '+ast[1][5]+' 9")# color='+ds9Color+' font="times'+ds9FontSize+'" text={'+ast[1][2]+'V ' +ast[1][3]+' FWHM }')
            d.set("frame 3")
            d.set("regions delete all")
            d.set('regions','image; circle('+ast[2][4]+' '+ast[2][5]+' 9")# color='+ds9Color+' font="times'+ds9FontSize+'" text={'+ast[2][2]+'V ' +ast[2][3]+' FWHM }')

            if ast[3][0] == 'dummy':
                d.set("frame 4")
                d.set("regions delete all")
                #pass
            else:
                d.set("frame 4")
                d.set("regions delete all")
                d.set('regions','image; circle('+ast[3][4]+' '+ast[3][5]+' 9")# color='+ds9Color+' font="times'+ds9FontSize+'" text={'+ast[3][2]+'V ' +ast[3][3]+' FWHM }')

            d.set("pan to "+str(ast[1][0])+' '+str(ast[1][1])+" wcs")
            #d.set("regions save foo.reg")
            #print(d.get('regions'))
            d.set("blink yes")


        ### INITIAL DISPLAY ###
        displayAst(asteroid)

        ### DISPLAY 1-3 or 2-4 ###
        if asteroid[0][0] == 'dummy':
            print("Images 2-4")
        elif asteroid[3][0] =="dummy":
            print("Images 1-3")
        else:
            print("Images 1-4")

        ### SHOW LOCATION ####
        dispRA = asteroid[1][0]
        dispDEC = asteroid[1][1]
        dispT = SkyCoord(ra=dispRA * u.degree, dec=dispDEC * u.degree)
        dispcoordsT = dispT.to_string('hmsdms')
        dispCOORDS = clean_coords(dispcoordsT)
        print("Location: ", dispCOORDS," Copied to Clipboard")
        pyperclip.copy(dispCOORDS)

        print("\n")
        #print("Resid: ",asteroid[4][0] )
        #ENTER Q/A RESP

    ## CONFIM WITH ENTER

    def just_desig(event):

        curItem = tree.focus()

        if tree.item(curItem)["text"]=="END":
                close_out()
                return

        astindex = int(tree.item(curItem)["text"])
        asteroid = asteroids[astindex]

        print("Asteroid ",astindex+1,"/", astLength)
        print("\n")

        if astindex == astLength + 1:
            print("\n close out")
            return

        #print("Resid: ",asteroid[4][0] )
        #ENTER Q/A RESP

        #DESIG IS SET HERE FIRST
        desig = "TMP001"
                                # AST       #PLOT  #CONFIRM
        resids = solve_residuals(asteroid, False, True)
        resids = "{:.2f}".format(resids)
        print("\n", resids, " Asteroid mean residual")

        #Temp file for scoring asteroids
        tempfile = open(dir + "/digest2temp.txt", "w")

        raT = asteroid[1][0]
        decT = asteroid[1][1]
        magT = round(float(asteroid[1][2]), 1)
        magT = str(magT)+" V"

        cT = SkyCoord(ra=raT * u.degree, dec=decT * u.degree)
        coordsT = cT.to_string('hmsdms')
        coordsCleanT = clean_coords(coordsT)

        # Get designation of first measurement, parse MPC
        if (findDesig):
            # Only need 1 pos to search for desig
            obsT = "     " + desig + "  KC" + midpoints[1] + coordsCleanT + "          " + magT + "      " + obscode
            # find designation
            solveddesig = find_desig(obsT)
            print("Information for " + desig)
            print("##########################################")
            print("#####    MPC SEARCH RESULTS BELOW    #####")
            print("##########################################")
            print("\n", solveddesig)

            if(solveddesig is not None):
                desig = solveddesig.split()[1]
                print("MPC desig: ", desig+"\n")
            else:
                print("No MPC designation found.\n")


        for i in range(len(asteroid)):
            #convert radec
            if asteroid[i][0]=='dummy':
                continue

            ra = asteroid[i][0]
            dec = asteroid[i][1]
            mag = round(float(asteroid[i][2]), 1)

            #Catch bad mags
            if(mag>21.2):
                mag = "      "
            else:
                mag = str(mag)+" V"

            c = SkyCoord(ra=ra * u.degree, dec=dec * u.degree)
            coords = c.to_string('hmsdms')
            coordsClean = clean_coords(coords)


            desig = desig.rjust(11)
            blankSP="  "

            tempfile.write(desig+blankSP+"KC"+midpoints[i]+coordsClean+"          "+mag+ "      "+obscode+"\n")

        tempfile.close()
        #Score the rock and print out
        score_rock(dir)
        print("\n Finished searching and scoring object. \n")


    def confirm_asteroid(event):

        curItem = tree.focus()

        if tree.item(curItem)["text"]=="END":
                close_out()
                return

        astindex = int(tree.item(curItem)["text"])
        asteroid = asteroids[astindex]

        print("Asteroid ",astindex+1,"/", astLength)
        print("\n")

        if astindex == astLength + 1:
            print("\n close out")
            return

        #print("Resid: ",asteroid[4][0] )
        #ENTER Q/A RESP

        #DESIG IS SET HERE FIRST
        desig = "TMP001"
        desigFromMPC = False
                                # AST       #PLOT  #CONFIRM
        resids = solve_residuals(asteroid, False, True)
        resids = "{:.2f}".format(resids)
        print("\n", resids, " Asteroid mean residual")

        #Temp file for scoring asteroids
        tempfile = open(dir + "/digest2temp.txt", "w")

        raT = asteroid[1][0]
        decT = asteroid[1][1]
        magT = round(float(asteroid[1][2]), 1)
        magT = str(magT)+" V"

        cT = SkyCoord(ra=raT * u.degree, dec=decT * u.degree)
        coordsT = cT.to_string('hmsdms')
        coordsCleanT = clean_coords(coordsT)

        # Get designation of first measurement, parse MPC
        if (findDesig):
            # Only need 1 pos to search for desig
            obsT = "     " + desig + "  KC" + midpoints[1] + coordsCleanT + "          " + magT + "      " + obscode
            # find designation
            solveddesig = find_desig(obsT)
            print("Information for " + desig)
            print("##########################################")
            print("#####    MPC SEARCH RESULTS BELOW    #####")
            print("##########################################")
            print("\n", solveddesig)

            if(solveddesig is not None):
                useMPCdesig = True

                if(useMPCdesig):
                    desig = solveddesig.split()[1]
                    print("Assigned MPC desig: ", desig+"\n")
                    desigFromMPC = True
            else:
                print("No MPC designation found.")


        #OVERWRITE REPORT?
        if(replacereport and not desigFromMPC):
            desig = id_generator()
            print("Assigned temp designation: " + desig+"\n")

        for i in range(len(asteroid)):
            #convert radec
            if asteroid[i][0]=='dummy':
                continue

            ra = asteroid[i][0]
            dec = asteroid[i][1]
            mag = round(float(asteroid[i][2]), 1)

            #Catch bad mags
            if(mag>21.2):
                mag = "      "
            else:
                mag = str(mag)+" V"

            c = SkyCoord(ra=ra * u.degree, dec=dec * u.degree)
            coords = c.to_string('hmsdms')
            coordsClean = clean_coords(coords)

            if(desigFromMPC):
                #Capture provisional designation
                if len(desig) == 7:
                    desig = desig.rjust(12)
                    blankSP = " "
                if len(desig)<7:
                    blankSP="  "
                    desig = desig.ljust(11)
            else:
                desig = desig.rjust(11)
                blankSP="  "
            # IF WE REPLACE REPORT
            if (replacereport):
                reportfile.write(desig+blankSP+"KC"+midpoints[i]+coordsClean+"          "+mag+ "      "+obscode+"\n")

            tempfile.write(desig+blankSP+"KC"+midpoints[i]+coordsClean+"          "+mag+ "      "+obscode+"\n")

        tempfile.close()
        #Score the rock and print out
        score_rock(dir)
        print("\n Finished processing object. \n")


    #CLEAR OUT TREE
    tree.delete(*tree.get_children())

    # TREE COLUMNS CREATE
    # tree.config(columns=('fwhm','astloc','astresid', 'astmag'))
    tree['columns'] = ('fwhm', 'astloc', 'astresid', 'astmag', 'velocity')

    tree.column('#0', width=70)
    tree.column('fwhm', width=70, anchor='center')
    tree.column('astloc', width=180, anchor='center')
    tree.column('astresid', width=70, anchor='center')
    tree.column('astmag', width=70, anchor='center')
    tree.column('velocity', width=150, anchor='center')

    tree.heading('#0', text='Ast Num')
    tree.heading('fwhm', text='Ast FWHM')
    tree.heading('astloc', text='Ast Location')
    tree.heading('astresid', text='Ast Resid')
    tree.heading('astmag', text='Ast Mag')
    tree.heading('velocity', text='Ast Vel Arcsec/min')

    tree.config(selectmode = 'browse')

    tree.bind('<<TreeviewSelect>>', show_asteroid)
    tree.bind("<Return>", confirm_asteroid)
    tree.bind("<c>", just_desig)

    astnum2 = 0

    #Convert total time to float
    totalTime = float(totalTime)


    for ast in asteroids:

        astT = []

        #REMOVE DUMMY
        for k in range(len(ast)):
            if ast[k][0] == "dummy":
                continue
            else:
                astT.append(ast[k])

        #SOLVE AVE FWHM
        fwhm = sum(float(astT[i][3]) for i in range(len(astT)))/len(astT)
        fwhm = round(fwhm,2)

        #SOLVE AVE MAG
        mag = sum(float(astT[i][2]) for i in range(len(astT))) / len(astT)
        mag = round(mag, 2)

        #SOLVE RESID
        resid = solve_residuals(astT, False, False)

        ### SHOW LOCATION ####
        ra = astT[2][0]
        dec = astT[2][1]

        dispT = SkyCoord(ra=ra * u.degree, dec=dec * u.degree)
        dispcoordsT = dispT.to_string('hmsdms')
        dispCOORDS = clean_coords(dispcoordsT)

        #### SOLVE SPEED ####
        x1 = astT[0][0]
        y1 = astT[0][1]
        x2 = astT[-1][0]
        y2 = astT[-1][1]

        astDist = math.sqrt( (x2-x1)**2+ (y2-y1)**2)
        astDist = astDist * 3600 # CONVERT TO ARCSEC
        vel = round(astDist / totalTime,2)

        #  parent  id     name             text                   #fwhm   #loc   #resid  #mag
        tree.insert('', str(astnum2), text=str(astnum2), values=(fwhm, dispCOORDS, resid, mag, vel))
        astnum2 += 1

        #INSERT END LINE
        if astnum2 == len(asteroids):
            tree.insert('',str(len(asteroids)+1),text="END")

    tree.update()

#MODULE TESTING PURPOSES, UNCOMMENT
# myTree = Toplevel()
# tree1 = ttk.Treeview(myTree)
# tree1.pack(fill="both")

#launch_ds9("/home/david/Desktop/C4", tree1, False)