'''
Program Name:   Bad Habit Detector
Author:         Tino Nummela
Date:			31.03.2022
'''

# Importing needed modules
import jetson.inference
import jetson.utils
import time
from datetime import datetime

# Initializing model, input source and output source
network = jetson.inference.detectNet(argv=["--model=BadHabits/ssd-mobilenet.onnx", "--labels=BadHabits/labels.txt", "--input-blob=input_0", "--output-cvg=scores", "--output-bbox=boxes"], threshold=0.5)

# Change '/dev/video0' to 'csi://0' if you're using CSI camera.
camera = jetson.utils.videoSource('/dev/video0')

display = jetson.utils.videoOutput('display://0')


# Function to calcultate percentage
def percentageHold():
	global percent
	percent = timeHold / totalTime * 100
	print("\tYou had phone in hand for", "{:.0f}".format(percent), "% of the time program was running.\n\n")


# Function to save most valuable statisics in to text file.
def saveStats():
	timeNow = datetime.now()
	timeNewFormat = timeNow.strftime("%d/%m/%Y %H:%M:%S")
	f = open("bad_habit_statistics.txt", "a")
	f.write("\nSession at " + timeNewFormat + " you used phone for " + "{:.0f}".format(percent) + "% of the total runtime. Total runtime of the program was " + "{:.1f}".format(totalTime) + " seconds.")
	f.close()
	

# Main function
def main():
	# Starting timer and initializing global variables
	start = time.time()	
	global timeHold
	global totalTime
	timeHold = 0
	
	try:
		print("\n WELCOME TO BAD HABIT DETECTOR \n")

		#Creating starting time stamp for counting time phone detected
		startTimeStamp = time.time()

		# While loop for live video feed
		while display.IsStreaming():
			# Setting phoneDetected to false and starting live feed
			phoneDetected = False
			liveFeed = camera.Capture()
			detections = network.Detect(liveFeed)
			display.Render(liveFeed)
			display.SetStatus('Bad Habit Detector | {:.0f} FPS'.format(network.GetNetworkFPS()))

			# For loop for going through classes/labels, easy to scale when more bad habits are added
			for detection in detections:
				label = network.GetClassDesc(detection.ClassID)
				
				# Deciding action when "phone" is detected
				if label == "phone":
					# Counting how long phone is detected
					phoneDetected = True
					newTimeStamp = time.time()
					timeDelta = newTimeStamp - startTimeStamp
					# Adding timeDelta value to timeHold variable
					timeHold += timeDelta
					# Setting startTimeStamp to newTimeStamp, so time.time() resets
					startTimeStamp = newTimeStamp
					print("BAD HABIT DETECTED")
					
				else:
					# Print error if something else is detected
					print("An error occurred")

			# Resets startTimeStamp if phone is not detected
			if phoneDetected == False:
				startTimeStamp = time.time()

	# CTRL+C to stop the program and print statistics
	except KeyboardInterrupt:
		print("\n\n\tProgram ended by the user.\n")
		# Ending timer and doing some calculations at to be printed after program is finished
		end = time.time()
		totalTime = end - start
		withoutPhone = totalTime - timeHold
		print("\tProgram was on for", float("{:.1f}".format(totalTime)), "seconds.")
		print("\tTotal time with phone was", float("{:.1f}".format(timeHold)), "seconds")
		print("\tTotal time without phone was", float("{:.1f}".format(withoutPhone)), "seconds")
		percentageHold()
		saveStats()
		pass


# Calling main function
if __name__ == '__main__':
	main()
