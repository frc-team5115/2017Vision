import math
import time
from networktables import NetworkTable
import cv2
import numpy as np
import os

os.system("uvcdynctrl -s 'Exposure, Auto' 1")
os.system("uvcdynctrl -s 'Exposure (Absolute)' 5")

import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTable.setIPAddress('10.51.15.2')
NetworkTable.setClientMode()
NetworkTable.initialize()

nt = NetworkTable.getTable('pi')

boilercam = cv2.VideoCapture(0)
cam.set(3, 160)
cam.set(4, 120)

gearcam = cv2.VideoCapture(1)
cam.set(3, 160)
cam.set(4, 120)

counter = 0

def getOffsetsGear():
	ret, frame = gearcam.read()
	height, width, channels = frame.shape
	hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
	lower = np.array([0, 150, 50])
	upper = np.array([75, 255, 255])
	thresh = cv2.inRange(hsv, lower, upper)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	maxarea = 0
	almostmaxarea = 0
	centerx1 = 0
	centerx2 = 0
	centerx = 0
	centery1 = 0
	centery2 = 0
	centery = 0
	contour = 0
	
	pixelOffsetX = 0
	pixelOffsetY = 0
	
	for c in contours:
		m = cv2.moments(c)
		if m['m00'] > maxarea:
			centerx1 = m['m10'] / m['m00']
			centery1 = m['m01'] / m['m00']
			maxarea = m['m00']
			contour = c
	
	for c in contours:
		m2 = cv2.moments(c)
		if m2['m00'] > almostmaxarea and m2['m00'] < maxarea:
			centerx2 = m2['m10'] / m2['m00']
			centery2 = m2['m01'] / m2['m00']
			lastmaxarea = m2['m00']
			contour = c
	
	centerx = (centerx1 + centerx2) / 2
		
	pixelOffsetX = centerx - (width / 2)

	#print str(pixelOffsetY)
	#print str(pixelOffsetX)

	angleOffsetX = 45 * pixelOffsetX / width
	return angleOffsetX
	
def getOffsetsBoiler():
	height, width, channels = frame.shape
	hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
	lower = np.array([0, 150, 50])
	upper = np.array([75, 255, 255])
	thresh = cv2.inRange(hsv, lower, upper)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	maxarea = 0
	centerx = 0
	centery = 0
	contour = 0
	
	pixelOffsetX = 0
	pixelOffsetY = 0
	
	for c in contours:
		m = cv2.moments(c)
		if m['m00'] > maxarea:
			centerx = m['m10'] / m['m00']
			centery = m['m01'] / m['m00']
			maxarea = m['m00']
			contour = c
		
	pixelOffsetX = centerx - (width / 2)
	pixelOffsetY = -(centery - (height / 2))

	#print str(pixelOffsetY)
	#print str(pixelOffsetX)

	angleOffsetX = 73 * pixelOffsetX / width
	return angleOffsetX, pixelOffsetY

while True:
	x, y = getOffsetsBoiler()
	gear = getOffsetsGear()

	print str(counter)
	counter += 1

	if ((x == 0) and (y == 0)):
		print("ON TARGET")
	else:
		print str(x)
		print str(y)
		print str(gear)
	if nt.isConnected():
		nt.putNumber('xOffset', x)
		nt.putNumber('yOffset', y)
		nt.putNumber('gearOffset', gear)
		
	time.sleep(.1)
