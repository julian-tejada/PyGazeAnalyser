
# This script estimate the frequency of fixation/saccades, their duration and latency regarding 
# a set of poligonal AOI defined on a txt file. The txt have to have the name aoi.txt. 
#
# The aoi.txt is delimited text file that uses a comma to separate values. The first line indicate
# the name of the columns which should include as many names as vertices has the largest n-gon defined: 
# Corners,x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6.....
# where Corners is the number of polygon vertices, xn  and yn are the coordinates (x and y) of 
# the polygon vertices that define the AOI.
#
# The aoi.txt could have as many lines as polygonal AOI defined for all of the images used as stimuli, 
# the measures of all areas will estimated recursively.

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

__author__ = "Julian Tejada 2019 adapted from a script of Edwin Dalmaijer"

# native
import os
import csv
import sys

# custom
from pygazeanalyser.idfreader import read_idf
from pygazeanalyser.gazeplotter import draw_fixations, draw_heatmap, draw_scanpath, draw_raw

# external
import numpy as np
import pandas as pd
from matplotlib import path # to operate the polygonal AOIs

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
out.writerow(["Subject","Image","Area","Trial","FF_AOI","DF_AOI","LF_AOI","FE_AOI0","DE_AOI0","LE_AOI0", "Dwell_AOI"])
AOI_Fixations = pd.DataFrame(np.zeros(((len(df)), 5)), columns=['area','trial', 'starttime_mean','duration','frequency'])
AOI_DwellTime = pd.DataFrame(np.zeros(((len(df)), 3)), columns=['area','trial','frequency'])
AOI_Fixations = pd.DataFrame(np.zeros(((len(df)), 5)), columns=['area','trial', 'starttime_mean','duration','frequency'])
AOI_SaccadesEntries = pd.DataFrame(np.zeros(((len(df)), 5)), columns=['area','trial','latency','frequency', 'duration'])

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
    
	
	for area in range(0,len(df),1):
#	for area in range(3):
	   	print("area '%i'" % area)
	   	Corners_x = []
	   	Corners_y = []
	   	for j in range(0,df.iloc[area, 0]*2,2):
	   		Corners_x.append(df.iloc[area,j+1])
	   		Corners_y.append(df.iloc[area,j+2])
	   	p = path.Path(zip(Corners_x, Corners_y))
	   	try:
	   	    points = p.contains_points(zip(fixations_df['endx'], fixations_df['endy']))	   	
	   	    TempFix = pd.DataFrame(fixations, columns=['starttime', 'endtime', 'duration', 'endx', 'endy'], index = points)
	   	    TempFix = TempFix.loc[True]
	   	        ######  AOI - Fixations- stop
	   	    AOI_Fixations['area'][area] =  area
	   	    AOI_Fixations['trial'][area] =  trialnr
	   	    AOI_Fixations['starttime_mean'][area] =  TempFix['starttime'].min()
	   	    AOI_Fixations['duration'][area] =  TempFix['duration'].sum()
	   	    AOI_Fixations['frequency'][area] =  TempFix['duration'].size
	   	except:  
	   	    AOI_Fixations['area'][area] =  area
	   	    AOI_Fixations['trial'][area] =  trialnr
	   	    AOI_Fixations['starttime_mean'][area] =  0
	   	    AOI_Fixations['duration'][area] =  0
	   	    AOI_Fixations['frequency'][area] =  0
              
	   	            
	   	 ######  AOI - Dwell time- stop
	   	try:
	   	    points = p.contains_points(zip( dwell_df['x'],  dwell_df['y']))
	   	    TempDwell = pd.DataFrame(dwell_df, index = points)

	   	    TempDwell = TempDwell.loc[True]
	   	    AOI_DwellTime['area'][area] =  area
	   	    AOI_DwellTime['trial'][area] =  trialnr
	   	    AOI_DwellTime['frequency'][area] =  TempDwell['x'].size
	   	except:
	   	    AOI_DwellTime['area'][area] =  area
	   	    AOI_DwellTime['trial'][area] =  trialnr
	   	    AOI_DwellTime['frequency'][area] =  0
	   	           
	   	 ######  AOI - Saccades Entries
	   	try:            
	   	    Points_star = p.contains_points(zip( saccades_df['startx'],  saccades_df['starty']))
	   	    Points_star = np.invert(Points_star)
	   	    Points_end = p.contains_points(zip( saccades_df['endx'],  saccades_df['endy']))
	   	    Points = np.vstack((Points_star, Points_end)).T
	   	    Entries = Points.all(axis=1)
	   	    Temp_sac_ent = pd.DataFrame(saccades, columns=['starttime', 'endtime', 'duration', 'startx', 'starty', 'endx', 'endy'], index=Entries)
	   	
	   	    Temp_sac_ent = Temp_sac_ent.loc[True]
	   	    AOI_SaccadesEntries['area'][area] = area
	   	    AOI_SaccadesEntries['trial'][area] =  trialnr
	   	    AOI_SaccadesEntries['latency'][area] =  Temp_sac_ent['starttime'].min()
	   	    AOI_SaccadesEntries['duration'][area] =  Temp_sac_ent['duration'].sum()
	   	    AOI_SaccadesEntries['frequency'][area] =  Temp_sac_ent['duration'].size
	   	except:
	   	    AOI_SaccadesEntries['area'][area] = area
	   	    AOI_SaccadesEntries['trial'][area] =  trialnr
	   	    AOI_SaccadesEntries['latency'][area] =  0
	   	    AOI_SaccadesEntries['duration'][area] =  0
	   	    AOI_SaccadesEntries['frequency'][area] =  0
	   	
	   	    print("Not entries found")
	   	out.writerow([str(sys.argv[1]),imgname[trialnr], area, trialnr, AOI_Fixations['frequency'][area],AOI_Fixations['duration'][area], AOI_Fixations['starttime_mean'][area], AOI_SaccadesEntries['frequency'][area], AOI_SaccadesEntries['duration'][area], AOI_SaccadesEntries['latency'][area], AOI_DwellTime['frequency'][area]])
	   	print("Escrita area '%i'" % area)
        
print('end')
    
    
    
     
     
    
