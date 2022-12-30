from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import initial_database as init_db

conn = psycopg2.connect(dbname=init_db.database, user=init_db.username, password=init_db.pwd, host=init_db.hostname)


class Parking_System:

    # Returns ID_parking
    def find_closest_parking_with_free_space(self) -> int:
        pass

    def reserve_parking_spot(self, spot: int):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("UPDATE place_status SET TRUE WHERE ID_place (%s)", (spot))
        flash("Parking spot is reserved")
        conn.commit()
        cur.close()

    # Finds ID of the nearest parked car (to double-check the surroundings)
    def find_nearest_parked_car(self) -> int:
        pass

    def ask_for_car_surroundings(self, spot: int) -> bool:
        pass

    # def find_parking_space(self) -> str:
    #     pass

    # Returns ID_place
    def find_space_on_chosen_parking(self, space: int) -> int:
        pass


    def report_parked_location(self, current_spot: int) -> bool:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT place_status FROM Place WHERE ID_place=(%s)", (current_spot))
        is_available = cur.fetchall()
        cur.close()
        return is_available
