__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module built wiht numpy for extracting non moving objects from the images extracted from the .db files to
find suspected transients.
"""

import numpy as np
from AstToolBox import sec2deg

"""
Subtract non moving objects from the database files and return transient objects to ReadDB.py

Data structure in asteroid object
                         0          1       2       3           4           5
 cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
"""

def findstars(images, star_search_radius, star_lim_mag, fwhm_min):

    matches1 = []
    matches2 = []
    matches3 = []
    matches4 = []

    transients1 = []
    transients2 = []
    transients3 = []
    transients4 = []

    """
        star_search_radius is passed in arcsec

        Remove stars from each array with position precision of 2 arc seconds
        4th decimal place in decimal degrees is 1 are sec precision
        allimages
            - Image 0
                Image 0 data
            -image 1
                Image 1 data
            ect

        matches[]
            - Image 1 matches to 2
            - Image 1 matches to 3
            - Image 1 matches to 4
    """

    #NP Options
    np.set_printoptions(suppress=True)

    #Convert each image to numpy float arrays
    image1 = np.array(images[0], dtype=np.float)
    image2 = np.array(images[1], dtype=np.float)
    image3 = np.array(images[2], dtype=np.float)
    image4 = np.array(images[3], dtype=np.float)

    #Set Ref Images based on Star Magnitude. Limit number of stars
    print(star_lim_mag, " Limiting star magnitude")
    reference1 = image1[image1[:, 2] < star_lim_mag]
    reference2 = image2[image2[:, 2] < star_lim_mag]

    #Convert star search radius from arcsec to deg
    star_search_deg = round(sec2deg(star_search_radius),8)
    print (str(star_search_deg) + " Star search radius in degrees\nSubtracting non-moving objects, please wait ...\n")
    star_search_calc = star_search_deg**2 #Squared before conversion?


    #Sub image 2 from 1
    for ra1, dec1, mag1, *dummy1 in image1:
            ra2, dec2, mag2, *dummy2 = reference2.T
            indices = (ra2-ra1)**2 + (dec2-dec1)**2 <= star_search_calc
            matches1.append(reference2[indices])

    #Sub image 1 from 2
    for ra1, dec1, mag1, *dummy1 in image2:
            ra2, dec2, mag2, *dummy2 = reference1.T
            indices = (ra2-ra1)**2 + (dec2-dec1)**2 <= star_search_calc
            matches2.append(reference1[indices])

    #Sub image 3 from 1
    for ra1, dec1, mag1, *dummy1 in image3:
            ra2, dec2, mag2, *dummy2 = reference1.T
            indices = (ra2-ra1)**2 + (dec2-dec1)**2 <= star_search_calc
            matches3.append(reference1[indices])

    #Sub imag4 from  1
    for ra1, dec1, mag1, *dummy1 in image4:
            ra2, dec2, mag2, *dummy2 = reference1.T
            indices = (ra2-ra1)**2 + (dec2-dec1)**2 <= star_search_calc
            matches4.append(reference1[indices])

    #Exract transients from matches
    for x in range(len(image1)):
        if np.any(matches1[x]):
            continue
        else:
            transients1.append(images[0][x])

    for x in range(len(image2)):
        if np.any(matches2[x]):
            continue
        else:
            transients2.append(images[1][x])

    for x in range(len(image3)):
        if np.any(matches3[x]):
            continue
        else:
            transients3.append(images[2][x])

    for x in range(len(image4)):
        if np.any(matches4[x]):
            continue
        else:
            transients4.append(images[3][x])

    print(len(transients1), "Transients in stack1")
    print(len(transients2), "Transients in stack2")
    print(len(transients3), "Transients in stack3")
    print(len(transients4), "Transients in stack4")

    print("\nDone finding matching stars..\n")


    return transients1, transients2, transients3, transients4
