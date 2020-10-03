__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module for displaying all extracted asteroids. Not tied to GUI. Run manually by uncommenting last line
"""

import pyds9
import pickle
import glob
import numpy as np

def display_asteroids(dir):

    d = pyds9.DS9(target='DS9:*', start=True, wait=10, verify=True)

    np.set_printoptions(suppress=True)

    #Clear out any previous runs in DS9
    d.set("blink no")
    d.set("frame delete all")

    # dir = "/home/david/Desktop/2.8.18/T3/"
    keep = False

    with open (dir + '/asteroids', 'rb') as fp:
        asteroids = pickle.load(fp)

    fitsfiles = glob.glob(dir + "/*.fits")
    for file in fitsfiles:
        if "Stack" in file:
            continue
        else:
            fitsfiles.remove(file)
    fitsfiles.sort()

    #load frames into ds9
    for i in range(len(fitsfiles)):
        print(fitsfiles[i])
        d.set("frame "+str(i+1))
        d.set("fits " + fitsfiles[i])

    #set locks and scale
    d.set("scale squared")
    d.set("scale zscale")
    d.set("scale match yes")
    d.set("frame lock wcs")
    #d.set("scale mode 99.5")
    d.set("blink interval .3")
    d.set("zoom 4")

    #cur = conn.cursor()  # 0         1         2        3          4           5
    #cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
    d.set("frame 1")
    for ast in asteroids:
        if ast[0][0] == 'dummy':
            continue
        d.set('regions','image; circle('+ast[0][4]+' '+ast[0][5]+' 5")')
    d.set("frame 2")
    for ast in asteroids:
        d.set('regions','image; circle(' + ast[1][4] + ' ' + ast[1][5] + ' 5")')
    d.set("frame 3")
    for ast in asteroids:
        d.set('regions','image; circle(' + ast[2][4] + ' ' + ast[2][5] + ' 5")')
    d.set("frame 4")
    for ast in asteroids:
        if ast[3][0] == 'dummy':
            continue
        d.set('regions','image; circle('+ast[3][4]+' '+ast[3][5]+' 5")')


    d.set("blink yes")

#display_asteroids("/home/david/Desktop/T4Sorted")