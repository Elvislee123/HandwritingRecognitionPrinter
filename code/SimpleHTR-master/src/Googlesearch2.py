#activated when Button is pressed
from time import sleep
from gpiozero import LED
#Controlling the lights for feedback
led1 = LED(3)
led2 = LED(4)
#pre-Recognition light sequence
for i in range(5):
	led1.on()
	sleep(0.2)
	led1.off()

import Snap
import imgprocess

#end of phase 1 light sequence
for i in range(1):
    led1.on()
    sleep(3)
    led1.off()

#beginning of phase 2 LED sequence
for i in range(5):
    led2.on()
    sleep(0.2)
    led2.off()

import main
import urllib.request
from PIL import Image
import numpy as np
import glob, os
from bs4 import BeautifulSoup as bs
import json
import requests
import random
import RPi.GPIO as GPIO

#possible browsers to search with. 
ua = [
      "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
      ]

#main.X() retrieves the word recognised, which is moved to the end of a url for the image search.
a = main.X()
url = "https://www.google.co.uk/search?hl=en&tbm=isch&source=hp&biw=1536&bih=754&ei=MABBXPGwDYXisAe1_bYg&q=cartoon"+a

C = []

#locating a url for an image from the desired word recognised from the tensorflow recogniser
def link_finder(ua,a,url,C,x):
    print('Finding Link')
    led1.on()
    headers = {"User-Agent": random.choice(ua)}
    req = requests.get(url, headers = headers)
    html = req.content

    soup = bs(html,"lxml")
    images = soup.find_all("div",{"class":"rg_meta"})

    images = [i.text for i in images]
    images = [json.loads(i) for i in images]

    for x in range(100):
        if len(C) == 1:
            break
        Link1 = images[x]
        if Link1["ity"] == 'jpg':
            L = Link1["ou"]
            print(L)
            C.append("finished")
    return L

#retrieving an image using the url requested from Link()
def downloader(image_url):
    print('retrieving image')
    file_name = a
    full_file_name = str(file_name) + '.jpg'
    print(full_file_name)
    print(image_url)
    while True:
        try:
            urllib.request.urlretrieve(image_url,full_file_name)
            break
        except OSError:
            #occasionally images cannot be directly downloaded, usually because of copyright infringement
            print("Im sorry, if we do this, it will be copyright infringement")
    return full_file_name

Link = link_finder(ua, a, url, C = [], x = 0)
Name = downloader(Link)

#a will determine matrix size, currently set as a square but can be modified by changing 'size'
a = 64
size = a, a

for infile in glob.glob(Name):
    file, ext = os.path.splitext(infile)
    im = Image.open(infile)
    New = im.convert('L')
    New.thumbnail(size)
    X = np.array(New)

#thresholding by changing all values below a certain number 'x' to 0 and anything equal or above to a 1
M = [[(0) for x in range(a)] for y in range(a)]
print('thresholding')
led2.on()
for z in X:
    for y in range(len(X)):
        for x in range(len(X[0])):
            A = X[y][x]
            #specified number 'x' is 170, can be modified for different exposures or brightnesses of images
            if A >= 170:
                M[y][x] = 1
            else:
                M[y][x] = 0

#LED sequence for the end of phase 2
for i in range(1):                    
    led2.on()
    sleep(3)
    led2.off()
#LED sequence for beginning of phase 3, printing
for i in range(5):
    led1.on()
    led2.on()
    sleep(0.2)
    led1.off()
    led2.off()

servo = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo,GPIO.OUT)
p = GPIO.PWM(servo,50)

#settting up pins connecting Raspberry pi to motors through the DRV8825
DIR = 20
STEP = 21
CW = 1
CCW = 0
SPR = 20
DIR2 = 5
STEP2 = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)
GPIO.setup(DIR2, GPIO.OUT)
GPIO.setup(STEP2, GPIO.OUT)
GPIO.output(DIR2, CW)

