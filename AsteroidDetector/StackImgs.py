__author__ = 'David Rankin, David@rankinstudio.com'


"""
Lots of stuff happens in here. Stacking of images with siril commands auto generated based on the image name select.
Time calibration, midpoint calibration, time delta variables are made.
"""

import os, glob, re, pickle
import subprocess
import shlex
from astropy.io import fits
from .CalibrateFits import calibrate_fits
from shutil import copy
import ciso8601
import calendar
from datetime import datetime
from .AstToolBox import timeToMPC, natural_sort


def stack_images(dir, subsingle, forcesingle, fitsname):

    root_path = os.path.dirname(os.path.realpath(__file__))

    ###  SIRIL SCRIPT CREAION ###
    stackImg = "r_"+fitsname+"stacked.fits"

    sirilFile = open(root_path + "/sirilScript.ssf", "w")

    # NUMBER OF DIRECTORIES IN WORKING FOLDER
    dirsNum = len(natural_sort(glob.glob(dir + "/*/")))

    for i in range(dirsNum): #Run once for every image direcory
        sirilFile.write("cd "+str(i+1)+"\n")
        sirilFile.write("register "+fitsname+"\n")
        sirilFile.write("stack r_"+fitsname+" sum\n")
        sirilFile.write("cd ..\n")
    sirilFile.write("close")
    sirilFile.close()

    try:
        with open(root_path + "/obsconfig.txt", "r") as obsf:
            for line in obsf:
                if "PP Path" in line:
                    ppPath = line.split(":")[-1].strip()
                if "Exposure Time Key" in line:
                    expTime = line.split(":")[-1].strip()
                if "Begin Exposure Key" in line:
                    beginExp = line.split(":")[-1].strip()
                if "Image Keyword" in line:
                    imageKeyword = line.split(":")[-1].strip()
                if "Dark Image" in line:
                    darkImg = line.split(":")[-1].strip()
                sirilScript = "sirilScript.ssf"

        obsf.close()
    except:
        print("\nConfiguration file obsconfig.txt not found, exiting..\n")
        return

    midpoints = []
    midpointsForHeader = []
    midpointsforDiff = [] # used for total sequence time calculation
    timeDeltas = [] # exposure time deltas for vector search
    fitsf2 = []

    if len(dir) < 1:
        return "Error: Select directory with image stacks \n"

    #GET CHILDREN DIRECTORIES
    dirs = glob.glob(dir + "/*/")
    dirs.sort()

    dirnum = 0
    onlystack = False
    singlestackmode = False

    if len(dirs) < 4:
        return "Error: Not enough images, need 4 sequences \n"

    for directory in dirs:

        fitsf2 = []
        dirnum += 1

        print("\n#####################################")
        print("###    Processing sequence ", dirnum, "    ###")
        print("#####################################\n")

        fitsf = glob.glob(directory + "*.fits")

        fitsf = natural_sort(fitsf)

        #CHANGE TO EACH NEW DIRECTORY
        os.chdir(directory)

        imgs = ""
        imgsfinal = ""

        #Sort fits by name
        for file in fitsf:
            #DONT READ SIRIL RESULT FILES
            if "_pp_" in file:
                continue

            if "r_" in file:
                continue

            if imageKeyword in file:
                fitsf2.append(file)
                img = file.split('/')[-1]
                imgs = imgs + img + " "

        ############## BKGSUBTRACT ############
        if (subsingle == True):
            print("\nPerforming background calibrations..\n")
            #for imagefile in fitsf2:
            calibrate_fits('single',darkImg,fitsf2[0])


        ############## Get exposure midpoint here ###########

        if forcesingle:

            singlestackmode = True

            print("\nSingle image processing mode..\n")

            firstImg = str(fitsf2[0])

            hdu_number = 0

            data, header = fits.getdata(firstImg, header=True)

            fits.getheader(firstImg, hdu_number)

            time1 = header[beginExp]
            exp1 = header[expTime]

            ts1 = ciso8601.parse_datetime(time1)
            ms1 = int(time1.split('.')[-1]) / 1000
            time1Sec = calendar.timegm(ts1.timetuple())

            #Add MS back to UNIX times
            time1Sec = time1Sec + ms1

            #MID for 1 and 2
            midp = time1Sec + (exp1 / 2)

            print("Midpoint in UNIX :", str(midp))
            expMidpoint = datetime.utcfromtimestamp(midp).strftime('%Y-%m-%dT%H:%M:%S.%f')
            expMidpoint = expMidpoint[:-3]

            midpointsforDiff.append(time1Sec)

            #Conver to final MPC time
            finalTime = timeToMPC(expMidpoint)

            midpoints.append(finalTime)

            #STACK RENAME HAPPENS HERE IN SINGLE MODE
            with fits.open(firstImg, mode='update', do_not_scale_image_data=True, uint=True) as hdul:

                image = hdul[0]

                time = str(expMidpoint)
                print(time, " Being written to header")

                image.header.set('DATE-OBS', time)

                hdul.close()

            print("Copying: "+ firstImg)
            copy(firstImg, dir + "/Stack" + str(dirnum) + ".fits")

        else:

            fitsf2 = natural_sort(fitsf2)

            firstImg = str(fitsf2[0])
            lastImg = str(fitsf2[-1])

            hdu_number = 0

            data, header = fits.getdata(firstImg, header=True)
            data2, header2 = fits.getdata(lastImg, header=True)

            fits.getheader(firstImg, hdu_number)
            fits.getheader(lastImg, hdu_number)

            time1 = header[beginExp]
            time1 = time1.replace('Z', '')
            print("First Image Time: ", time1)
            exp1 = header[expTime]
            time2 = header2[beginExp]
            time2 = time2.replace('Z','')
            print("Last Image Time: ", time2)
            exp2 = header2[expTime]

            ts1 = ciso8601.parse_datetime(time1)
            ms1 = int(time1.split('.')[-1]) / 1000
            time1Sec = calendar.timegm(ts1.timetuple())
            ts2 = ciso8601.parse_datetime(time2)
            ms2 = int(time2.split('.')[-1]) / 1000
            time2Sec = calendar.timegm(ts2.timetuple())

            #Add MS back to UNIX times
            time1Sec = time1Sec + ms1
            time2Sec = time2Sec + ms2

            midp = (time1Sec + time2Sec + exp2) / 2
            print("Midpoint in UNIX :", str(midp))
            expMidpoint = datetime.utcfromtimestamp(midp).strftime('%Y-%m-%dT%H:%M:%S.%f')
            expMidpoint = expMidpoint[:-3]


            print(expMidpoint, "Midpoint found")

            midpointsForHeader.append(expMidpoint)
            midpointsforDiff.append(time1Sec)

            #Conver to final MPC time
            finalTime = timeToMPC(expMidpoint)
            print(finalTime)

            midpoints.append(finalTime)


    #Extract total time for set to solve ast vel later
    #Also extract time deltas in sec for asteroid vector search
    time1 = midpointsforDiff[0]
    time2 = midpointsforDiff[1]
    time3 = midpointsforDiff[2]
    time4 = midpointsforDiff[3]

    delta1 = 0
    delta2 = time2 - time1
    delta3 = time3 - time2
    delta4 = time4 - time3

    #TIME DELTAS
    timeDeltas.append(delta1) #Add T0 to start
    timeDeltas.append(round(delta2,4))
    timeDeltas.append(round(delta3,4))
    timeDeltas.append(round(delta4,4))

    print("\nTime Deltas: ", timeDeltas,"\n")

    #TOTAL TIME
    totalTimeT = (time4 - time1)
    totalTimeF = round(totalTimeT / 60, 2) #Convert to minutes for arcsec/min speed calculation
    print(totalTimeF, "Min ", " Total Elapsed Time")

    #DUMP VARS
    with open(dir + '/totaltime', 'wb') as fp:
        pickle.dump(totalTimeF, fp)
    with open(dir + '/timedeltas', 'wb') as fp:
        pickle.dump(timeDeltas, fp)

    #RENAME HAPPENS ABOVE IN SINGLE MODE
    if not singlestackmode:

        siril_command = "siril -s "+root_path+"/"+sirilScript+" -d "+dir
        print("Siril Command Used: ", siril_command)

        my_env = os.environ.copy()
        my_env["PATH"] = ""+ppPath+":" + my_env["PATH"]
        my_env["PHOTPIPEDIR"] = ppPath

        print("Combining images .. \n")
        combine = subprocess.Popen(shlex.split(siril_command), env=my_env)
        combine.wait()

        #RENAME FILES
        dirsnum = 0
        for directory in dirs:

            dirsnum +=1

            image1fn = str(fitsf2[0])

            #COPY HEADER INFO OVER TO STACKED IMAGE

            with fits.open(image1fn,do_not_scale_image_data=True, uint=True) as hdul: #Ref Img
                image = hdul[0]

                header1 = image.header

                hdul.close()

                # data2, header2 = fits.getdata(directory+"/"+ stackImg, header=True)

            with fits.open(directory+"/"+ stackImg, mode='update', do_not_scale_image_data=True, uint=True) as hdul: #Stacked Img

                image2 = hdul[0]

                #Add solved midpoins back to the deader of stacked images
                time = str(midpointsForHeader[dirsnum -1])
                time = time.replace(' ', 'T')
                print(time)

                #COPY KEYS FROM REFERENCE HEADER
                image2.header = header1

                #UPDATE TIME
                image2.header.set('DATE-OBS', time)
                del image2.header['BKG_SUB']

                #UPDATE EXPOSURE TIME (CALCUALTE)

                hdul.close()

                os.rename(directory+"/"+stackImg, dir + "/Stack" + str(dirsnum) + ".fits")

            #CLEAN UP DIRECTORY
            fitsfs = glob.glob(directory + "*.fits")

            for img in fitsfs:
                if "pp_" in img:
                    os.remove(img)
                if "cc_" in img:
                    os.remove(img)
                if "r_" in img:
                    os.remove(img)

            seqfiles = glob.glob(directory + "*.seq")
            for seq in seqfiles:
                os.remove(seq)

    with open(dir + '/midpoints', 'wb') as fp:
        pickle.dump(midpoints, fp)


    return "\nCompleted processing images \n"

#MODULE TESTING PURPOSES UNCOMMENT
#stack_images("/home/david/Desktop/20190102/C1", False, False, "Image_")