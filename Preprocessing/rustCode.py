import cv2
import os
import argparse
from multiprocessing import Pool
import multiprocessing
import shutil
import numpy as np
import imutils
import dlib


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Mostrar informacion de depuracion", action="store_true")
parser.add_argument("-fp", "--fp", help="Carpeta a procesar")
parser.add_argument("-ap", "--ap", help="absolute path")

args = parser.parse_args()


class preprocessData:

	global file, folderPath, detector, tempImage
	def __init__(self,folderPath,absolutePath):
		
		self.folderPath = folderPath
		self.absolutePath = absolutePath
		self.detector = dlib.simple_object_detector("detectors/detector_plants_v5_C150.svm")
		self.tempImage = None


	def createSubFolders(self):
		types = ["json","rgb","re","rgn"]

		for i in types:
			path = str(self.absolutePath)+str(i)+"_data"
			if not os.path.exists(path):
				os.mkdir(path)
				
	def findTypes(self,folder):

		json = []
		rgb = []
		re = []
		rgn = []
		# this list has the values which didn't match with any type
		other = []
		cont=0
		#find the files in the whole path
		for root, dirs, files in os.walk(folder):
			for file in files:
				line = str(os.path.join(root, file))
				cont+=1
				if line.find("rgb") != -1:
					rgb.append(line)

				elif line.find("re.") != -1:
					re.append(line)

				elif line.find("rgn.") != -1:
					rgn.append(line)

				elif line.find(".json") != -1:
					json.append(line)

				else:
					other.append(line)

		print("cont4: "+str(cont))

		#print(json)
		
		return json,rgb,re,rgn, other

	def findTypes4Clean(self,folder):
		print(folder)
		json = []
		rgb = []
		re = []
		rgn = []
		# this list has the values which didn't match with any type
		other = []
		#find the files in the whole path
		cont = 0
		for root, dirs, files in os.walk(folder):
			for file in files:
				line = str(os.path.join(root, file))
				#print(line)
				cont+=1
				if line.find("rgb_") != -1:
					rgb.append(line)

				elif line.find("re_") != -1:
					re.append(line)

				elif line.find("rgn_") != -1:
					rgn.append(line)

				elif line.find("json_") != -1:
					json.append(line)

				else:
					other.append(line)
			

		#print(json)
		
		return json,rgb,re,rgn, other

	def sendData(self,list_type,typestr):
	
		cont = 0
		changeCount = 0
		for i in list_type:

			#Erase the begginig of the path
			cfpath = i.replace("../model_preprocessing/data","")
			#Find the last '/'
			line_split = cfpath.rindex('/')
			#use the last '/' to erase the namefile
			cfpath = cfpath[:line_split+1]
			#update the path with the folder and the rest of the path
			save_file = "../model_preprocessing/data2/"+typestr+"/"+cfpath

			#Erase a '/' to find the new last index of the '/'
			save_file = save_file[:len(save_file)-1]
			
			#print("sin/"+save_file)
			#Find the last '/'
			line_split = save_file.rindex('/')

			#Erase the folder lot*
			save_file = save_file[:line_split+1]
			#print("sin/pal"+save_file)

			# Extract the number of the illness to restart the counter
			if changeCount != i[28] and typestr != "rgb_data":
				cont=0

			#Update the new number of the illness
			changeCount = i[28]
			#print(typestr+str(changeCount))

			# If the type is rgb its nececesarry to delete other folder of the path
			if typestr == "rgb_data":
				last_index = i.rindex('/')
				place = i[last_index-1:last_index]
				
				#print(place)
				#print(i)

				save_file = save_file[:save_file.find("lot")]
				save_file = save_file[:-2]
				#Save the new path with the new place of the rgb specific illness 
				save_file = save_file +place+"/"
				
				
				#print(save_file)

			#Create the folder
			if not os.path.exists(save_file):
				os.makedirs(save_file)

			#copy the file
			shutil.copy(i, save_file)

			file = i[i.rindex('/'):]
			ext = ""

			if typestr == "json_data":
				ext = ".json"
			else:
				ext = ".jpg"

			#print(typestr+str(cont))
			#print(save_file+str(cont)+ext)
			os.rename(save_file+file, save_file+str(cont)+ext)
			cont+=1
		

			


	def extractFiles(self):
		#path = os.listdir(self.folderPath)

		# Create the four new subfolders
		self.createSubFolders()

		json,rgb,re,rgn, idk = self.findTypes(self.folderPath)

		types = [json,rgb,re,rgn]
		string_types = ["json_data","rgb_data","re_data","rgn_data"]
		
		#Print the total values of the set
		#print(len(json)+len(rgb)+len(re)+len(rgn)+len(idk))
		#Print the values which doesn't match with no type
		#print(idk)

		for st,t in zip(string_types,types):
			self.sendData(t,st)

		# Rename all the rgb files
		p.renameRGBFiles(args.ap)

