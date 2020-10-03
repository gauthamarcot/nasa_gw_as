__author__ = 'David Rankin, David@rankinstudio.com'

"""
Asteroid extraction from DB files.
This module uses time based vectors to predict the 3rd and 4th hit after two objects are extracted
matching the star search and asteroid search parameters. It needs to be rewritten in numpy to speed
it up.
"""

import pickle
import os
from AstToolBox import solve_residuals, sec2deg
import numpy as np
import matplotlib.pyplot as plt


"""
Data structure in asteroid object
                         0          1       2       3           4           5
 cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
"""

def find_asteroids(dir, star_search_rad, fwhm_min, ast_search_rad, astmatch, req4):

    print("Require 4 is: ", req4)

    root_path = os.path.dirname(os.path.realpath(__file__))

    try:
        with open(root_path + "/obsconfig.txt", "r") as obsf:
            for line in obsf:
                if "Max Resid" in line:
                    maxResid = float(line.split(":")[-1].strip())
                if "Slop Factor" in line:
                    slopFactor = float(line.split(":")[-1].strip())
        obsf.close()

    except:
        print("\nConfiguration file obsconfig.txt not found, exiting..\n")
        return


    asteroids = []
    asteroids1 = []
    asteroids2 = []
    removefrom2=[]
    asteroids2_final=[]
    astmatch = 0

    if (os.path.isfile(dir + "/asteroids")):
        os.remove(dir + "/asteroids")

    # Convert star search rad to degrees
    star_search_deg = round(sec2deg(star_search_rad)**2,8)

    # Convert star search radius from arcsec to deg, square it?
    ast_search_deg = round(sec2deg(ast_search_rad)**2, 8)

    # Convert slop factor to degrees
    slopFactor = round(sec2deg(slopFactor)**2, 8)

    ### POINT INSIDE CIRCLE WHERE D**2 <= R**2

    # print(slopFactor, " Slop factor degrees")
    # print(ast_search_deg, " Asteroid search radius in decimal degrees")
    # print(star_search_deg, " Star search radius in decimal degrees")


    if req4 == True:
        print("Require 4 hits ")

    try:
        with open(dir + '/t1', 'rb') as fp:
            t1 = pickle.load(fp)
        with open(dir + '/t2', 'rb') as fp:
            t2 = pickle.load(fp)
        with open(dir + '/t3', 'rb') as fp:
            t3 = pickle.load(fp)
        with open(dir + '/t4', 'rb') as fp:
            t4 = pickle.load(fp)
        with open(dir + '/timedeltas', 'rb') as fp:
            timeDeltas = pickle.load(fp)
        print(timeDeltas, " Time deltas")
    except:
        print("\nError loading transient or time delta files\n")
        return

    tDelta1 = timeDeltas[0]
    tDelta2 = timeDeltas[1]
    tDelta3 = timeDeltas[2]
    tDelta4 = timeDeltas[3]

    # CHECK MOVING OBJECTS 1 to 4
    print("\nSearching for asteroids images 1-3, and 1-4\n")
    for i in range(len(t1)):
        if float(t1[i][3]) < fwhm_min:
            continue
                        #ra1        #dec1
        pt1 = np.array([t1[i][0], t1[i][1]])

        for n in range(len(t2)):
            #CHECK MIN FWHM
            if float(t2[n][3]) < fwhm_min:
                continue
                            #Ra2        #Dec2
            pt2 = np.array([t2[n][0], t2[n][1]])

            dist2 = np.linalg.norm(pt2 - pt1)

            #First dist should only have checks for limits
            if dist2**2 <= ast_search_deg and dist2**2 >= star_search_deg:

                for x in range(len(t3)):
                    #CHECK MIN FWHM
                    if float(t3[x][3]) < fwhm_min:
                        continue

                    # Wighted average to find poitn 3, such that scale 0 = pt1, scale 1 = pt2, scale 2 = pt3
                    ave1 = 2 / tDelta2
                    scaleby = (tDelta3 * ave1)
                                    #ra3        #dec3

                    pt3 = np.array([t3[x][0], t3[x][1]])
                    #PREDITED POINT 3
                    pt3P = pt1 * (1 - scaleby) + pt2 * scaleby

                    dist3 = np.linalg.norm(pt3P - pt3)

                    if dist3**2 <= slopFactor: #Requires star search calc for radius search

                        astresid = solve_residuals([(pt1),(pt2),(pt3)], False, False)

                        #     MINUS HALF OF RESID SEARH FOR 3
                        if astresid <= maxResid:

                            astresid = "{:.2f}".format(astresid)
                            print(astresid, " Asteroid mean resid 1-3")

                            #WRITE OUT ASTEROID AFTER 3 HITS
                            astmatch += 1
                            asteroid = []
                            asteroid.append(t1[i])
                            asteroid.append(t2[n])
                            asteroid.append(t3[x])

                            #CEHCK FOR 4th HIT
                            for g in range(len(t4)):

                                if float(t4[g][3]) < fwhm_min:
                                    continue

                                ave2 = 3/tDelta3
                                scaleby2 = (tDelta4 * ave2)

                                pt4 = np.array([t4[g][0], t4[g][1]])
                                pt4P = pt1 * (1 - scaleby2) + pt2 * scaleby2

                                dist4 = np.linalg.norm(pt4 - pt4P)

                                if dist4**2 <= slopFactor * 1.5:

                                    astresid = solve_residuals([(pt1), (pt2), (pt3), (pt4)], False, False)

                                        # PLUS HALF OF SEARCH FOR 4
                                    if astresid <= maxResid:
                                        astresid = "{:.2f}".format(astresid)
                                        print(astresid, " Asteroid mean resid 1-4")
                                        asteroid.append(t4[g])
                                        #GO BACK TO PARENT LOOP
                                        if req4:
                                            asteroids1.append(asteroid)
                                        break

                            if not req4:
                                if(len(asteroid)<4):
                                    asteroid.append(["dummy"])

                                #asteroid.append([astresid, "some other stuff"])

                                #REGARDLESS OF 4th WRITE 3RD
                                asteroids1.append(asteroid)

    # CHECK MOVING OBJECTS 2 to 4
    if not req4:
        print("Searching for asteroids images 2-4\n")
        for i in range(len(t2)):
            # CHECK SIZE
            if float(t2[i][3]) < fwhm_min:
                continue

            pt2 = np.array([t2[i][0], t2[i][1]])

            # check against 1 for each in 2
            for n in range(len(t3)):
                # CHECK MIN FWHM
                if float(t3[n][3]) < fwhm_min:
                    continue
                pt3 = np.array([t3[n][0], t3[n][1]])

                dist2 = np.linalg.norm(pt3 - pt2)

                if dist2**2 <= ast_search_deg  and dist2**2 >= star_search_deg:

                    for x in range(len(t4)):
                        if float(t4[x][3]) < fwhm_min:
                            continue

                        ave = 2 / tDelta4
                        scaleby2 = (tDelta4 * ave)

                        pt4 = np.array([t4[x][0], t4[x][1]])
                        #PREDICTED
                        pt4P = pt2 * (1 - scaleby2) + pt3 * scaleby2

                        dist4 = np.linalg.norm(pt4 - pt4P)

                        if (dist4**2 <= slopFactor ):

                            residData = [(pt2),(pt3),(pt4)]
                            astresid = solve_residuals(residData, False, False)

                            if astresid <= maxResid:
                                astresid = "{:.2f}".format(astresid)
                                print(astresid, " Asteroid mean resid 2-4")

                                # WRITE OUT ASTEROID AFTER 3 HITS
                                astmatch += 1
                                asteroid = []
                                asteroid.append(["dummy"])
                                asteroid.append(t2[i])
                                asteroid.append(t3[n])
                                asteroid.append(t4[x])

                                # REGARDLESS OF 4th WRITE 3RD
                                asteroids2.append(asteroid)

                                #asteroid.append([astresid, "some other shit"])
                                #sys.stdout.write('\r' + str(astmatch) + " Asteroids Found\n")
                                break

    #Compare asteroids1 to asteroids2
    if not req4:
        print("\nRemoving duplicates between 1-4 and 2-4\n")
        for x in range(len(asteroids1)):
            #print("Asteroid1 ", asteroids1[x])
            ast1 = asteroids1[x][1] #Get second position
            pt1 = np.array([ast1[0],ast1[1]])

            for n in range(len(asteroids2)):
                ast2 = asteroids2[n][1] #Get second position
                pt2 = np.array([ast2[0], ast2[1]])

                if np.linalg.norm(pt1 - pt2) < star_search_deg*2:
                    try:
                        removefrom2.append(asteroids2[n])
                        break
                    except:
                        print("Error removing duplicate from 2-4")
                        break

        for asteroid in asteroids2:
            if asteroid in removefrom2:
                continue
            else:
                asteroids2_final.append(asteroid)

    asteroids.extend(asteroids1)

    if not req4:
        asteroids.extend(asteroids2_final)

    astmatch = len(asteroids)
    print("#########################################")
    print("##### ",len(asteroids), " Possible asteroids found  #####")
    print("#########################################\n")

    #Dump asteroids into current working dir
    with open(dir + '/asteroids', 'wb') as fp:
        pickle.dump(asteroids, fp)

    #Return num of asteroids found
    return astmatch

#MODULE TESTING PURPOSES UNCOMMENT
#find_asteroids("/home/david/Desktop/EXAMP/C10", 2.2, 1.7, 30, 0, True)
