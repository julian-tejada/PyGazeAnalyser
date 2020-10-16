# analysis script for natural viewing experiment
#
# version 1 (1 Mar 2014)

# This script estimate the frequency of fixation/saccades, their duration and latency regarding 
# a set of AOI defined on a txt file. The txt have to have the same name that the txt file with 
# the tracker records but with the extension aoi.txt. For instance, if the tracker file is called 
# subject1.txt, the AOI file should called subject1.aoi.txt.
#
# The aoi.txt is delimited text file that uses a comma to separate values. The first line indicate
# the name of the columns which should include at least four columns: 
# x0,y0,x1,y1
# where (x0,y0) are the coordinates of the left upper corner of the rectangle that define the AOI, and
# (x1,y1) are the coordinates of the right button corner of the same rectangle
#
# The aoi.txt could have as many lines as AOI defined for all of the images used as stimuli, 
# the measures of all areas will estimated recursively 
#
# The result is a csv file with the next columns
# "Subject","Image","Area","Trial","FF_AOI","DF_AOI","LF_AOI","FE_AOI0","DE_AOI0","LE_AOI0", "Dwell_AOI"
# where Area is the Subject is the name of the text file with the tracker records. Image is the name of
# the screenshot of the stimuli analyzed. Area is a consecutive number of the areas defined in the 
# aoi.txt file. Trial is a consecutive number of the trials that compound a set of stimuli. 
# FF_AOI if frequency of fixations on the AOI; DF_AOI if the fixation duration on the AOI, 
# FE_AOI0 is the frequency of entries on the AOIs, DE_AOI0 is the duration of the entries on each AOIs,  
# LE_AOI0 if the latency of the firts fixation on each AOI, Dwell_AOI is the number of lines on 
# the text file with the tracker records whichs correspond with the AOI.
# 

__author__ = "Edwin Dalmaijer, adapted by Julian Tejada 2019"

# native
import os
import csv
import sys

# custom
#from pygazeanalyser.edfreader import read_edf
from pygazeanalyser.idfreader import read_idf
from pygazeanalyser.gazeplotter import draw_fixations, draw_heatmap, draw_scanpath, draw_raw

# external
import numpy as np
import pandas as pd

# # # # #
# CONSTANTS

# PARTICIPANTS
print ("File name: %s" % str(sys.argv[1]))
#ppname = 'BC_Avila_6'
PPS = [str(sys.argv[1])]
# DIRECTORIES
# paths
#DIR = os.path.dirname(__file__)
DIR = os.path.dirname(os.path.realpath('__file__'))
#
IMGDIR = os.path.join(DIR, 'imgs', str(sys.argv[1]))
imgname = os.listdir(IMGDIR)
os.chdir(os.path.join(IMGDIR))
imgname.sort(key=os.path.getmtime)
os.chdir(DIR)

DATADIR = os.path.join(DIR, 'data')
PLOTDIR = os.path.join(DIR, 'plots')
OUTPUTFILENAME = os.path.join(DIR, "output.txt")
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
DISPSIZE = (1920,1080) # (px,px)
SCREENSIZE = (39.9,29.9) # (cm,cm)
SCREENDIST = 61.0 # cm
PXPERCM = np.mean([DISPSIZE[0]/SCREENSIZE[0],DISPSIZE[1]/SCREENSIZE[1]]) # px/cm


# # # # #
# READ FILES

# loop through all participants
#for ppname in PPS:
ppname = str(sys.argv[1])	
#print("starting data analysis for participant '%s'" % (ppname))

	# BEHAVIOUR
print("loading behavioural data")
#df = pd.read_csv(os.path.join(DATADIR, 'BC_Avila_6.aoi.txt'))	
df = pd.read_csv(os.path.join(DATADIR, 'aoi.txt' ))	
	# path
fp = os.path.join(DATADIR, '%s.txt' % ppname)
	
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
	

edfdata = read_idf(fp, EDFSTART, EDFSTOP, missing=0.0)
	

	
print("plotting gaze data")

# dataframe of results

