import heapq
from typing import List

from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import initial_database as init_db
from teamproject_car import car
from teamproject_car.car import Car
import numpy as np

conn = psycopg2.connect(dbname=init_db.database, user=init_db.username, password=init_db.pwd, host=init_db.hostname)


class Parking_System:

    # Car_ID of car that's we current operating for loggers
    def __init__(self):
        self.ID_car = None

    # from list of coordinates of parking, it finds the closest parking
    def find_closest_parking(self, points: List[List[np.longdouble]], current_point: List[np.longdouble]) -> List[
        List[np.longdouble]]:
        minHeap = []
        for xp, yp in points:
            # For others point that (0,0) it's sqrt((xp-xs)**2+(xp-xs)**2)
            dist = ((xp - current_point[0]) ** 2) + ((yp - current_point[1]) ** 2)
            dist = np.sqrt(dist)
            minHeap.append([dist, xp, yp])
        heapq.heapify(minHeap)

        dist, x, y = heapq.heappop(minHeap)
        res = [x, y]
        str_res = str(res[0]) + "," + str(res[1])
        return str_res

    # Returns ID_parking !closes working
    def find_closest_parking_with_free_space(self, check_for_charging_points: bool, location, ID_car: str) -> str:
        init_no_space = True
        self.ID_car = ID_car

        # retrieve all coordinates of parkings
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''select coordination from parking;''')
        all_coordinates = cur.fetchall()
        cur.close()

        # maping coordinates for desirable state (List[List[np.double]])
        list_of_all_coordinates = []
        for point in all_coordinates:
            list_of_all_coordinates.append(list(map(np.double, point[0].split(','))))
        while init_no_space:

            coordinates_of_nearest_parking = self.find_closest_parking(list_of_all_coordinates, location)

            # find sector of nearest_parking
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(
                '''SELECT "sector_name" from sector WHERE "ID_parking" = (SELECT "ID_parking" FROM Parking WHERE coordination=(%s));''',
                (coordinates_of_nearest_parking,))
            list_of_sectors = cur.fetchall()
            cur.close()

            sector_name = ' '
            # check if in this sector there is free space, if isn't check the next one
            for sector in list_of_sectors:
                # retrieving sector name in format '1sector1'
                current_sector_to_check = sector[0]
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(
                    '''select number_of_places, number_of_occupied_places from sector WHERE "sector_name"=(%s);''',
                    (current_sector_to_check,))
                places_from_sector = cur.fetchall()
                cur.close()
                if places_from_sector[0][0] > places_from_sector[0][1]:
                    if check_for_charging_points:
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute(
                            '''SELECT "ID_place" FROM Place WHERE EXISTS (SELECT charging_point, place_status, sector_name FROM Place WHERE sector_name=(%s) AND place_status='free' AND charging_point='t');''',
                            (sector_name,))
                        possible_places = cur.fetchall()
                        cur.close()
                        if possible_places is None:
                            continue
                    print(f"[{self.ID_car}]In sector {current_sector_to_check} there is available spot")
                    sector_name = current_sector_to_check
                    break
                else:
                    print(
                        f"[{self.ID_car}]In sector {current_sector_to_check} there is NO available spot. Searching in next one")
            if check_for_charging_points:
                ID_Place=self.find_space_on_chosen_parking_with_charging_spot(sector_name)
            else:
                ID_Place = self.find_space_on_chosen_parking(sector_name)

            ID_nearest_car = self.find_nearest_parked_car(ID_Place)
            # 1 if you're first car
            if (ID_nearest_car != 1):
                if self.ask_for_car_surroundings(ID_nearest_car) == False:
                    init_no_space = True
                    # If we know that this place is unavailable
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute('''UPDATE place SET place_status='unavailable' WHERE "ID_place"=(%s)''', (ID_Place,))
                    print(f"[{self.ID_car}] Parking spot {ID_Place} is unavailable")
                    conn.commit()
                    cur.close()
                else:
                    init_no_space = False


        # retrieve coordinates for Car
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            '''select start_of_sector_coordinates from sector WHERE sector_name=(%s);''',
            (sector_name,))
        coordinates_for_car = cur.fetchall()
        cur.close()

        result = []
        result.append(ID_Place)
        result.append(coordinates_for_car)

        return result

    # checked
    def reserve_parking_spot(self, spot: str):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''UPDATE place SET place_status='occupied', occupying_car=(%s) WHERE "ID_place"=(%s)''', (self.ID_car, spot,))
        print(f"[{self.ID_car}] Parking spot {spot} is reserved")
        conn.commit()
        cur.close()

    # Checked
    # Finds ID of the nearest parked car (to double-check the surroundings)
    def find_nearest_parked_car(self, spot: str) -> str:

        if spot[len(spot) - 1] == 1:
            print(f"[{self.ID_car}] You are first car on this parking")
            return 1

        change_spot = spot[len(spot) - 1]
        change_spot = int(change_spot)
        change_spot -= 1
        change_spot = str(change_spot)
        spot = spot[:-1] + change_spot
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''select occupying_car from place WHERE "ID_place"=(%s)''', (spot,))
        id_nearest_parked_car = cur.fetchone()
        cur.close()
        return id_nearest_parked_car[0]

    # Waiting for main/start script
    def ask_for_car_surroundings(self, nearest_parked_car) -> bool:
        if Car.ID_car == nearest_parked_car:
            state_of_surroundings = Car.get_surroundings()
        return state_of_surroundings

    # Returns ID_place
    def find_space_on_chosen_parking(self, sector_name: str) -> str:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''SELECT "ID_place" FROM Place WHERE Place.place_status='free' AND sector_name like  (%s)''',
                    (sector_name,))
        id_nearest_free_space = cur.fetchone()
        cur.close()
        print(f"[{self.ID_car}]This is your place {id_nearest_free_space[0]}")
        return id_nearest_free_space[0]

    def find_space_on_chosen_parking_with_charging_spot(self, sector_name: str) -> str:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''SELECT "ID_place" FROM Place WHERE Place.place_status='free' AND charging_point='t' AND sector_name like '1sector3';''',
                    (sector_name,))
        id_nearest_free_space = cur.fetchone()
        cur.close()
        print(f"[{self.ID_car}]This is your place {id_nearest_free_space[0]}")
        return id_nearest_free_space[0]

    def free_parking_spot(self, Id_car):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''UPDATE place SET place_status='free', occupying_car=NULL WHERE occupying_car=(%s)''',
                    (Id_car,))
        print(f"[{Id_car} left parking. This parking spot is free")
        conn.commit()
        cur.close()

    # def report_parked_location(self, current_spot: str) -> bool:
    #     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #     cur.execute("SELECT place_status FROM Place WHERE ID_place=(%s)", (current_spot))
    #     is_available = cur.fetchall()
    #     cur.close()
    #     return is_available
