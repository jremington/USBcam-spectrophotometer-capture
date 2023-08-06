# Python program to capture frames from the ThunderOptics M-spectrophotometer
# extract spectrum and display in real time
# use opencv for image manipulation, matplotlib for plotting
# S. James Remington 8/2023

import cv2
import numpy as np
import matplotlib.pyplot as mp 
from time import time, gmtime, strftime 

mp.ion()  #enable interactive mode, nonblocking figures
  
# declare/define a video capture object
vid = cv2.VideoCapture(0)
if not vid.isOpened():
    print("Cannot open camera")
    exit()
 
#set exposure time (seconds, powers of 2)
exposure = 2
vid.set(cv2.CAP_PROP_EXPOSURE, exposure)

# report settings of connected USB camera 
print('Camera settings')
print ('backend name',vid.getBackendName())
print ('auto exposure ',vid.get(cv2.CAP_PROP_AUTO_EXPOSURE))
print ('width ',vid.get(cv2.CAP_PROP_FRAME_WIDTH))
print ('height ',vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
print ('gain ', vid.get(cv2.CAP_PROP_GAIN))
print ('exposure ',vid.get(cv2.CAP_PROP_EXPOSURE))

n=0  #frame number
x = np.array(range(0,1920),dtype=float) #X axis default = array index
xs = x #to be scaled
naks = 0 #frame read errors
# print floats to two decimal places
np.set_printoptions(precision=2)

# axis scaling constants from supplied M-spec calibration (nm)
A = 360.103489
B = 0.25480527
C = 2.51627e-5
D = -8.266e-9

# set up plot axis scale in nanometers
for i in range(1920):
    xs[i] = A + B*x[i] + C*x[i]*x[i] + D*x[i]*x[i]*x[i]

start = int(time()*1000)
# real time spectrum capture and display 
while(True):
      
    # Capture video frame
    ret, frame = vid.read()
    if not ret:
        naks=naks+1
        continue
    # carve out ROI (coordinates are device specific)
    f = np.array(frame[406:434,0:1920,1])

    n=n+1
    now = int(time()*1000)
    print('[',now-start,'] frame',n)
    start = now	
    # Display the resulting frame as image
    cv2.imshow('frameROI', f)
    
    # the 'q' key quits (focus must be on frameROI window)
    # or 's' save data  (ditto)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        print('keyboard interrupt, quitting')
        break
    
    if key == ord('s'): #write out previously collected spectrum to disk
        filename="spec"+str(n-1)+".txt"
        s_datetime =  strftime("%Y-%m-%d %H:%M:%S", gmtime())
        try:    
            with open( filename,'w') as output_file:
                output_file.write(s_datetime+","+str(exposure)+"\n")  #title line with date/GMT/exposure setting
                for i in range(1920):
                    sxs = '{:.2f}'.format(xs[i])
                    line = sxs+","+str(spec[i])+"\n"  #.csv format wavelength, intensity
                    output_file.write(line)
                output_file.close()
                print(">>>" + filename + " written")
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
                print ('>>>output file open failure')
                break

    spec = f.sum(axis=0)  #integrate spectrum vertical axis
    #ignore empty return values, which happens with long exposures
    if spec[0] > 0:
        mp.cla()  #clear plot field
        mp.plot(xs,spec) #plot data
        mp.suptitle('Frame '+str(n))
        mp.pause(0.1) #pause required for display to appear
    else:
        naks = naks+1

# done, release the video object
print('NAKS =', naks)
vid.release()
# destroy windows before exit
cv2.destroyAllWindows()
