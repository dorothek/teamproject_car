from parking_system import Parking_System
from car import Car
import fill_places_randomly
import psycopg2
import initial_database
import random
import string


def random_ID():  # creating a unique car ID
    car_marka = ['Toyota', 'Citroen', 'Peugeot', 'Renault', 'Kia', 'Honda', 'Hyundai', 'Audi', 'Volkswagen', 'BMW', 'Tesla']
    letters = string.ascii_uppercase
    return str(random.choice(car_marka)) + random.choice(letters) + random.choice(letters) + str(
        random.randrange(100, 1000, 3))

def generateCar():
    xCor = random.uniform(54.590000, 54.620000)
    yCor = random.uniform(18.200000, 18.280000)
    energyLvl = random.uniform(0.1, 0.99)
    return Car(False, random_ID(), (xCor,yCor), round(energyLvl))




if __name__ == '__main__':
    # get password and db name
    # databaseName = input('Database name: ')
    # PWD = input('Database password: ')
    # ------------------------------------------------------------------------
    # DB DATA
    hostname = 'localhost'
    database = 'teamproject_car'
    username = 'postgres'
    pwd = 'Czemuja?1'
    port_id = 5432
    conn = None
    # ------------------------------------------------------------------------
    # initialize db
    # firstly you have to create an empty PostgreSQL database (using pgAdmin)
    # after creating change the variable database and pwd to what you have set (and other information if needed)

    # initial_database.initDatabase(hostname, database, username, pwd, port_id, conn)

    # ------------------------------------------------------------------------
    # fill db

    # fill_places_randomly.fillPlacesRandomly(hostname, database, username, pwd, port_id, conn)

    # ------------------------------------------------------------------------
    # create db connection

    conn = psycopg2.connect(dbname=database, user=username, password=pwd, host=hostname)

    # get parked cars

    # generate random moving cars
    movingCars = list()
    for i in range(10):
        movingCars.append(generateCar())
    print(movingCars)

    # create parking system

    PS = Parking_System(conn)

    # symulate few cars

    movingCars[0].search_for_parking_spots(PS)
    movingCars[0].leave_parking_spot(PS)