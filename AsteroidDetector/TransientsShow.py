__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module for troubleshooting, displays extracted transients.
"""

import pyds9
import pickle
import glob
import numpy as np

def display_transients(dir):
    d = pyds9.DS9(target='DS9:*', start=True, wait=10, verify=True)

    np.set_printoptions(suppress=True)

    #Clear out any previous runs in DS9
    d.set("blink no")
    d.set("frame delete all")

    # dir = "/home/david/Desktop/2.8.18/T3/"
    keep = False

    with open (dir + '/t1', 'rb') as fp:
        t1 = pickle.load(fp)

    with open (dir + '/t2', 'rb') as fp:
        t2 = pickle.load(fp)

    with open (dir + '/t3', 'rb') as fp:
        t3 = pickle.load(fp)

    with open (dir + '/t4', 'rb') as fp:
        t4 = pickle.load(fp)

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
    d.set("lock colorbar yes")
    d.set("lock scalelimits yes")
    #d.set("scale mode 99.5")
    d.set("blink interval .3")
    d.set("zoom 4")

    #cur = conn.cursor()  # 0         1         2        3          4           5
    #cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
    d.set("frame 1")
    for t in range(len(t1)):
        d.set('regions','image; circle('+t1[t][4]+' '+t1[t][5]+' '+t1[t][3]+'")')
    d.set("frame 2")
    for t in range(len(t2)):
        d.set('regions','image; circle('+t2[t][4]+' '+t2[t][5]+' '+t2[t][3]+'")')
    d.set("frame 3")
    for t in range(len(t3)):
        d.set('regions','image; circle('+t3[t][4]+' '+t3[t][5]+' '+t3[t][3]+'")')
    d.set("frame 4")
    for t in range(len(t4)):
        d.set('regions','image; circle('+t4[t][4]+' '+t4[t][5]+' '+t4[t][3]+'")')


    d.set("blink yes")

#display_transients("/home/david/Desktop/T7Sorted")