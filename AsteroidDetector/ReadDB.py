__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module to extract the sources from the PP .db files, and subtract the stars using Numpy and
reference image built from the star lim mag feature after subtracting image 1 from 2, and 2 from 1.
"""

import sqlite3
from sqlite3 import Error
import glob
import math
from StarSubtract import findstars
import pickle
from decimal import *
from AstToolBox import deg2sec

def parse_db(dir, limmag, star_search_radius, fwhm_min, ast_search_rad, star_lim_mag):

    message = ""

    allimgs = []
    """
    If the center is at (x0,y0) and the radius is r, then
    1) if (x-x0)^2 + (y-y0)^2 < r^2, the point (x,y) is inside the circle,
    mag = zeropoint - 2.5*LOG10(ADU)
    """
    search_radius_arcsec = Decimal(round(deg2sec(star_search_radius),5))
    star_search_calc = Decimal(math.pow(search_radius_arcsec ,2))

    # Convert star search radius from arcsec to deg
    asteroid_search = Decimal(round(deg2sec(ast_search_rad), 5))
    ast_search_calc = Decimal(math.pow(asteroid_search, 2))

    def create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None


    def select_all_data(conn):

        try:

            cur = conn.cursor()   #0         1         2        3          4           5
            cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE, _e_Vmag FROM data")

            rows = cur.fetchall()

            i = 0

            alldata = []

            for row in rows:
                if row[2] < limmag:
                    objdata = []  # clear it out
                    objnum = i
                    objdata.append(row[0])  # RA
                    objdata.append(row[1]) # DEC
                    objdata.append(str(round(row[2],2))) # V Mag
                    objdata.append(str(round(row[3],2)))  # FWHM
                    objdata.append(str(row[4]))  # X
                    objdata.append(str(row[5]))  # Y
                    objdata.append(str(row[6]))  # e Vmag
                    objdata.append(objnum)  # NUMBER ID FOR LATER USE

                    alldata.append(objdata)
                    i += 1

            print("Stars / objects found: "+ str(len(alldata)) + "\n")

            return alldata

        except:
            print("\nError finding data, did images register correctly?\n")
            return


    def find_transients(all_images):

        #DUMP IMAGES
        with open(dir + '/img1', 'wb') as fp:
            pickle.dump(all_images[0], fp)
        with open(dir + '/img2', 'wb') as fp:
            pickle.dump(all_images[1], fp)
        with open(dir + '/img3', 'wb') as fp:
            pickle.dump(all_images[2], fp)
        with open(dir + '/img4', 'wb') as fp:
            pickle.dump(all_images[3], fp)

        #Find transients
        t1, t2, t3, t4 = findstars(allimgs, star_search_radius, star_lim_mag, fwhm_min)


        with open(dir + '/t1', 'wb') as fp:
            pickle.dump(t1, fp)

        with open(dir + '/t2', 'wb') as fp:
            pickle.dump(t2, fp)

        with open(dir + '/t3', 'wb') as fp:
            pickle.dump(t3, fp)

        with open(dir + '/t4', 'wb') as fp:
            pickle.dump(t4, fp)

        aveT = (len(t1) + len(t2) + len(t3) + len(t4)) / 4

        print("Average transients: "+ str(aveT))

        if aveT > 3500:
            print("warning, to many transients found, exiting...")
            return "Too many transients"
        else:
            return ""


    ############# THIS RUNS #######################
    #GET DB FILES
    dbfiles = glob.glob(dir + "/*.db")
    dbfiles.sort()

    allimgs = []

    if len(dbfiles) < 3:
        message =  "\nDatabase files not found \nDid you register images? \n"
        return message

    for file in dbfiles:
        print("Scanning database file: " + file.split("/")[-1])

        #define database files
        database = file

        # create a database connection
        conn = create_connection(database)

        #select data
        data = select_all_data(conn)

        allimgs.append(data)

    if message != "":
        print(message)
    else:
        transmessage = find_transients(allimgs)
        if transmessage != "":
            message = "Too many transients"
    return message

#parse_db(dir, limmag, star_search_radius, fwhm_min, ast_search_rad, star_lim_mag):
#parse_db("/home/david/Desktop/20180609/T12Sorted/", 20.5, 2, 1.5, 20, 21)
