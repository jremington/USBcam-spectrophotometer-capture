# M-spectrophotometer-capture
Real time spectrum capture and display using Python/OpenCV/Matplotlib

Interactive program to control and capture spectra from the Thunder Optics M-spectrophotometer.

This is a bare-bones Python program intended for aligning optics, with hard-coded options for device selection, wavelength axis scaling, and data file saving.
It captures a full frame and displays the region of interest (ROI) image using OpenCV, integrated the ROI and displays the captured spectrum as an autoscaled plot using Matplotlib. Developed for Windows 10 using Python 3.11. Modify as you see fit!

1. Device selection: video capture device number has to be determined by experiment, as they are arbitrarily chosen by the OS. "0" or "1" are likely choices.
2. Exposure control: integer power of 2, time in seconds. "0" is 1 second, "-1" is 0.5 seconds, etc.
3. Gain control: may be possible, I have not experimented with it.
4. Interactive options: click on the "frameROI" window to bring it into focus. Typing "q" on the keyboard quits the program. Typing "s" on the keyboard saves the current displayed spectrum as an ASCII text file in .csv format. The first line is date/time/exposure time, following lines are wavelength (nm) and intensity.
5. Device specific parameters: A, B, C, D are X-axis wavelength calibration constants for a third order polynomial, supplied with each M-spectrophotomter. ROI is also supplied. These constants were determined from the "settings" page in the Acquire menu of the Spectragryph software package, after loading the device specific calibration file.
