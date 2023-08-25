# Python program to capture frames from the ThunderOptics M-spectrophotometer
# extract spectrum and display in real time
# use opencv for image manipulation, matplotlib for plotting
#
# This version expects the camera parameters to be in a file named "TO_Mcam.dat" in the folder
# Example file data (order of lines is immaterial, except the first title line)
'''
#sensor constants and settings for Thunder Optics M-spectrometer 8/7/2023
gain 300
exposure 0
x-scale 360.103489 0.25480527 2.51627e-5 -8.266e-9
ROI 406 434 0 1920
'''
# S. James Remington 8/2023

import cv2
import numpy as np
import matplotlib.pyplot as mp 
from time import time, gmtime, strftime 

mp.ion()  #enable interactive mode, nonblocking figures
naks = 0 #frame read errors
np.set_printoptions(precision=2) # print floats to two decimal places

# declare/define a video capture object
vid = cv2.VideoCapture(0)
if not vid.isOpened():
    print("Cannot open camera")
    exit()
 
# report settings of connected USB camera 
print('Attached camera settings:')
print ('backend name:',vid.getBackendName())
print ('auto exposure: ',vid.get(cv2.CAP_PROP_AUTO_EXPOSURE))
print ('width: ',vid.get(cv2.CAP_PROP_FRAME_WIDTH))
print ('height: ',vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
print ('gain: ', vid.get(cv2.CAP_PROP_GAIN))
print ('exposure: ',vid.get(cv2.CAP_PROP_EXPOSURE))

#initialize camera parameter dictionary to defaults
params = {
    "exposure": -1,
    "gain": 500,
    "x-scale": [0.0,1.0 ,0.0, 0.0],
    "ROI": [406, 434,0,1920]
    }

#update parameters from user file TO_Mcam.dat
# Open file
f = open('TO_Mcam.dat', 'r')
# Read and print title line
header1 = f.readline()
print(header1)

# Loop over lines and extract setting variables
for line in f:
    line = line.strip()
    columns = line.split()
    data = []
    for j in range (1,len(columns)):
        data.append(float(columns[j])) #setting values
    update={columns[0]:data} #dictionary entry for update
    #print('update: ',update)
    params.update(update) #update the defaults

print("\nUpdated parameters:")
for k,v in params.items():
    print(k,v)

# set exposure and gain
exposure = params['exposure'][0]
vid.set(cv2.CAP_PROP_EXPOSURE, exposure)
gain = params['gain'][0]
vid.set(cv2.CAP_PROP_GAIN,gain)

n=0  #initialize frame number
x_start=int(params['ROI'][2]) #wavelength axis
x_end=int(params['ROI'][3]) 

x = np.array(range(x_start,x_end),dtype=float) #X axis default = array index
xs = x #to be scaled

# wavelength axis scaling constants from supplied M-spec calibration (nm)
A = params['x-scale'][0]
B = params['x-scale'][1]
C = params['x-scale'][2]
D = params['x-scale'][3]

# set up plot axis scale in nanometers
for i in range(x_start,x_end):
    xs[i] = A + B*x[i] + C*x[i]*x[i] + D*x[i]*x[i]*x[i]

# region of interest Y bounds (indexed from top left, down)
y_start = int(params['ROI'][0])
y_end = int(params['ROI'][1])

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
    spec = f.sum(axis=0)  #integrate spectrum vertical axis

    #ignore empty return values, which happens with long exposures
    if spec[0] > 0:
        n=n+1
        now = int(time()*1000)
        print('[',now-start,'] frame',n)
        start = now
        
        # Display the resulting frame as image
        cv2.imshow('ROI', f)

        # 'q' key quits (focus must be on frameROI window)
        # 's' save data  (ditto)
        # 'u' or 'd' to increase/decrease exposure one stop
        key = cv2.waitKey(1) & 0xFF
    
        if key == ord('q'):
            print('keyboard interrupt, quitting')
            break

        # plot spectrum
        mp.cla()  #clear plot field
        mp.plot(xs,spec) #plot data
        mp.suptitle('Frame '+str(n))
        mp.pause(0.1) #pause required for display to appear

        if key == ord('s'): #write out spectrum to disk
            key = 0 #once only
            filename="spec"+str(n)+".txt"
            s_datetime =  strftime("%Y-%m-%d %H:%M:%S", gmtime())
            try:    
                with open( filename,'w') as output_file:
                    output_file.write(s_datetime+","+str(exposure)+","+str(gain)+"\n")  #title line with date/GMT/exposure setting
                    for i in range(1920):
                        sxs = '{:.2f}'.format(xs[i])
                        line = sxs+","+str(spec[i])+"\n"  #.csv format wavelength, intensity
                        output_file.write(line)
                    output_file.close()
                    print(">>> " + filename + " written")
            except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
                print ('>>>output file open failure')
                break
    else:
        naks = naks+1
        continue

    #interactive exposure adjustment
    if key == ord('u'):
        exposure = exposure+1
        vid.set(cv2.CAP_PROP_EXPOSURE, exposure)
        print(">>> exposure",exposure)
    if key == ord('d'):
        exposure = exposure-1
        vid.set(cv2.CAP_PROP_EXPOSURE, exposure)
        print(">>> exposure",exposure)
    key = 0  #clear command

# done, release the video object
print('Empty frames: ', naks)  #report number of empty image frames
vid.release()
# destroy windows before exit
cv2.destroyAllWindows()
