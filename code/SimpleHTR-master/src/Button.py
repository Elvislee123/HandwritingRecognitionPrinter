from gpiozero import Button

button = Button(2)
buttonWasPressed = False
buttonWasReleased = False

while True:

	if button.is_pressed:
		buttonWasPressed = True
		break


if buttonWasPressed == True:
	import Googlesearch2.py

