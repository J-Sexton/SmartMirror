import face_recognition
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import os
import webbrowser
import sys
import picamera
import imutils
import tkinter as tk
import time

import numpy as np

from db import DB

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)

# provide name of image
process_this_frame = True
detect_motion = True
is_user_viewing = False

def monitor():
    movement_counter = 0
    camera = picamera.PiCamera()
    rawCapture = PiRGBArray(camera)
    camera.resolution = (320, 240)
    camera.framerate = 30
    time.sleep(0.11)
    firstFrame = None
    #cam = cv2.VideoCapture(0)
    while detect_motion:
        for test in camera.capture_continuous(rawCapture, format="bgr"):
            #frame = cam.read()[1]
            #frame = imutils.resize(frame, width=500)
            testImage = rawCapture.array
            # test_image = rawCapture.array
            cv2.imwrite("test.jpg", testImage)
            #coversts to grey
            frame = testImage

            currentFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            #Performs Gaussian Blure on image
            currentFrame = cv2.GaussianBlur(currentFrame, (25,25), 15)
            cv2.imwrite("grey_blur.jpg", currentFrame)
            # If we have not established a first frame( the basis of all of our motion tracking) then we establish it here
            if firstFrame is None:
                print("Got first frame")
                # Save first frame
                firstFrame = currentFrame
                cv2.imwrite("first.jpg", firstFrame)
                #Starts over
                rawCapture.truncate(0)
                # Starts over
                continue
            # Calculates Agsolute Difference between the first frame and the current frame
            frameDelta = cv2.absdiff(firstFrame, currentFrame)
            #Writes out frameDelta as jpg
            cv2.imwrite("frameDelta.jpg", frameDelta)
            #Does the threshold of the image(may need tweeking depending on environment)
            thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            # Writes out thresh image as thresh.jog
            cv2.imwrite("thresh.jpg", thresh)
            # Finds contours within the thresh image
            (cnts, contours, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:

                area = cv2.contourArea(c)
                # If size of contour is not big enough, ignore it(aka, if the movement is not big enough ignore it)
                if cv2.contourArea(c) < 1000:
                    continue
                # We look for three points of movement within any check
                else:
                    movement_counter += 1
                    print("Movement")
                    # If mwe detect 3 points of movement we begin facial authentication
                    if movement_counter % 3 == 0:
                        #Frame represnets the current frame of the system.
                        #TODO redo facial_authentication_results = facial_authenticate(frame)
                        print ("Try To Authenticate")
                        #rawCapture.truncate(0)
                        #if facial_authentication_results is True:
                        #    print("Success!")
                        #else:
                        #    copyright
            rawCapture.truncate(0)

   ## while True:
   ##     cv2.imshow(window, diffImg(image_minus, image_base, image_plus))
   ##     image_minus = image_base
   ##     image_base = image_plus
   ##     image_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

   ##     key = cv2.waitKey(10)
   ##     if key == 27:
   ##         print("Goodbye")
   ##         break
class Facial:

    def __init__(self, root):
        self.database = DB(root)



    def facial_authenticate(self,image):
        global detect_motion
        cv2.imwrite("test2.jpg", image)
        # Resize frame of video to 1/4 size for faster face recognition processing
        #small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        try:
            user_face_dict = self.get_all_email_images()
            for key in user_face_dict.keys():
                user_image = face_recognition.load_image_file("Images/" + key + ".jpg")
                user_face_encoding = face_recognition.face_encodings(user_image)[0]

                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)
                for face_encoding in face_encodings:
                    match = face_recognition.compare_faces([user_face_encoding], face_encoding)
                    status = "Unknown"

                    if match[0]:
                        status = "Success"
                        print(status + " : "+ key)
                        webbrowser.open_new_tab("http://172.20.10.8:5000/mirror/"+key)
                        detect_motion = False
                        is_user_viewing = True
                        return True
                    else:
                        print(status)
                        break;

                    face_names.append(status)
        except:
            e = sys.exc_info()[0]
            print("<p>Error: %s</p>" % e)

    def captureImage(self,userName):
        global process_this_frame
        camera = picamera.PiCamera()
        rawCapture = PiRGBArray(camera)
        camera.resolution = (320, 240)
        camera.framerate = 30
        time.sleep(1)
        ret_img = None;
        process_this_frame = False
        for image in camera.capture_continuous(rawCapture, format="bgr"):
            print("Image Captured")
            img = rawCapture.array
            cv2.imwrite("Images/"+ userName +".jpg", img)
            ret_img = img
            rawCapture.truncate(0)
        return ret_img

    def get_all_email_images(self):
        emails = self.database.getEmail()
        user_image_dict = {}
        for email in emails:
            a_user_image = face_recognition.load_image_file(email[0] + "/" + email[0] + ".jpg")
            user_image_dict[email[0]] = a_user_image
        return user_image_dict
