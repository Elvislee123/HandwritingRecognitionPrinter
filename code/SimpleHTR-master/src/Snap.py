from picamera import PiCamera
from time import sleep
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

#using the PiCamera to take a photo of the input word, then apply image processing to recognise the word.
camera = PiCamera()
camera.start_preview()
sleep(2)
#captures the image and saves it to the folder src
camera.capture('/home/pi/code/SimpleHTR-master/src/Image.jpg')
camera.stop_preview()

img = Image.open("Image.jpg")
#an initial enhancemnt of the image
en = ImageEnhance.Brightness(img)
img = en.enhance(1.5)

#changing the image to a 200x200 pixel image
size = 200, 200
img.thumbnail(size)

#blurring an image to lower pixel colour discrepencies with name 'white'
white = img.filter(ImageFilter.BLUR).filter(ImageFilter.MaxFilter(15))

#creating instance grey, which is a version of the image but black and white
grey = img.convert('L')

#illuminiation equalizing, as different parts of the page have different brightnesses
# http://stackoverflow.com/a/4632685 
width,height = img.size
impix = img.load()
whitepix = white.load()
greypix = grey.load()
for y in range(height):
    for x in range(width):
        try:
                greypix = min(255, max(255 * impix[x,y][0] / whitepix[x,y][0], 255 * impix[x,y][1] / whitepix[x,y][1], 255 * impix[x,y][2] / whitepix[x,y][2]))
        except ZeroDivisionError:
                print("There is no picture")
                break

#Simple edge enhancement from PIL to make edges sharper 
img = img.filter(ImageFilter.EDGE_ENHANCE)

#Increasing overall brightness by factor 1.2
en2 = ImageEnhance.Brightness(img)
img = en2.enhance(1.2)

#Converting to RGBA to manipulate pixel data
img = img.convert('RGBA')

data = np.array(img)   # "data" is a height x width x 4 numpy array
red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

# Replace red with white... (leaves alpha values alone...)
white_areas = (red == 255) & (blue == 255) & (green == 255)
data[..., :-1][white_areas.T] = (0, 255, 0) # Transpose back needed
data[..., :-1][white_areas.T] = (255, 0, 0)
data[..., :-1][white_areas.T] = (0, 0, 255)

#saving the image as 'img2'
img2 = Image.fromarray(data)
img2.save("Im1.jpg")

#Manipulating the image using its pixels to threshold it in a matrix version (use of numpy.array)
img2 = img2.convert('L')
a = 140
size = a, a
img2.thumbnail(size)
X = np.array(img2)

#creating matrix M to store data
M = [[(0) for x in range(a)] for y in range(a)]
for z in X:
	for y in range(len(X)):
		for x in range(len(X[0])):
			A = X[y][x]
			if A >= 130:
				M[y][x] = 255
			else:
				M[y][x] = 0

#creating image from Matrix M creating an unidenfied 8 bit integer image 
im = Image.fromarray(np.uint8(M))
#saving initial image
im.save('Image1.jpg')
#overriding image after cropping it
area = (0, 0, len(X[0]), len(X))
U = im.crop(area)
U.save('Image1.jpg')

