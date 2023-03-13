# analysis script for media heatmaps
# 
# This script create mean heatmaps using opensesame loogger file plus eyetracking data
#
# the script recevies three parameters:
# 1. Name of the opensesame logger column
# 2. Partial match of the group name
# 3. Image name in which the mean activity will be projected.


# version 1 (1 Mar 2014)

__author__ = "Julian Tejada"

# native
import os
import sys

# custom
from pygazeanalyser.tobiireader import read_tobii
from pygazeanalyser.gazeplotter import draw_fixations, draw_heatmap, draw_scanpath, draw_raw

# external
import numpy
import pandas as pd



# DIRECTORIES
# paths
# DIR = os.path.dirname(__file__)
DIR = os.path.dirname(os.path.realpath('__file__'))
print ("dir: %s" % str(DIR))

#
IMGDIR = os.path.join(DIR, 'imgs/integrates')
print ("image dir: %s" % str(IMGDIR))
imgname = os.listdir(IMGDIR)
os.chdir(os.path.join(IMGDIR))
imgname.sort(key=os.path.getmtime)
os.chdir(DIR)
imgname = str(sys.argv[3])

DATADIR = os.path.join(DIR, 'data')
PLOTDIR = os.path.join(DIR, 'plots')
OUTPUTFILENAME = os.path.join(DIR, "output.txt")

tsv = []
csv = []
files = os.listdir(os.path.join(DATADIR))
csv = list(filter(lambda x: x.endswith('.csv'), files))
tsv = list(filter(lambda x: x.endswith('_TOBII_output.tsv'), files))


csv_pd = pd.DataFrame(
    {'Filename_csv': csv,
    })
tsv_pd = pd.DataFrame(
    {'Filename_tsv': tsv,
    })

csv_pd['Order'] = csv_pd['Filename_csv'].str.replace('[^\d\.]','', regex=True).astype(float)
tsv_pd['Order'] = tsv_pd['Filename_tsv'].str.replace('[^\d\.]','', regex=True).astype(float)

csv_pd = csv_pd.sort_values(by=['Order'])
tsv_pd = tsv_pd.sort_values(by=['Order'])


Files_pd = pd.merge(csv_pd, tsv_pd, on="Order" )

PPS = []
Order = []
Repetitions = []

for  filenumber in range(len(Files_pd)):
    Temp = pd.read_csv(os.path.join(DATADIR, Files_pd['Filename_csv'][filenumber]),delimiter=',')
    Index = Temp[Temp[str(sys.argv[1])].str.contains(str(sys.argv[2]))]
    # Index = Temp[Temp[str("Fotos")].str.contains("foto3")]
    Order = Order + list(Index.index.values)
    PPS.append(str(Files_pd['Filename_tsv'][filenumber]))
    Repetitions.append(int(len(Index.index)))


# check if the image directory exists
if not os.path.isdir(IMGDIR):
	raise Exception("ERROR: no image directory found; path '%s' does not exist!" % IMGDIR)
# check if the data directory exists
if not os.path.isdir(DATADIR):
	raise Exception("ERROR: no data directory found; path '%s' does not exist!" % DATADIR)
# check if output directorie exist; if not, create it
if not os.path.isdir(PLOTDIR):
	os.mkdir(PLOTDIR)

# DATA FILES
SEP = '\t' # value separator
EDFSTART = "start_trial" # EDF file trial start message
EDFSTOP = "stop_trial" # EDF file trial end message
TRIALORDER = [EDFSTART, 'start_trial','stop_trial', EDFSTOP]
INVALCODE = 0.0 # value coding invalid data

# EXPERIMENT SPECS
DISPSIZE = (1280,1024) # (px,px)
SCREENSIZE = (39.9,29.9) # (cm,cm)
SCREENDIST = 61.0 # cm
PXPERCM = numpy.mean([DISPSIZE[0]/SCREENSIZE[0],DISPSIZE[1]/SCREENSIZE[1]]) # px/cm


# # # # #
# READ FILES
saccades = []
fixations = []
j = 0
k = 0
# loop through all participants
for ppname in PPS:
    print("starting data analysis for participant '%s'" % (ppname))

    # BEHAVIOUR
    print("loading behavioural data")
    
    # path
    fp = os.path.join(DATADIR, '%s' % ppname)
    
    #fp = "/home/julan/ownCloud/FederalSergipe/Projetos/Konrad/PyGaze/data/Teste2.txt"
    # open the file
    fl = open(fp, 'r')
    
    # read the file content
    data = fl.readlines()
    
    # close the file
    fl.close()
    
    # separate header from rest of file
    header = data.pop(0)
    header = header.replace('\n','').replace('\r','').replace('"','').split(SEP)
    
    # process file contents
    for i in range(len(data)):
        data[i] = data[i].replace('\n','').replace('\r','').replace('"','').split(SEP)
    
    # GAZE DATA
    print("loading gaze data")
    
    # path
    #fp = os.path.join(DATADIR, '%s.txt' % ppname)
    
    

    # edfdata[trialnr]['size'] = list of pupil size samples in trialnr
    edfdata = read_tobii(fp, EDFSTART, EDFSTOP, missing=0.0)
    
    # NEW OUTPUT DIRECTORIES
    # create a new output directory for the current participant
    pplotdir = os.path.join(PLOTDIR, 'integrates')
    # check if the directory already exists
    if not os.path.isdir(pplotdir):
        # create it if it doesn't yet exist
        os.mkdir(pplotdir)


    # # # # #
    # PLOTS
    
    print("plotting gaze data")

    # loop through trials
#	for trialnr in range(len(edfdata)):
        
#		# load image name, saccades, and fixations
#		if data[trialnr][header.index("Type")] == 'MSG':
#			continue
#		imgname = data[trialnr][header.index("Stimulus")]
        #imgname = "ConfiguracionExperimentoConsumidor3.png"
    print("imagename '%s'" % imgname )
    # print("trialnr '%i'" % Order[j] )
        #'L Event Info' in edfdata
    for repeat in range(Repetitions[j]):
        saccades= saccades + edfdata[Order[k]]['events']['Esac']
        fixations= fixations + edfdata[Order[k]]['events']['Efix']
        k+=1
    # [starttime, endtime, duration, endx, endy]
    j+=1



		
		# paths
imagefile = os.path.join(IMGDIR, imgname)
#rawplotfile = os.path.join(pplotdir, "raw_data_%s_%d" % (ppname,trialnr))
scatterfile = os.path.join(pplotdir, "fixations_%s" % imgname)
scanpathfile =  os.path.join(pplotdir, "scanpath_%s" % imgname)
heatmapfile = os.path.join(pplotdir, "heatmap_%s" % imgname)

draw_fixations(fixations, DISPSIZE, imagefile=imagefile, durationsize=True, durationcolour=True, alpha=0.5, savefilename=scatterfile)
draw_scanpath(fixations, saccades, DISPSIZE, imagefile=imagefile, alpha=0.5, savefilename=scanpathfile)
		
draw_heatmap(fixations, DISPSIZE, imagefile=imagefile, durationweight=True, alpha=0.5, savefilename=heatmapfile)
