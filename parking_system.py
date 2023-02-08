from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import initial_database as init_db
from teamproject_car import car
from teamproject_car.car import Car

conn = psycopg2.connect(dbname=init_db.database, user=init_db.username, password=init_db.pwd, host=init_db.hostname)

#TO-DO
#Search for nearest parking lots from coordinates
#Correct find_nearest_parked_car(self, spot: str) (for now it doesn't work when particular space is unavaible
#Correct raport_parked_location

class Parking_System:
    #working
    def check_if_sector_is_close_to_car(self, all_coordinates, car_location):
        pass

    # Returns ID_parking !closes working
    def find_closest_parking_with_free_space_id_place(self) -> str:
        init_no_space = True
        while(init_no_space):
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT start_of_sector_coordinates FROM Sector")
            all_coordinates = cur.fetchall()
            cur.close()

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT ID_parking FROM Sector WHERE start_of_sector_coordinates==(%s)", )
            ID_parking = cur.fetchall()
            cur.close()


            ID_Place = self.find_space_on_chosen_parking(ID_parking)
            ID_nearest_car = self.find_nearest_parked_car(ID_Place)
            # 1 if you're first car
            if(ID_nearest_car!=1):
                if self.ask_for_car_surroundings(ID_Place) == True:
                    init_no_space=True
                    #If we know that this place is unavailable
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute('''UPDATE place SET place_status='unavailable' WHERE "ID_place"=(%s)''', (ID_Place,))
                    print("Parking spot is unavailable")
                    conn.commit()
                    cur.close()
                else:
                    init_no_space=False
            #double confirms that place is avaible?
        return ID_Place

    def find_closest_parking_with_free_space(self, ID_place: str):
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



    #Checked
    #Returns ID_place
    def find_space_on_chosen_parking(self, ID_parking: int) -> str:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ID_parking = str(ID_parking)
        ID_parking += '%'
        cur.execute('''SELECT "ID_place" FROM Place WHERE Place.place_status='free' AND "ID_place" like  (%s)''',
                    (ID_parking,))
        id_nearest_free_space = cur.fetchone()
        cur.close()
        print("This is your place:", id_nearest_free_space)
        return id_nearest_free_space


    def report_parked_location(self, current_spot: int) -> bool:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT place_status FROM Place WHERE ID_place=(%s)", (current_spot))
        is_available = cur.fetchall()
        cur.close()
        return is_available
