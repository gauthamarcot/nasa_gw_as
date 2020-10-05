"""Main GUI for application"""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from AsteroidDetector.StackImgs import stack_images
from AsteroidDetector.RegisterStacks import register_stacks
from AsteroidDetector.ReadDB import parse_db
from AsteroidDetector.FindAsteroids import find_asteroids
from AsteroidDetector.DS9 import launch_ds9
from AsteroidDetector.TransientsShow import display_transients
from AsteroidDetector.SkycovReport import generageCovReport
from AsteroidDetector.ShowExtractedStars import display_stars
import glob, os

class Application(Frame):

    def __init__(self, master):

        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):

        #SETUP MENU STRUCTURE
        menubar = Menu(root)

        #SETUP FILE MENU
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        aboutmenu = Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About", command= self.show_about)
        #aboutmenu.add_command(label="Register", command=self.register_app)
        menubar.add_cascade(label="About", menu=aboutmenu)

        #ADD MENUBAR TO CONFIG
        root.config(menu=menubar)

        self.inst = Label(self, text = "IMAGE DIR:")
        self.inst.grid(row = 0, column = 0, columnspan = 4, sticky = W)

        self.inst2 = Label(self, text = "IMAGE STACK / REG:")
        self.inst2.grid(row = 0, column = 1, columnspan = 4, sticky = W)

        #SELECT DIR
        self.buttonTS = Button(self, text='SET IMAGE DIR', command= self.sel_working_dir)
        self.buttonTS.grid(row= 1, column =0, sticky = W)

        #Stack Images
        self.buttonStack = Button(self, text="PROCESS IMGS", command = self.stack_images)
        self.buttonStack.grid(row=1, column=1, sticky=W)
        self.buttonStack.config(state=DISABLED)

        #Stack Images
        self.buttonReport = Button(self, text="COV REPORT", command = self.gen_covreport)
        self.buttonReport.grid(row=1, column=2, sticky=W)

        #LABEL INSTRUCTIONS
        self.inst3 = Label(self, text = "PARAMETERS:")
        self.inst3.grid(row = 2, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.fwhmInput = Entry(self, text='FWHM')
        self.fwhmInput.grid(row = 3, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.inst3 = Label(self, text = "Min. FWHM in Arc Sec")
        self.inst3.grid(row = 3, column = 1, columnspan = 1, sticky = W)

        #AST SEARCH RADIUS
        self.astSearchInput =Entry(self)
        self.astSearchInput.grid(row = 4, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.inst4 = Label(self, text = "Asteroid Search ArcSec")
        self.inst4.grid(row = 4, column = 1, columnspan = 1, sticky = W)

        #STAR SEARCH RAD
        self.starSearchInput =Entry(self)
        self.starSearchInput.grid(row = 5, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.inst5 = Label(self, text = "Star Search ArcSec")
        self.inst5.grid(row = 5, column = 1, columnspan = 1, sticky = W)

        #LIM MAG
        self.limMagInput =Entry(self)
        self.limMagInput.grid(row = 6, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.inst6 = Label(self, text = "Limiting Mag V")
        self.inst6.grid(row = 6, column = 1, columnspan = 1, sticky = W)

        #LIM MAG
        self.starLimMag =Entry(self)
        self.starLimMag.grid(row = 7, column = 0, columnspan = 1, sticky = W)

        #LABEL INSTRUCTIONS
        self.inst8 = Label(self, text = "Star Lim Mag")
        self.inst8.grid(row = 7, column = 1, columnspan = 1, sticky = W)

        #SUB BG SINGLE
        self.forceOverwrite = IntVar()
        self.forceOverwrite.set(0)
        self.forceOverwriteC = Checkbutton(self, text=": Force OverWrite", variable=self.forceOverwrite)
        self.forceOverwriteC.grid(row = 3, column = 2, columnspan = 1, sticky = W )

        #SUB BG SINGLE
        self.forceSingle = IntVar()
        self.forceSingle.set(0)
        self.forceSingleC = Checkbutton(self, text=": Single Img Mode", variable=self.forceSingle)
        self.forceSingleC.grid(row = 4, column = 2, columnspan = 1, sticky = W )

        #SUB BG SINGLE
        self.subSingle = IntVar()
        self.subSingle.set(0)
        self.subCheck = Checkbutton(self, text=": Experimental", variable=self.subSingle)
        self.subCheck.grid(row = 5, column = 2, columnspan = 1, sticky = W )


        #REQUORE 4 HITS
        self.req4 = IntVar()
        self.req4.set(0)
        self.checkbuttonC = Checkbutton(self, text=": Req. 4 Hits", variable=self.req4)
        self.checkbuttonC.grid(row = 6, column = 2, columnspan = 1, sticky = W )

        #REQUORE 4 HITS
        self.bgSubStack = IntVar()
        self.bgSubStack.set(1)
        self.checkbuttonD = Checkbutton(self, text=": BG Sub Stack", variable=self.bgSubStack)
        self.checkbuttonD.grid(row = 7, column = 2, columnspan = 1, sticky = W )

        ### ROW 7 IS OPEN NOW

        #FINDAST  command= lambda: action(someNumber)
        self.findAstBtn = Button(self, text='FIND ASTEROIDS', command= self.subtract_and_reduce)
        self.findAstBtn.grid(row= 8, column =0, sticky = W)
        self.findAstBtn.config(state=DISABLED)


        #CLEAN UP
        self.cleanUpBtn = Button(self, text='LAUNCH DS9', command= self.launch_ds9)
        self.cleanUpBtn.grid(row= 8, column =1, sticky = W)
        #self.cleanUpBtn.config(state=DISABLED)

        #TRANSIENTS
        self.tranBtn = Button(self, text='SHOW TRANS', command= self.show_transients)
        self.tranBtn.grid(row= 8, column =2, sticky = W)
        self.tranBtn.config(state=DISABLED)

        #Extractions
        self.extBtn = Button(self, text='SHOW EXTRACTION', command= self.show_stars)
        self.extBtn.grid(row= 9, column =0, sticky = W)
        self.extBtn.config(state=DISABLED)

        #LABEL INSTRUCTIONS
        self.inst7 = Label(self, text = "Image Number: ")
        self.inst7.grid(row = 9, column = 1, columnspan = 1, sticky = W)

        #Extract img
        self.extImgInput =Entry(self)
        self.extImgInput.grid(row = 9, column = 2, columnspan = 1, sticky = W)
        self.extImgInput.insert(END, "1")


        self.defaultFopen = ""
        self.require4 = False
        self.subSingleV = False
        self.fSingleMode = False
        self.forceOverwriteV = False
        self.bgSubStackV = False

        myTree = Toplevel()
        self.tree = ttk.Treeview(myTree)
        self.tree.pack(fill="both")

        #self.launch_ds9()


        # LOAD CONFIG
        root_path = os.path.dirname(os.path.realpath(__file__))
        try:
            obsf = open(root_path + "/obsconfig.txt", "r")
            for line in obsf:
                if "Default FWHM Minimum" in line:
                    self.fwhmInput.insert(END, line.split(":")[-1].strip())
                if "Default Asteroid Search Radius" in line:
                    self.astSearchInput.insert(END, line.split(":")[-1].strip())
                if "Default Star Search Radius" in line:
                    self.starSearchInput.insert(END, line.split(":")[-1].strip())
                if "Default Limiting Mag" in line:
                    self.limMagInput.insert(END, line.split(":")[-1].strip())
                if "Default File Open Dir" in line:
                    self.defaultFopen = line.split(":")[-1].strip()
                if "Star Lim Mag" in line:
                    self.starLimMag.insert(END, line.split(":")[-1].strip())
            print("\nDefaults Loaded\n")
            obsf.close()
        except:
            "Config file not found, exiting.."
            return


        #SETUP VARIABLES
        self.working_dir = ""

    def show_about(self):

        ABOUT_TEXT = """About
        ASTEROID DETECTOR V1.0
        Program 2018 David Rankin
        """
        toplevel = Toplevel()
        toplevel.resizable(width=FALSE, height=FALSE)
        toplevel.title('About')
        label1 = Label(toplevel, text=ABOUT_TEXT, height=0, width=50, justify=LEFT)
        label1.grid()

    ############ SELECT WORKING DIR ###################
    def sel_working_dir(self):
        self.working_dir = filedialog.askdirectory(initialdir = self.defaultFopen)
        print("Working directory set to: ", self.working_dir)

        terminal_title = "Sequence: " + self.working_dir.split('/')[-1]

        print("\33]0;"+terminal_title+"\a", end='', flush=True)

        if self.working_dir == () or self.working_dir == "":
            self.buttonStack.config(state=DISABLED)
            self.findAstBtn.config(state=DISABLED)
            self.tranBtn.config(state=DISABLED)
            return

        self.buttonStack.config(state=NORMAL)
        self.findAstBtn.config(state=NORMAL)
        self.cleanUpBtn.config(state=NORMAL)
        self.tranBtn.config(state=NORMAL)
        self.extBtn.config(state=NORMAL)

    ############ PROCESS INDIVIDUAL IMAGES ###################
    def stack_images(self):

        fitsfn = glob.glob(self.working_dir +"/*.fits")
        print(fitsfn)
        fitsfn = fitsfn[0].split("/")[1]
        fitsfn = fitsfn.split("_")
        fitsfn = fitsfn[0]+"_"
        print(fitsfn)

        self.buttonStack.config(state=DISABLED)

        if self.subSingle.get() == 1:
            self.subSingleV = True
        else:
            self.subSingleV = False

        if self.forceSingle.get() == 1:
            self.fSingleMode = True
        else:
            self.fSingleMode = False

        message = stack_images(self.working_dir, self.subSingleV, self.fSingleMode, fitsfn)
        if (message != None):

            if (message == "Error, images failed to register."):
                return

        self.buttonStack.config(state=NORMAL)
        self.register_stacked_images()

    ############ REGISTER STACKED IMAGES ###################
    def register_stacked_images(self):
        print("\nRegistering and solving stacked images .. \n")

        if self.bgSubStack.get() == 1:
            self.bgSubStackV = True

        message = register_stacks(self.working_dir, self.bgSubStackV)

        if (message == "Error"):
            print("Error, not enough images. Exiting")
            return
        else:
            self.subtract_and_reduce()

    ############ SUBTRACT STARS AND FIND ASTEROIDS ###################
    def subtract_and_reduce(self):

        self.update()

        dir = self.working_dir
        limmag = float(self.limMagInput.get())
        fwhm_min = float(self.fwhmInput.get())
        ast_search_rad = float(self.astSearchInput.get())
        star_search_radius = float(self.starSearchInput.get())
        star_lim_mag = float(self.starLimMag.get())

        searchtype = 'asteroid'

        #FROM ReadDB
        #Message 2 returns string if error
        message2 = parse_db(dir, limmag, star_search_radius, fwhm_min, ast_search_rad, star_lim_mag)
        print(message2)
        if (message2 != ""):
            return

        ### CALL ASTEROID SEARCH HERE ###
        astmatch = 0
        #Message4 returns number

        if self.req4.get() == 1:
            self.require4 = True
        else:
            self.require4 = False

        message4 = find_asteroids(dir, star_search_radius, fwhm_min, ast_search_rad, astmatch, self.require4)

        if message4 < 1:
            print("\nNo asteroids found..\n")
            message4 = "\nNo asteroids found..\n"

        else: #
            #Launch DS9 to confirm
            self.launch_ds9()

    def launch_ds9(self):
        #TESTING
        self.working_dir = "/usr/local/bin/ds9"

        if self.forceOverwrite.get() == 1:
            self.forceOverwriteV = True
        else:
            self.forceOverwriteV = False

        launch_ds9(self.working_dir, self.tree, self.forceOverwriteV)

    def show_transients(self):
        print("\nDisplaying Transients in DS9\n")
        display_transients(self.working_dir)

    def gen_covreport(self):
        print("\nGenerate skycov report\n")
        self.skycov_dir = filedialog.askdirectory(initialdir = self.defaultFopen)
        print("Working directory set to: ", self.skycov_dir)
        if self.skycov_dir == () or self.skycov_dir == "":
            return
        try:
            generageCovReport(self.skycov_dir)
        except:
            print("\nError generating report")

    def show_stars(self):
        imgnum = int(self.extImgInput.get())
        display_stars(self.working_dir, imgnum)

    #CLOSE OUT AND SAVE DEFAULTS TO TEXT FILE
    def on_closing(self):

        root_path = os.path.dirname(os.path.realpath(__file__))

        try:
            configFile = open(root_path + "/obsconfig.txt", "r")
            configFileNew = open(root_path + "/obsconfigN.txt", "w")

            for line in configFile:

                if "Default FWHM Minimum" in line:
                    configFileNew.write("Default FWHM Minimum: " + self.fwhmInput.get() +"\n")
                    continue

                if "Default Asteroid Search Radius" in line:
                    configFileNew.write("Default Asteroid Search Radius: " + self.astSearchInput.get()+"\n")
                    continue

                if "Default Star Search Radius" in line:
                    configFileNew.write("Default Star Search Radius: " + self.starSearchInput.get()+"\n")
                    continue

                if "Default Limiting Mag" in line:
                    configFileNew.write("Default Limiting Mag: " + self.limMagInput.get()+"\n")
                    continue

                if "Star Lim Mag" in line:
                    configFileNew.write("Star Lim Mag: " + self.starLimMag.get()+"\n")
                    continue

                configFileNew.write(line)

            print("\nDefaults Saved\n")
            configFile.close()
            configFileNew.close()

            os.remove(root_path + "/obsconfig.txt")
            os.rename(root_path + "/obsconfigN.txt", root_path + "/obsconfig.txt")

        except:
            "Error saving config.."
            return

        #exiting
        print("Exiting...")
        root.destroy()

root = Tk()
root.title("ASTEROID DETECTOR")
root.geometry("670x450")
app = Application(root)
root.resizable(width=FALSE, height=FALSE)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