#a selection panel for different resolutions, for smoother movement use finer resolutions such as 1/16 or 1/32
MODE = (14, 15, 18)
MODE2 = (13, 19, 26)
GPIO.setup(MODE, GPIO.OUT)
GPIO.setup(MODE2, GPIO.OUT)
RESOLUTION = {'Full': (0, 0, 0),
		'Half': (1, 0, 0),
		'1/4': (0, 1, 0),
		'1/8': (1, 1, 0),
		'1/16': (0, 0, 1),
		'1/32': (1, 0, 1)}
GPIO.output(MODE, RESOLUTION['1/32'])
GPIO.output(MODE2, RESOLUTION['1/32'])

step_count = SPR * 32 * 6
step_count2 = step_count - 1
Pixel_count = int(step_count / 64)
delay = 0.005 / 32
delay2 = 0.01 / 32

#initially specify Directions of the pair of stepper motors
GPIO.output(DIR, CCW)
GPIO.output(DIR2, CCW)

#line up the stepper motors so they always start off at the same point
for x in range(2*step_count):
	GPIO.output(STEP, GPIO.HIGH)
	GPIO.output(STEP2, GPIO.HIGH)
	sleep(delay)
	GPIO.output(STEP, GPIO.LOW)
	GPIO.output(STEP2, GPIO.LOW)
	sleep(delay)


#start the servo motor at position 12.5
p.start(12.5)
print('printing')

#Moving the stepper motors in the desired way: left to right, then down one pixel, then right to left, and so on
#mimicing a zigzag
for a in range(64):
    row = M[a]
    if (a+1) % 2 != 0:
        #an indication of what line the printing is currently doing. Odd line will move steppers CW or clockwise
        print('odd line')
        for b in range(64):
            #printing line by line, DIR2 controls the horizontal moving stepper motors
            for x in range(Pixel_count):
                GPIO.output(DIR2, CW) #stepcount
                GPIO.output(STEP2, GPIO.HIGH)
                sleep(delay2)
                GPIO.output(STEP2, GPIO.LOW)
                sleep(delay2)
            if row[b] == 0:
                try:
                    for x in range(1):
                        p.ChangeDutyCycle(10)
                        sleep(0.1)
                        p.ChangeDutyCycle(12.5)
                        sleep(0.1)
                except KeyboardInterrupt:
                    GPIO.cleanup()
            else:
                sleep(0.1)
        #move platform down by 1 pixel using DIR (controls the vertical pair of steppers)
        for x in range(Pixel_count):
            GPIO.output(DIR, CW)
            GPIO.output(STEP, GPIO.HIGH) #Pixel_count
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)
    #checking for an even line or odd line
    if (a+1) % 2 == 0:
        #Even line will move steppers CCW or counter-clockwise
        print('even line')
        for b in range(64):
            #inverse indicates moving the printing pen the other direction to save travelling time of 'b' pixels
            inverse = len(M[0]) - b 
            for x in range(Pixel_count):
                #using the GPIO to control stepper motors in CCW direction with delay2 or 0.01/32 second delays
                #for maximum resolution and smooth motion for the stepper motors.
                GPIO.output(DIR2, CCW)
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(delay2)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(delay2)
            #Checking for a 0 within the matrix to tell the printer to make a mark.
            if row[inverse-1] == 0:
                try:
                    for x in range(1):
                        #to make a mark, move the servo motor from potion 10 to 12.5, thus pulling a string.
                        p.ChangeDutyCycle(10)
                        sleep(0.1)
                        p.ChangeDutyCycle(12.5)
                        sleep(0.1)
                except KeyboardInterrupt:
                    GPIO.cleanup()
            else:
                sleep(0.1)
        #after doing 64 pixels, move platform down one pixel
        for x in range(Pixel_count):
            GPIO.output(DIR, CW)
            GPIO.output(STEP, GPIO.HIGH) #Pixel_count
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)

#Final Post printing LED flash
for i in range(1):
    led1.on()
    led2.on()
    sleep(3)
    led1.off()
    led2.off()