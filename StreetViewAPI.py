from polyline.codec import PolylineCodec
import urllib.parse
import json
import urllib.request
import urllib.error
import tempfile
import os
from Calculations import calculate_initial_compass_bearing, calculate_pitch
import cv2
import threading

GOOGLE_STREETVIEW_API_KEY = ''

GOOGLE_MAPS_DIRECTIONS_API = 'https://maps.googleapis.com/maps/api/directions/json?'

STREETVIEW_URL = ("http://maps.googleapis.com/maps/api/streetview?"
                  "size=640x480&key=" + GOOGLE_STREETVIEW_API_KEY)


def _build_directions_url(origin, destination) -> str:
    query_paramaters = [('origin', origin), ('destination', destination), ('key', GOOGLE_STREETVIEW_API_KEY)]
    print(GOOGLE_MAPS_DIRECTIONS_API + urllib.parse.urlencode(query_paramaters))
    return GOOGLE_MAPS_DIRECTIONS_API + urllib.parse.urlencode(query_paramaters)


def get_result(url: str) -> 'json':
    """parses the json"""
    response = None
    try:
        response = urllib.request.urlopen(url)
        json_text = response.read().decode(encoding='utf-8')

        return json.loads(json_text)

    finally:
        if response is not None:
            response.close()


def build_coords(json) -> list:
    # Builds coords from the polylines
    result = []
    for i in json['routes'][0]['legs'][0]['steps']:
        result.extend(PolylineCodec().decode(i['polyline']['points']))
    return result


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def get_heading(start, end):
    return '{0:.4f}'.format(calculate_initial_compass_bearing(start, end))


class StreetViewThread(threading.Thread):
    def __init__(self, coordinates, pointindex, centercoord, height, driveby):
        threading.Thread.__init__(self)
        self.coordinates = coordinates
        self.pointindex = pointindex
        self.result = []
        self.driveby = driveby
        self.centercoord = centercoord
        self.height = height

    def run(self):
        for idx, coord in tuple(enumerate(self.coordinates))[:-3]:
            # -3 doesn't iterate through overlapping list. (for heading).
            # I lose 3 coords, tiny sacrifice.
            try:
                outfile = tempfile.NamedTemporaryFile(delete=False,
                                                      prefix=("{0:06}".format(self.pointindex + idx) + '__'))
                outfile.close()


                if self.driveby == "True":
                    heading = get_heading(coord, self.centercoord)
                    pitch = calculate_pitch(self.centercoord, coord, self.height)
                else:
                    heading = get_heading(coord, self.coordinates[idx + 3])
                    pitch = 0

                url = "{}&location={},{}&heading={}&pitch={}".format(STREETVIEW_URL, coord[0], coord[1], heading,
                                                                     pitch)  # coord,next_coord
                # Since I broke the coords list into chunks for different workers it can't look at the next coords at the end
                # of a single chunk. There has to be some overlap. So I added 3 from the next chunk into this chunk while
                # ending before the overlap.
                # [COORD1,COORD2,COORD3,COORD4,COORD5,COORD6],[COORD4,COORD5,COORD6,COORD7....]
                #                     ^Stops iterating here

                urllib.request.urlretrieve(url, outfile.name)
                self.result.append(outfile.name)

                print('{:.1%}'.format(idx / len(self.coordinates)))
            except urllib.error.URLError:
                os.unlink(outfile.name)


def streetview_thread(coordinates, driveby="False", centercoord=(0, 0), height=0.0):
    NUMBEROFTHREADS = 20
    slicedlist = [coordinates[i:i + (len(coordinates) // NUMBEROFTHREADS) + 3] for i in
                  range(0, len(coordinates), len(coordinates) // NUMBEROFTHREADS)]
    result_path = []
    threads = []
    for i in range(NUMBEROFTHREADS):
        t = StreetViewThread(slicedlist[i], (len(slicedlist[0]) * i), centercoord, height, driveby)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
        result_path.extend(t.result)
    return sorted(result_path, key=str)


def make_video(images, output_path, fps=16, size=(640, 480), is_color=True):
    """
    Create a video from a list of images.
    """

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    vid = cv2.VideoWriter(output_path, fourcc, fps, size, is_color)
    for image in images:
        img = cv2.imread(image)
        vid.write(img)
    vid.release()
    cv2.destroyAllWindows()


def construct_video():
    start = input('Input Origin: ')
    end = input('Input Destination: ')
    driveby = input('Look around an object? Type True or False: ')

    if driveby == "True":
        centercoord = tuple([float(i) for i in (input("Give object coordinate:")).split(",")])
        height = float(input("Give object height in km:"))
        outputname = input('Name of File: \n') + ".avi"
        imagelocations = streetview_thread(build_coords(get_result(_build_directions_url(start, end))), driveby,
                                           centercoord, height)
    else:
        outputname = input('Name of File: \n') + ".avi"
        imagelocations = streetview_thread(build_coords(get_result(_build_directions_url(start, end))))

    print(imagelocations)
    # TODO:
    # Better location input.
    make_video(imagelocations, 'D://Video Output//' + outputname)

# TODO:
# IDEA: POINT AT INTERESTING OBJECT. IF COORDS ARE WITHIN THE RADIUS OF OBJECT POINT TO IT INSTEAD OF AHEAD OF VEHICLE.
##Figure out how to USE JAVASCRIPT API TO CALL StreetViewService
# cntower
# 43.638891, -79.456817 Start
# 43.683613, -79.361742 End
# 43.642391, -79.387015 Tower