__author__ = 'David Rankin, David@rankinstudio.com'

"""
MPC SkyCov report module
"""

from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
import glob

"""
NEO SEARCH FIELD CENTERS
SOURCE: V03
DATE: 20180113
FIELD SIZE RA: 0.84
FIELD SIZE DEC: 0.63
LIMITING MAGNITUDE: 20
FILENAME: 01.13.2018
139.6730, 61.3653, 0.84, 0.63, 20
80.9164, 39.8092, 0.84, 0.63, 20
81.7255, 38.7690, 0.84, 0.63, 20
"""

def getDate(file):
    data, header = fits.getdata(file, header=True)

    hdu_number = 0
    fits.getheader(file, hdu_number)

    fitsDate = header['DATE-OBS']
    fitsDate = fitsDate.split('-')

    fitsYY = fitsDate[0]
    fitsMM = fitsDate[1]
    fitsDD = fitsDate[2]
    fitsDD = fitsDD.split('T')[0]
    return fitsYY, fitsMM, fitsDD

def getCoords(file):
    #GET THE LOCATION COORDINATES FROM FITS HEADER
    data, header = fits.getdata(file, header=True)

    hdu_number = 0
    fits.getheader(file, hdu_number)

    rast = str(header['OBJCTRA'])
    decst = str(header['OBJCTDEC'])

    c = SkyCoord(rast+' '+decst, unit=(u.hourangle, u.deg))

    ra = c.ra.degree
    dec = c.dec.degree

    ra = "%.4f" % ra
    dec = "%.4f" % dec

    return ra, dec


def generageCovReport(dir):
    #GET FILES

    source = "V03"
    camresX = "0.84"
    camresY = "0.63"
    limmag = "19.5"

    folders = glob.glob(dir+"/*/")
    folders.sort()

    filenum = 0

    for folder in folders:
        filenum += 1

        fitsfile = folder + "Stack1.fits"
        ra, dec = getCoords(fitsfile)

        if filenum == 1:
            YY, MM, DD = getDate(fitsfile)
            fitsDateFileName = MM + "." + DD + "." + YY
            f = open(dir+ 'SkyCovReport ' + fitsDateFileName + '.txt', 'w')  # CREATE MATCHING KML FILE NAME
            f.write("NEO SEARCH FIELD CENTERS\n")
            f.write("SOURCE: " + source + "\n")
            f.write("DATE: " + YY + MM + DD + "\n")  # YYYY MM DD
            f.write("FIELD SIZE RA: " + camresX + "\n")
            f.write("FIELD SIZE DEC: " + camresY + "\n")
            f.write("LIMITING MAGNITUDE: " + limmag + "\n")
            f.write("FILENAME: " + fitsDateFileName + "\n")

        ra = str(ra)
        dec = str(dec)

        f.write(ra+", " +dec+", "+camresX+", "+camresY+", "+limmag + "\n")

    f.close()

    print("SkyCov report completed")

    return

#generageCovReport("/home/david/Desktop/20180928/")