#4880

	def renameRGBFiles(self,path):
		cont = 0
		number = 0
		contentro= 0
		for root, dirs, files in os.walk(path):
			for file in files:
				line = str(os.path.join(root, file))
				
				if line.find("rgb_") != -1:
					
					findNumber = line.rindex("data")
					
					#print(line[findNumber+5:findNumber+6])
					if number != line[findNumber+5:findNumber+6]:
						cont = 0
						contentro+=1

					number = line[findNumber+5:findNumber+6]

					line2 = line[:line.rindex('/')]
					newfile = line2+"/"+"0"+str(cont)+".jpg"
					#print(line)
					#print(newfile)
					os.rename(line, newfile )
					cont+=1
					
	
	def getGrapichHistogram(self,frame,concatenate=True):
		bgr_planes = cv2.split(frame)
		histSize = 256
		histRange = (0, 256) # the upper boundary is exclusive
		accumulate = False
		b_hist = cv2.calcHist(bgr_planes, [0], None, [histSize], histRange, accumulate=accumulate)
		g_hist = cv2.calcHist(bgr_planes, [1], None, [histSize], histRange, accumulate=accumulate)
		r_hist = cv2.calcHist(bgr_planes, [2], None, [histSize], histRange, accumulate=accumulate)
		hist_w = 512
		hist_h = 400
		bin_w = int(np.round( hist_w/histSize ))
		histImage = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
		cv2.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
		cv2.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
		cv2.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
		for i in range(1, histSize):
			cv2.line(histImage, ( bin_w*(i-1), hist_h - int(np.round(b_hist[i-1])) ),
					( bin_w*(i), hist_h - int(np.round(b_hist[i])) ),
					( 255, 0, 0), thickness=2)
			cv2.line(histImage, ( bin_w*(i-1), hist_h - int(np.round(g_hist[i-1])) ),
					( bin_w*(i), hist_h - int(np.round(g_hist[i])) ),
					( 0, 255, 0), thickness=2)
			cv2.line(histImage, ( bin_w*(i-1), hist_h - int(np.round(r_hist[i-1])) ),
					( bin_w*(i), hist_h - int(np.round(r_hist[i])) ),
					( 0, 0, 255), thickness=2)

		histImage= cv2.resize(histImage,(200,100))
		if not(concatenate):
			return histImage

		x_offset= int(frame.shape[1]/2)
		y_offset=0
		frame[y_offset:y_offset+histImage.shape[0], x_offset:x_offset+histImage.shape[1]] = histImage

		return frame

	def cleanJson(self,json):
		print(json)


	def saveVideoAnalyse(self,rgn):
		frame = cv2.imread(rgn[0])
		frame = np.concatenate((frame, frame), axis=1)
		#fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		#out = cv2.VideoWriter("video.avi", fourcc, 10,(frame.shape[1], frame.shape[0]), True)

		for img in rgn:
			frame =cv2.imread(img)
			
			dets = self.detector(frame)
			print("Number of plants detected: {}".format(len(dets)))
			for k, d in enumerate(dets):
				cv2.rectangle(img_output, (d.left(),d.top() ), (d.left() + d.width(), d.top() + d.height()), (0, 255, 0), 2)
				print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
					k, d.left(), d.top(), d.right(), d.bottom()))

			cv2.imshow("dects",img_output)
			cv2.waitKey(5000)

			src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			dst = cv2.equalizeHist(src)

			img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

			# equalize the histogram of the Y channel
			img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

			# convert the YUV image back to RGB format
			img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
			
			frame = self.getGrapichHistogram(frame)
			img_output = self.getGrapichHistogram(img_output)

			frame = np.concatenate((frame, img_output), axis=1)


			cv2.imshow("rgnImage",frame)

			#out.write(frame)

			#cv2.imshow('calcHist Demo', histImage)
			#cv2.imshow("hist",img_output)

			cv2.waitKey(1)

			# if cv2.waitKey(1) & 0xFF == ord('q'):
			# 	break
	
	def Hist_and_Backproj(self,val):

		hsv = cv2.cvtColor(self.tempImage, cv2.COLOR_BGR2HSV)
		ch = (0, 0)
		hue = np.empty(hsv.shape, hsv.dtype)
		cv2.mixChannels([hsv], [hue], ch)
	
		bins = val
		histSize = max(bins, 2)
		ranges = [0, 180] # hue_range
		
		
		hist = cv2.calcHist([hue], [0], None, [histSize], ranges, accumulate=False)
		cv2.normalize(hist, hist, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
		
		
		backproj = cv2.calcBackProject([hue], [0], hist, ranges, scale=1)
		
		
		cv2.imshow('BackProj', backproj)
		
		
		w = 400
		h = 400
		bin_w = int(round(w / histSize))
		histImg = np.zeros((h, w, 3), dtype=np.uint8)
		for i in range(bins):
			cv2.rectangle(histImg, (i*bin_w, h), ( (i+1)*bin_w, h - int(np.round( hist[i]*h/255.0 )) ), (0, 0, 255), cv2.FILLED)
		cv2.imshow('Histogram', histImg)
		



	def cleanValue(self,pixel):
		if pixel < 0 :
			return 0

		return pixel

	def analysePlant(self, img, debug=False):

		grayscaled = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2GRAY)
		retval, threshold = cv2.threshold(img.copy(), 50, 255, cv2.THRESH_BINARY)
		th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 125, 1)
		gh = self.getGrapichHistogram(img.copy(),False)
		im2, contours, hierarchy = cv2.findContours(th.copy() ,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		self.tempImage = img

		#window_image = 'original'
		#cv2.namedWindow(window_image)
		bins = 25
		#cv2.createTrackbar('* Hue  bins: ', window_image, bins, 180, self.Hist_and_Backproj )
		#self.Hist_and_Backproj(bins)

		dets = self.detector(img)
		detsFrame = img.copy()
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(detsFrame,str(len(dets)),(0,50), font, 1,(255,255,255),2,cv2.LINE_AA)

		# To show the new detections
		if debug:			
			for k, d in enumerate(dets):
					x = self.cleanValue(d.left())
					y = self.cleanValue(d.top())
					w = self.cleanValue(d.width())
					h = self.cleanValue(d.height())

					cv2.rectangle(detsFrame, (d.left(),d.top() ), (d.left() + d.width(), d.top() + d.height()), (0, 255, 0), 2)
					print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
						k, d.left(), d.top(), d.right(), d.bottom()))

		gray = cv2.bilateralFilter(grayscaled, 11, 17, 17)
		edged = cv2.Canny(gray, 30, 200)

		im2, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
		#cnts = imutils.grab_contours(cnts)
		#cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
		screenCnt = []
		# This image is temporal for find the back projection value
		
		for c in contours:
			peri = cv2.arcLength(c, True)
			if peri > 400:
				screenCnt.append(c)
				#   print("entro")
			
		#cv2.drawContours(frame, cnts, -1, (0,255,0), 3)
		#cv2.drawContours(img, contours, -1, (0,255,0), 3)
		cantContornos = len(screenCnt)
		cantDets = len(dets)
		valueResponse = True

		if cantContornos == 0 and cantDets == 0:
			valueResponse = False
		elif cantContornos > 7:
			valueResponse = False

		if debug:
			frame = img.copy()
			cv2.putText(frame,str(len(screenCnt)),(0,50), font, 1,(255,255,255),2,cv2.LINE_AA)
			cv2.drawContours(frame, screenCnt, -1, (0, 255, 0), 3)
			cv2.imshow('original',img)
			cv2.imshow('detsFrame',detsFrame)
			cv2.imshow('cnts2',frame)
			cv2.imshow('threshold',threshold)
			cv2.imshow('Adaptitive threshold',th)
			cv2.imshow('graphicH',gh)

		
		
			cv2.waitKey(35000)
		# print("---------------------------------")
		# print("Response"+str(valueResponse))
		# print("contornos"+str(cantContornos))
		# print("cantDets"+str(cantDets))
		# print("---------------------------------")
		return valueResponse




	def cleanRe(self,frame):

		x = frame.shape[0]
		y = frame.shape[1]
		ch = frame.shape[2]
		
		dets = self.detector(frame)
		newFrame = np.zeros((x,y,ch),np.uint8)
		#print("Number of plants detected: {}".format(len(dets)))
		for k, d in enumerate(dets):
			x = self.cleanValue(d.left())
			y = self.cleanValue(d.top())
			w = self.cleanValue(d.width())
			h = self.cleanValue(d.height())

			crop_img = frame[y:y+h, x:x+w]

			decision = self.analysePlant(crop_img)
			if decision:
				x_offset= x
				y_offset= y

				newFrame[y_offset:y_offset+crop_img.shape[0], x_offset:x_offset+crop_img.shape[1]] = crop_img

			cv2.rectangle(frame.copy(), (d.left(),d.top() ), (d.left() + d.width(), d.top() + d.height()), (0, 255, 0), 2)
			#print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
				#k, d.left(), d.top(), d.right(), d.bottom()))

		#Save in the image path the new photo
		#cv2.write(img,newFrame)

		
		cv2.imshow("dects",frame)

		cv2.waitKey(10000)
		return newFrame


	def cleanRgn(self,frame):

		x = frame.shape[0]
		y = frame.shape[1]
		ch = frame.shape[2]
		
		dets = self.detector(frame)
		newFrame = np.zeros((x,y,ch),np.uint8)
		#print("Number of plants detected: {}".format(len(dets)))
		for k, d in enumerate(dets):
			x = self.cleanValue(d.left())
			y = self.cleanValue(d.top())
			w = self.cleanValue(d.width())
			h = self.cleanValue(d.height())

			crop_img = frame[y:y+h, x:x+w]

			decision = self.analysePlant(crop_img)
			if decision:
				x_offset= x
				y_offset= y

				newFrame[y_offset:y_offset+crop_img.shape[0], x_offset:x_offset+crop_img.shape[1]] = crop_img

			cv2.rectangle(frame.copy(), (d.left(),d.top() ), (d.left() + d.width(), d.top() + d.height()), (0, 255, 0), 2)
			#print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
			#	k, d.left(), d.top(), d.right(), d.bottom()))

		#Save in the image path the new photo
		#cv2.write(img,newFrame)

		
		cv2.imshow("dects",frame)

		cv2.waitKey(10000)
		return newFrame

	def analyseRgbPlant(self, img, debug=False):

		ORANGE_MIN = np.array([5, 50, 50],np.uint8)
		ORANGE_MAX = np.array([25, 255, 255],np.uint8)

		hsv_img = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2HSV)
		frame_threshed = cv2.inRange(hsv_img, ORANGE_MIN, ORANGE_MAX)

		cv2.imshow("thresh",frame_threshed)
		cv2.imshow("img",img)		

		for x in range(0,img.shape[0]):
			for y in range(0,img.shape[1]):
				r,g,b = img[x,y]
				if (r > 200 or g > 200 or b > 200) or ((r<80 and g<10  and b<80)and(r<200 and g<250 and b<200)):
					img[x,y]=0


		cv2.imshow("newFrame",img)
				

		valueResponse = False

		return valueResponse

	def cleanRgb(self, frame):
		decision = self.analyseRgbPlant(frame,False)
		cv2.waitKey(100000)
		return frame

	def cleanJson(self, json):
		return json


	def cleanFiles(self,folder):

		json,rgb,re,rgn, idk = self.findTypes4Clean(folder)
		# clean the rgn images
		#loop for clean all the re images
		# for e in re:
		# 	frame =cv2.imread(e)
		# 	print(frame.shape[2])
		# 	cleanFrame = self.cleanRe(frame)
		# 	cv2.imshow("newFrame",cleanFrame)
		# 	print(e)


		# # loop for clean all the re images
		# for n in rgn:
		# 	frame =cv2.imread(n)
		# 	print(frame.shape[2])
		# 	cleanFrame = self.cleanRgn(frame)
		# 	cv2.imshow("newFrame",cleanFrame)
		# 	print(n)


		for b in rgb:
			frame = cv2.imread(b)
			cleanFrame = self.cleanRgb(frame)
			
			print(b)		


		for j in json:
			Json = self.cleanJson(j)
			print(j)




		

p = preprocessData(args.fp, args.ap)
#p.extractFiles()
p.cleanFiles(args.ap)









# Para comparar el número original de archivos
# json,rgb,re,rgn, idk = p.findTypes(args.fp)
# print(len(json))
# print(len(rgb))
# print(len(re))
# print(len(rgn))
# print(len(idk))




