from parking_system import Parking_System


class Car:

    def __init__(self, is_parked: bool, location: str, energy_level: float, ID_car: int):
        self.parking_system = Parking_System()
        self.is_parked = is_parked
        self.location = location
        self.energy_level = energy_level
        self.ID_car = ID_car

    # scanning car surroundings for free parking space, returns True if free space detected
    def get_surroundings(self) -> bool:
        pass

    # searching for available parking spots
    def search_for_parking_spots(self):
        if self.energy_level <= 0.3:
            destination = self.parking_system.find_closest_parking_with_free_space(True)
        else:
            destination = self.parking_system.find_closest_parking_with_free_space(False)
        self.parking_system.reserve_parking_spot(destination)

    # reports parking location, to database, if parking unavailable starts search for another parking spot
    def report_parked_location_car(self):
        if not self.parking_system.report_parked_location(self.location):
            self.search_for_parking_spots()