out = csv.writer(open(os.path.join(DATADIR, '%s.aoi.analisis.txt' % ppname),"a"), delimiter=';', quoting=csv.QUOTE_ALL)
out.writerow(["Sujeto","Imagen","Area","Ensayo","FF_AOI","DF_AOI","LF_AOI","FE_AOI0","DE_AOI0","LE_AOI0", "Dwell_AOI"])
AOI_Fixations = pd.DataFrame(np.zeros(((len(edfdata)), 5)), columns=['area','trial', 'starttime_mean','duration','frequency'])
AOI_DwellTime = pd.DataFrame(np.zeros(((len(edfdata)), 3)), columns=['area','trial','frequency'])
AOI_Fixations = pd.DataFrame(np.zeros(((len(edfdata)), 5)), columns=['area','trial', 'starttime_mean','duration','frequency'])
AOI_SaccadesEntries = pd.DataFrame(np.zeros(((len(edfdata)), 5)), columns=['area','trial','latency','frequency', 'duration'])

	# loop through trials
for trialnr in range(len(edfdata)):
		
		# load image name, saccades, and fixations

	print("imagename '%s'" % imgname[trialnr])
	print("trialnr '%i'" % trialnr )
		#'L Event Info' in edfdata
	saccades = edfdata[trialnr]['events']['Esac']
	fixations = edfdata[trialnr]['events']['Efix'] # [starttime, endtime, duration, endx, endy]
	dwell_x = edfdata[trialnr]['x']
	dwell_y = edfdata[trialnr]['y']
	

    ### AOI - Fixations- start detection
	# create a dataframe with all fixations
	fixations_df = pd.DataFrame(fixations, columns=['starttime', 'endtime', 'duration', 'endx', 'endy'])
    # create a dataframe with all saccades
	saccades_df = pd.DataFrame(saccades, columns=['starttime', 'endtime', 'duration', 'startx', 'starty', 'endx', 'endy'])
    # create dataframes with dwell_x and dwell_y
	dwell_df = pd.DataFrame({'x':dwell_x, 'y':dwell_y})
    # Remove blinks
	dwell_df = dwell_df.drop(dwell_df[(dwell_df.x <= 0) & (dwell_df.y <= 0)].index)
    

    
	for  area in range(len(df)):
	   	print("area '%i'" % area)
         ######  AOI - Fixations- stop
	   	TempFix = fixations_df[(fixations_df['endx']>df['x0'][area]) & (fixations_df['endx']<=df['x1'][area]) & (fixations_df['endy']>df['y0'][area]) & (fixations_df['endy']<=df['y1'][area])]
	   	AOI_Fixations['area'][area] =  area
	   	AOI_Fixations['trial'][area] =  trialnr
	   	AOI_Fixations['starttime_mean'][area] =  TempFix['starttime'].min()
	   	AOI_Fixations['duration'][area] =  TempFix['duration'].sum()
	   	AOI_Fixations['frequency'][area] =  len(TempFix['duration'])
	   	 ######  AOI - Dwell time- stop
	   	TempDwell = dwell_df[(dwell_df['x']>df['x0'][area]) & (dwell_df['x']<=df['x1'][area]) & (dwell_df['y']>df['y0'][area]) & (dwell_df['y']<=df['y1'][area])]
	   	AOI_DwellTime['area'][area] =  area
	   	AOI_DwellTime['trial'][area] =  trialnr
	   	AOI_DwellTime['frequency'][area] =  len(TempDwell['x'])
	   	
	   	
	   	 ######  AOI - Saccades Entries
	   	Temp_sac_ent = saccades_df[(((saccades_df['startx']<df['x0'][area]) | (saccades_df['startx']>df['x1'][area])) & ((saccades_df['starty']<df['y0'][area]) | (saccades_df['starty']>df['y1'][area]))) & (((saccades_df['endx']>df['x0'][area]) & (saccades_df['endx']<=df['x1'][area])) & ((saccades_df['endy']>df['y0'][area]) & (saccades_df['endy']<=df['y1'][area])))]
	   	AOI_SaccadesEntries['area'][area] = area
	   	AOI_SaccadesEntries['trial'][area] =  trialnr
	   	AOI_SaccadesEntries['latency'][area] =  Temp_sac_ent['starttime'].min()
	   	AOI_SaccadesEntries['duration'][area] =  Temp_sac_ent['duration'].sum()
	   	AOI_SaccadesEntries['frequency'][area] =  len(Temp_sac_ent['duration'])
	   	out.writerow([str(sys.argv[1]),imgname[trialnr], area, trialnr, AOI_Fixations['frequency'][area],AOI_Fixations['duration'][area], AOI_Fixations['starttime_mean'][area], AOI_SaccadesEntries['frequency'][area], AOI_SaccadesEntries['duration'][area], AOI_SaccadesEntries['latency'][area], AOI_DwellTime['frequency'][area]])
	   	
	   	print("Escrita area '%i'" % area)
        
print('end')
    
    
    
     
     
    
