__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module for troubleshooting extraction with PP
"""

import pyds9
import pickle
import glob
import numpy as np

def display_stars(dir, img):

    d = pyds9.DS9(target='DS9:*', start=True, wait=10, verify=True)

    np.set_printoptions(suppress=True)

    #Clear out any previous runs in DS9
    d.set("scale squared")
    d.set("scale zscale")
    d.set("scale match yes")
    d.set("frame lock wcs")
    d.set("lock colorbar yes")
    d.set("lock scalelimits yes")
    d.set("blink no")
    d.set("frame delete all")

    imgF = "img"+str(img)


    with open (dir + '/'+imgF, 'rb') as fp:
        imgShow = pickle.load(fp)

    print("Displaying extracted objects: " + str(len(imgShow)))

    fitsfile = dir + "/Stack"+str(img)+".fits"

    d.set("frame "+str(img))
    d.set("fits " + fitsfile)

    #set locks and scale
    d.set("scale squared")
    d.set("scale zscale")
    d.set("scale match yes")
    d.set("frame lock wcs")

    #cur = conn.cursor()  # 0         1         2        3          4           5
    #cur.execute("SELECT `ra.deg`, `dec.deg`, _Vmag, FWHM_IMAGE, XWIN_IMAGE, YWIN_IMAGE FROM data")
    for t in range(len(imgShow)):
        d.set('regions','image; circle('+imgShow[t][4]+' '+imgShow[t][5]+' 8")# text={'+imgShow[t][2]+'V }' )


#display_stars("/home/david/Desktop/C4", 3)