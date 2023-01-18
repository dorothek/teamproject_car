import random as rd

# Abstract sensor class
# Every sensor has it's own position on the car (front, left, right, back)
class sensor:
    def __init__(self, position: str):
        self.position = position

    def collectData(self):
        self.distance = -1
        return self.distance


# This type of sensor represents a camera build into automatic car
# It has it's special field - cameraView - holds camera footage
# It can collectData -> get the camera view,
# and interpreate it (to see if there is something blocking the potentially empty parking space)
class camera(sensor):
    def __init__(self, position: str, cameraView):
        self.position = position
        self.cameraView = cameraView

    def collectData(self):
        self.cameraView = 'An image'
        return self.interpretation(self.cameraView)

    # Here in the future will be code that will interpreate the image / or potentailly
    # that could be performed by a car, then this method is not required and camera return an image
    def interpretation(self, image):
        # Here in the future will be code that will interpreate the image
        randomNum = rd.randint(1, 1000)
        if randomNum <= 500:
            return 'empty'
        elif randomNum > 500 and randomNum <= 850:
            return 'car'
        elif randomNum > 850 and randomNum <= 950:
            return 'human'
        else:
            return 'object'


# This type of sensor represents a radar
# It has it's special field - distance -> holds distance from the sensor to the object
# It can collectData -> check how far things are from a car and return this distance
class radar(sensor):
    def __init__(self, position: str, distance: float):
        self.position = position
        self.distance = distance

    def collectData(self):
        self.distance = rd.randint(1, 5)
        return self.distance