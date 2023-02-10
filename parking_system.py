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

#TO-DO

#Correct find_nearest_parked_car(self, spot: str) (for now it doesn't work when particular space is unavaible
#Add searching sectors



class Parking_System:

    #from list of coordinates of parking, it finds the closest parking
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
    def find_closest_parking_with_free_space_id_place(self, ID_parking: str, location) -> str:
        init_no_space = True

        #retrieve all coordinates of parkings
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''select coordination from parking;''')
        all_coordinates = cur.fetchall()
        cur.close()

        #maping coordinates for desirable state (List[List[np.double]])
        list_of_all_coordinates = []
        for object in all_coordinates:
            list_of_all_coordinates.append(list(map(np.double, object[0].split(','))))
        while(init_no_space):

            coordinates_of_nearest_parking = self.find_closest_parking(list_of_all_coordinates, location)

            #find sector of nearest_parking
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('''SELECT "sector_name" from sector WHERE "ID_parking" = (SELECT "ID_parking" FROM Parking WHERE coordination=(%s);''', (coordinates_of_nearest_parking, ))
            list_of_sectors = cur.fetchall()
            cur.close()

            #check if in this sector there is free space




            #For testing
            sector_name = '1sector1'

            ID_Place = self.find_space_on_chosen_parking(sector_name)
            ID_nearest_car = self.find_nearest_parked_car(ID_Place)
            # 1 if you're first car
            if(ID_nearest_car!=1):
                if self.ask_for_car_surroundings(ID_Place) == False:
                    init_no_space=True
                    #If we know that this place is unavailable
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute('''UPDATE place SET place_status='unavailable' WHERE "ID_place"=(%s)''', (ID_Place,))
                    print("Parking spot is unavailable")
                    conn.commit()
                    cur.close()
                else:
                    init_no_space=False

        return ID_Place

    def find_closest_parking_with_free_space(self):
       # ID_place = self.find_closest_parking_with_free_space_id_place()
       pass

    #checked
    def reserve_parking_spot(self, spot: str):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''UPDATE place SET place_status='occupied' WHERE "ID_place"=(%s)''', (spot,))
        print("Parking spot is reserved")
        conn.commit()
        cur.close()

    #Checked
    # Finds ID of the nearest parked car (to double-check the surroundings)
    def find_nearest_parked_car(self, spot: str) -> str:

        if (spot[len(spot) - 1] == 1):
            print("You are first car on this parking")
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
        return id_nearest_parked_car
#Waiting for main/start script
    def ask_for_car_surroundings(self, spot: str, nearest_parked_car) -> bool:
        #? Trzeba stworzyć obiekt Car, żeby się dostać
        if (Car.ID_car==nearest_parked_car):
            state_of_surroundings = Car.get_surroundings()
        return state_of_surroundings




    #Returns ID_place
    def find_space_on_chosen_parking(self, sector_name: str) -> str:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # ID_parking = str(ID_parking)
        # ID_parking += '%'
        cur.execute('''SELECT "ID_place" FROM Place WHERE Place.place_status='free' AND sector_name like  (%s)''',
                    (sector_name,))
        id_nearest_free_space = cur.fetchone()
        cur.close()
        print("This is your place:", id_nearest_free_space)
        return id_nearest_free_space

    def free_parking_spot(self, Id_Car: str):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('''UPDATE place SET place_status='free', occupying_car=NULL WHERE occupying_car=(%s)''', (Id_Car,))
        print("Parking spot is free")
        conn.commit()
        cur.close()


    # def report_parked_location(self, current_spot: str) -> bool:
    #     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #     cur.execute("SELECT place_status FROM Place WHERE ID_place=(%s)", (current_spot))
    #     is_available = cur.fetchall()
    #     cur.close()
    #     return is_available
