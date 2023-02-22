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

    print("----------------------- Initializing Database -----------------------")
    initial_database.initDatabase(hostname, database, username, pwd, port_id, conn)
    print("----------------------- Database Initialized Successfully -----------------------")
    # ------------------------------------------------------------------------
    # fill db

    print("----------------------- Filling Database with cars -----------------------")
    fill_places_randomly.fillPlacesRandomly(hostname, database, username, pwd, port_id, conn)

    # ------------------------------------------------------------------------
    # create db connection

    print("----------------------- Connecting to database -----------------------")
    conn = psycopg2.connect(dbname=database, user=username, password=pwd, host=hostname)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # get parked cars
    print("----------------------- Creating Cars objects from the database -----------------------")
    cur.execute("""SELECT "ID_car" FROM car ORDER BY RANDOM() LIMIT 30;""")
    results = cur.fetchall()

    parkedCars = [Car(True, result[0]) for result in results]
    cur.close()

    # generate random moving cars
    print("----------------------- Generating moving cars -----------------------")
    movingCars = list()
    for i in range(30):
        movingCars.append(generateCar())

    # # create parking system

    print("----------------------- Connecting Parking System to database -----------------------")
    PS = Parking_System(conn)

    # simple "dummy" symulation
    print("----------------------- Beginning simulation -----------------------")
    for i in range(30):
        print("----------------------- New car looking for a parking place -----------------------")
        movingCars[i].search_for_parking_spots(PS)
        print("----------------------- Car leaving the parking -----------------------")
        parkedCars[i].leave_parking_spot(PS)


    conn.close()