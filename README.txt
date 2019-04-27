##
An Imperial college Design engineering project 'Gizmo'
Elvis Lee
##

this uses an existing Tensorflow system integrated with image processing and mechatronics to create a handwriting recognition image printer.

Original files:
	Snap.py
	imgprocess.py
	Googlesearch2.py
	Button.py

Modified existing files:
	main.py 
		line 19 'text.jpg'

Existing files:
	Tensorflow handwriting recognition
	https://github.com/githubharald/SimpleHTR

file running order:

	Button.py
		Googlesearch2.py
			Snap.py
			imgprocess.py
			main.py (Tensorflow system)

###
IMPORTANT

To fully utilize this code, you must download training data
this is found though the existing tensorflow system, simply click the link and follow its instructions for dataset training using IAM training data. 
This data will be inputted into:
	code/Simple-HTR-master/data/words
###