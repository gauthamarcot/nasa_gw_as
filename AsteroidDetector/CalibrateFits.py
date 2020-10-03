__author__ = 'David Rankin, David@rankinstudio.com'

"""
Module for background subtraction on images before running them through the pipeline
"""

from astropy.io import fits
from photutils import Background2D, MedianBackground

##type is single image or stack
def calibrate_fits(type,darkImg,imagefile):

    print("Stack type: ", type)

    if type == 'single':

        fn = imagefile

        with fits.open(fn, mode='update') as hdul:

            image = hdul[0]

            print("Single mode background subtraction on ", fn.split("/")[-1])

            bkg = Background2D(image.data, (25, 25), filter_size=(7, 7))

            image.header.set('BKG_SUB', "Yes")

            image.data = image.data - bkg.background

            print("Image data type: ", image.data.dtype.name)

            hdul.flush()

    if type == 'stack':

        fn = imagefile
        print("Stack mode background subtraction on ", fn.split("/")[-1])

        # data, header = fits.getdata(fn, header=True)
        with fits.open(fn, mode='update') as hdul:
            image = hdul[0]

            if 'BKG_SUB' in image.header:
                print(fn.split("/")[-1], "Stack image already background subtracted, moving on..")
                return

            mask = (image.data == 0)
            bkg = Background2D(image.data, (15, 15), filter_size=(9,9), mask=mask)
            back = bkg.background * ~mask

            # norm = ImageNormalize(stretch=SqrtStretch())
            # plt.imshow(back, origin='lower', cmap='Greys_r', norm=norm)
            # plt.show()

            image.data = image.data - back

            image.scale('int32')

            image.header.set('BKG_SUB', "Yes")

            hdul.flush()

# copyfile('/home/david/Desktop/T19Sorted/1/Image_Light_002.fits','/home/david/Desktop/20180902/T19Sorted/1/Image_Light_002.fits')
# calibrate_fits("single",'null','/home/david/Desktop/20180902/T19Sorted/1/Image_Light_002.fits')
