from PIL import Image
import numpy as np
import glob, os

Name = 'Image1.jpg'
size = (140,140)

#using glob (finds path names) to manipulate image - 'Image1.jpg'
for infile in glob.glob(Name):
    file, ext = os.path.splitext(infile)
    New = Image.open(infile)
    #New = im.convert('L')
    New.thumbnail(size)
    X = np.array(New)

#threshold changing pixel values over 200 to 255 and any below 200 to 0
M = [[(0) for x in range(len(X[0]))] for y in range(len(X))]
print('generating threshold')
for z in X:
    for y in range(len(X)):
        for x in range(len(X[0])):
            A = X[y][x]
            if A >= 200:
                M[y][x] = 255
            else:
                M[y][x] = 0

#Finding the boundaries for the word, in aim to create a suitable input for the Tensorflow handwriting recogniser
def Top(M):
    for z in M:
        for y in range(len(M)):
            for x in range(len(M[0])):
                A = M[y][x]
                if A == 0:
                    a1 = y
                    return a1

a1 = Top(M)

def Left(M):
    for z in M:
        for x in range(len(M[0])):
            for y in range(len(M)):
                A = M[y][x]
                if A == 0:
                    a2 = x
                    return a2

a2 = Left(M)

def Right(M):
    for z in M:
        for x in range(len(M[0])):
            for y in range(len(M)):
                A = M[y][len(M[0])-x-1]
                if A == 0:
                    b1 = len(M[0])-x-1
                    return b1

b1 = Right(M)

def Bottom(M):
    for z in M:
        for y in range(len(M)):
            for x in range(len(M[0])):
                A = M[len(M)-y-1][x]
                if A == 0:
                    b2 = len(M)-y-1
                    return b2

b2 = Bottom(M)

#a2, a1, b1, b2 are 2 numbers which will identify the 2 corners of the image containing only the word
#then the image will be cropped exactly to those values.
area = (a2, a1, b1, b2)
cropped_img = New.crop(area)
cropped_img.show()
cropped_img.save("text.jpg")

