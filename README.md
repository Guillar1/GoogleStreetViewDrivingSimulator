# Google Street View Driving Simulator

This Python program will generate a timelapse of a Google Streetview drive between two destinations. It is like being in the driver seat of
a Google Streetview car. It can also focus on a given place by given it it's coordinates and height. It is currently multithreaded, as it makes it
faster to fetch the images from the API. You can give the location in any format that the Google Directions API will be able to accept.

## Dependencies

* Python >=3.6.2
* NumPy
* OpenCV
* Polyline


## Example Interaction
Simple Drive Between Two Locations:

    Input Origin: San Diego
    Input Destination: Los Angeles
    Look around an object? Type True or False: False
    Generating a drive time-lapse
    Please type in name of file: 
    sandiegotolosangeles
    Where do you want to save this file?: 
    D:\Video Output
    ...
    Worker Completion Percentages
    ...
    Video Generated Successfully at D:\Video Output\sandiegotolosangeles.mp4
  
 Sample Drive Focusing on an Object:

    Input Origin: 43.638891, -79.456817
    Input Destination: 43.683613, -79.361742
    Look around an object? Type True or False: True
    Give object coordinate:43.642391, -79.387015
    Give object height in km:0.55
    Name of File: 
    cntower
    Where do you want to save this file?: 
    D:\Video Output
	  ...
    Worker Completion Percentages
    ...
    Video Generated Successfully at D:\Video Output\cntower.mp4


## Youtube Video
[![Google Street View Simulator Video](http://img.youtube.com/vi/77FeNIHuC20/0.jpg)](http://www.youtube.com/watch?v=77FeNIHuC20)
