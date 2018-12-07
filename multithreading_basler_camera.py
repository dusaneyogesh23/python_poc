
# Python program to illustrate the concept 
# of threading 
# importing the threading module 
import threading
from pypylon import pylon
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import time

path="/tmp/fifo_buffer"

try:
    os.mkfifo(path,0600)
except OSError, e:
    if e.errno != os.errno.EEXIST:
        raise   
    # time.sleep might help here
    pass


flag = 1


def save_basler_frams(): 
    """ 
    function to capture frames from basler camera 
    """
    # Number of images to be grabbed.
    countOfImagesToGrab = 50
    
    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    # Print the model name of the camera.
    #print("Using device ", camera.GetDeviceInfo().GetModelName())

    camera.Width = 640
    camera.Height = 480

    #camera.properties['AcquisitionFrameRateEnable'] = True
    camera.AcquisitionFrameRate= 30
    #camera.ExposureTime= time_exposure

    # Grabing Continusely (video) with minimal delay
    #camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    
    # Start the grabbing of c_countOfImagesToGrab images.
    # The camera device is parameterized with a default configuration which
    # sets up free-running continuous acquisition.
    camera.StartGrabbingMax(countOfImagesToGrab) 
    
    converter = pylon.ImageFormatConverter()
    
    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    
    while camera.IsGrabbing():
        time.sleep(1)
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
         
        if grabResult.GrabSucceeded():
            flag = 0
            print("SizeX: ", grabResult.Width)
            print("SizeY: ", grabResult.Height)
            image = converter.Convert(grabResult)
            img = image.GetArray()
            print(img)
            with open(path, 'wb') as f:
                # b for binary mode
                f.write(img)
                #fifo = open(path, "w")
                #fifo.write(img)
                #fifo.close()
                f.close()
                grabResult.Release()
                time.sleep(1)
        else:
            print("save_basler_frams!!!")
            continue
        # Releasing the resource
        camera.StopGrabbing()

def capture_basler_frames(): 
    """ 
    function to save basler capture frames in the form of images
    """
    total_record=0
    while 1:
        time.sleep(1)
        try:
            with open(path, 'rb') as f:
                jpgdata = f.read()
                if jpgdata == "":
                    total_record += 1
                    filename = str("Example-"+str(total_record)+".jpg")
                    print(filename) 
                    plt.imsave(filename,jpgdata) 
                else:
                    print("in fifo else")
                    continue
        except:
            print("capture_basler_frames!!!") 
            continue

if __name__ == "__main__": 
    # creating thread 
    t1 = threading.Thread(target=capture_basler_frames,) 
    t2 = threading.Thread(target=save_basler_frams,) 
  
    # starting thread 1 
    t1.start() 
    # starting thread 2 
    t2.start() 
  
    # wait until thread 1 is completely executed 
    t1.join() 
    # wait until thread 2 is completely executed 
    t2.join() 
  
    # both threads completely executed 
    print("Done!") 
