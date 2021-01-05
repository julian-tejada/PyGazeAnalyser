# analysis script for natural viewing experiment
#
# version 1 (1 Mar 2014)

__author__ = "Edwin Dalmaijer"

# native
import os
import sys

# custom
from pygazeanalyser.eyetribereader import read_eyetribe
from pygazeanalyser.gazeplotter import draw_fixations, draw_heatmap, draw_scanpath, draw_raw

# external
import numpy


# # # # #
# CONSTANTS

# PARTICIPANTS
print ("File name: %s" % str(sys.argv[1]))
#PPS = ['RegistroPilotoJulian']
PPS = [str(sys.argv[1])]
# DIRECTORIES
# paths
# DIR = os.path.dirname(__file__)
DIR = os.path.dirname(os.path.realpath('__file__'))
print ("dir: %s" % str(DIR))

#
IMGDIR = os.path.join(DIR, 'imgs', str(sys.argv[1]))
print ("image dir: %s" % str(IMGDIR))
imgname = os.listdir(IMGDIR)
os.chdir(os.path.join(IMGDIR))
imgname.sort(key=os.path.getmtime)
os.chdir(DIR)
# imgname = ['PublicidadOreo_1_Fotos_foto3.jpg_Sujeto_1.png','PublicidadOreo_2_Fotos_foto5.jpg_Sujeto_1.png','PublicidadOreo_3_Fotos_foto6.jpg_Sujeto_1.png','PublicidadOreo_4_Fotos_foto9.jpg_Sujeto_1.png','PublicidadOreo_5_Fotos_foto8.jpg_Sujeto_1.png','PublicidadOreo_6_Fotos_Foto2.jpg_Sujeto_1.png','PublicidadOreo_7_Fotos_foto4.jpg_Sujeto_1.png','PublicidadOreo_8_Fotos_Foto1.jpg_Sujeto_1.png','PublicidadOreo_9_Fotos_foto10.jpg_Sujeto_1.png','PublicidadOreo_10_Fotos_foto7.jpg_Sujeto_1.png']
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
PXPERCM = numpy.mean([DISPSIZE[0]/SCREENSIZE[0],DISPSIZE[1]/SCREENSIZE[1]]) # px/cm


# # # # #
# READ FILES

# loop through all participants
for ppname in PPS:
	
	print("starting data analysis for participant '%s'" % (ppname))

	# BEHAVIOUR
	print("loading behavioural data")
	
	# path
	fp = os.path.join(DATADIR, '%s.tsv' % ppname)
	
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
	
	## check if the path exist
	#if not os.path.isfile(fp):
		## if not, check if the EDF exists
		#edfp = os.path.join(DATADIR, '%s.edf' % ppname)
		#if os.path.isfile(edfp):
			## if it does, convert if usinf edf2asc.exe
			#os.system("edf2asc %s" % edfp)
			## load ASCII
			#fp = os.path.join(DATADIR, '%s.asc' % ppname)
		## if it does not exist, raise an exception
		#else:
			#raise Exception("No eye data file (neither ASC, nor EDF) file found for participant '%s' (tried paths:\nASC: %s\nEDF: %s" % (ppname, fp, edfp))
	
	# read the file
	# edfdata[trialnr]['time'] = list of timestamps in trialnr
	# edfdata[trialnr]['size'] = list of pupil size samples in trialnr
	edfdata = read_eyetribe(fp, EDFSTART, EDFSTOP, missing=0.0)
	
	# NEW OUTPUT DIRECTORIES
	# create a new output directory for the current participant
	pplotdir = os.path.join(PLOTDIR, ppname)
	# check if the directory already exists
	if not os.path.isdir(pplotdir):
		# create it if it doesn't yet exist
		os.mkdir(pplotdir)


	# # # # #
	# PLOTS
	
	print("plotting gaze data")

	# loop through trials
	for trialnr in range(len(edfdata)):
		
#		# load image name, saccades, and fixations
#		if data[trialnr][header.index("Type")] == 'MSG':
#			continue
#		imgname = data[trialnr][header.index("Stimulus")]
		#imgname = "ConfiguracionExperimentoConsumidor3.png"
		print("imagename '%s'" % imgname )
		print("trialnr '%i'" % trialnr )
		#'L Event Info' in edfdata
		saccades = edfdata[trialnr]['events']['Esac']
		# [starttime, endtime, duration, startx, starty, endx, endy]
		#saccades = data[trialnr]['L Event Info']['Saccade']
		
		fixations = edfdata[trialnr]['events']['Efix'] # [starttime, endtime, duration, endx, endy]
		
		# paths
		imagefile = os.path.join(IMGDIR,imgname[trialnr])
		rawplotfile = os.path.join(pplotdir, "raw_data_%s_%d" % (ppname,trialnr))
		scatterfile = os.path.join(pplotdir, "fixations_%s_%d" % (ppname,trialnr))
		scanpathfile =  os.path.join(pplotdir, "scanpath_%s_%d" % (ppname,trialnr))
		heatmapfile = os.path.join(pplotdir, "heatmap_%s_%d" % (ppname,trialnr))
		
		##raw data points
		#draw_raw(edfdata[trialnr]['x'], edfdata[trialnr]['y'],edfdata[trialnr]['size'], DISPSIZE, imagefile=imagefile, savefilename=rawplotfile)

		#fixations
		draw_fixations(fixations, DISPSIZE, imagefile=imagefile, durationsize=True, durationcolour=True, alpha=0.5, savefilename=scatterfile)
		
		##scanpath
		draw_scanpath(fixations, saccades, DISPSIZE, imagefile=imagefile, alpha=0.5, savefilename=scanpathfile)

		# heatmap		
		draw_heatmap(fixations, DISPSIZE, imagefile=imagefile, durationweight=True, alpha=0.5, savefilename=heatmapfile)
