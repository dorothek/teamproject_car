from sensor import camera,radar

class Car:

    def __init__(self, is_parked: bool, location: (float, float), energy_level: float, ID_car: str):
        self.sensor_front = camera("front",""), radar("front",-1)
        self.sensor_back = camera("back",""), radar("back",-1)
        self.sensor_left = camera("left",""), radar("left",-1)
        self.sensor_right = camera("right",""), radar("right",-1)
        self.is_parked = is_parked
        self.location = location
        self.energy_level = energy_level
        self.ID_car = ID_car

    # scanning car surroundings for free parking space, returns True if free space detected
    def get_surroundings(self) -> bool:
        parallel_sensors = (self.sensor_front, self.sensor_back)
        perpendicular_sensors = (self.sensor_left, self.sensor_right)
        for sensor in parallel_sensors:
            # if camera sees a human or do not see anything in
            if sensor[0].collectData() in ('empty', 'human'):
                return True
            # if camera sees anything else method checks how far it is
            # returns True if there is enough space in between to parallel parking
            elif sensor[1].collectData() >= 5:
                return True
        for sensor in perpendicular_sensors:
            if sensor[0].collectData() in ('empty', 'human'):
                return True
            # returns True if there is enough space in between to perpendicular parking
            elif sensor[1].collectData() >= 2.5:
                return True
        # if space not found return false
        return False

    # searching for available parking spots
    def search_for_parking_spots(self, parking):
        # if there is low energy level searches for spaces with charging spots
        if self.energy_level <= 0.3:
            destination = parking.find_closest_parking_with_free_space(True, self.location, parking)
        else:
            destination = parking.find_closest_parking_with_free_space(False, self.location, parking)
        # reserving parking space
        parking.reserve_parking_spot(destination)

    # car leaves parking space
    def leave_parking_spot(self, parking):
        parking.leave(self.ID_car)

    # # reports parking location, to database, if parking unavailable starts search for another parking spot
    # def report_parked_location_car(self, parking):
    #     if not Parking_System.report_parked_location(self.location):
    #         self.search_for_parking_spots(parking)
