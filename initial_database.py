import psycopg2.extras
import random
import string

def initDatabase(hostname, database, username, pwd, port_id, conn):

    hostname = hostname
    database = database
    username = username
    pwd = pwd
    port_id = port_id
    conn = conn



    try:
        with psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id) as conn:

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur: #DictCursor enable to use column names while selecting

    ###########################################------------PARKING TABLE-------------#######################################
                cur.execute('DROP TABLE IF EXISTS parking CASCADE')
                create_script='''CREATE TABLE IF NOT EXISTS public.parking
                    (
                        "ID_parking" SERIAL NOT NULL,
                        coordination VARCHAR(50)  NOT NULL,
                        google_ID VARCHAR(50) NOT NULL,
                        number_of_places integer NOT NULL,
                        number_of_occupied_places integer,
                        CONSTRAINT "parking_pkey" PRIMARY KEY ("ID_parking")
                    )'''
                cur.execute(create_script)
                insert_script= 'INSERT INTO parking ("ID_parking", coordination, google_ID, number_of_places, number_of_occupied_places) VALUES (%s, %s, %s, %s, %s)'
                with open('parkingi.txt') as f: #loading data from file and creating rows in table parking
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        insert_values = line.split('\t')
                        cur.execute(insert_script, insert_values)
                # cur.execute('SELECT * FROM parking') #print for my debugging needs
                # for record in cur.fetchall():
                #     print(record)
    ########################################################################################################################

    #######################################------------SECTOR TABLE-------------############################################
                cur.execute('DROP TABLE IF EXISTS sector CASCADE')
                create_script = '''CREATE TABLE IF NOT EXISTS public.sector
                    (
                        "ID_parking" integer NOT NULL,
                        sector_name VARCHAR(20) NOT NULL,
                        number_of_places integer NOT NULL,
                        number_of_occupied_places integer,
                        parallel_or_perpendicular VARCHAR(20) NOT NULL,
                        start_of_sector_coordinates VARCHAR(150) NOT NULL,
                        end_of_sector_coordinates VARCHAR(150) NOT NULL,
                        CONSTRAINT "sector_pkey" PRIMARY KEY (sector_name),
                        CONSTRAINT "ID_parking" FOREIGN KEY ("ID_parking")
                            REFERENCES public.parking ("ID_parking") MATCH SIMPLE
                            ON UPDATE NO ACTION
                            ON DELETE NO ACTION
                    )'''
                cur.execute(create_script)
                insert_script = 'INSERT INTO sector ("ID_parking", sector_name, number_of_places, number_of_occupied_places, ' \
                                'parallel_or_perpendicular, start_of_sector_coordinates, end_of_sector_coordinates) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                places_in_sector=[] #stores number of places in each sector
                sector_names=[] #stores sectors names
                now_occupied_places=[] #stores number of occupied places in each sector
                with open('sector.txt') as f: #loading from the file information about sectors and creating row for table sector
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        insert_values = line.split('\t')
                        sector_names.append(insert_values[1])
                        places_in_sector.append(int(insert_values[2]))
                        now_occupied_places.append(int(insert_values[3]))
                        cur.execute(insert_script, insert_values)
                        # cur.execute('SELECT * FROM parking') #print for my debugging needs
                        # for record in cur.fetchall():
                        #     print(record)
    ########################################################################################################################

    #######################################------------CAR TABLE-------------###############################################
                cur.execute('DROP TABLE IF EXISTS car CASCADE')
                create_script = '''CREATE TABLE IF NOT EXISTS public.car
                    (
                        "ID_car" VARCHAR(25) NOT NULL,
                        current_location VARCHAR(150),
                        disability_adapted boolean,
                        CONSTRAINT "car_pkey" PRIMARY KEY ("ID_car")
                    )'''
                cur.execute(create_script)
                insert_script = 'INSERT INTO car ("ID_car", current_location, disability_adapted) VALUES (%s, %s, %s)'
                car_marka = ['Toyota', 'Citroen', 'Peugeot', 'Renault', 'Kia', 'Honda', 'Hyundai', 'Audi', 'Volkswagen', 'BMW', 'Tesla']
                ID_car=[] #stored ID's of all cars

                def random_ID(): #creating a unique car ID
                    letters = string.ascii_uppercase
                    return str(random.choice(car_marka)) + random.choice(letters) + random.choice(letters) + str(random.randrange(100, 1000, 3))

                for i in range(0,sum(now_occupied_places)): #creating as many cars as there is occupied places in all sectors of all parkings
                    auto = random_ID()
                    while auto in ID_car: #validation if the ID already exists
                        auto=random_ID()
                    ID_car.append(auto)
                    options = False, True
                    disability_value = random.choices(options, weights=(90, 10)) #disability_value = False /True randomizer with probability 0.9 that is not disabled
                    location='NULL'
                    insert_values = (auto, location, disability_value[0])
                    cur.execute(insert_script, insert_values)

                # cur.execute('SELECT * FROM car')
                # for record in cur.fetchall():
                #     print(record)
    ########################################################################################################################

    ###########################################------------PLACE TABLE-------------############################################
                cur.execute('DROP TABLE IF EXISTS place')
                create_script = '''CREATE TABLE IF NOT EXISTS public.place
                    (
                        sector_name VARCHAR(20) NOT NULL,
                        "ID_place" VARCHAR(20) NOT NULL,
                        place_status VARCHAR(50) NOT NULL,
                        date_of_occupation timestamp without time zone,
                        predicted_departure_time timestamp without time zone DEFAULT NULL,
                        occupying_car VARCHAR(25),
                        charging_point boolean,
                        disability_adapted boolean,
                        CONSTRAINT "place_pkey" PRIMARY KEY ("ID_place"),
                        CONSTRAINT "place_sector_name_fkey" FOREIGN KEY (sector_name)
                            REFERENCES public.sector (sector_name) MATCH SIMPLE
                            ON UPDATE NO ACTION
                            ON DELETE NO ACTION
                    )'''
                cur.execute(create_script)
                insert_script = 'INSERT INTO place (sector_name, "ID_place", place_status, date_of_occupation, predicted_departure_time, occupying_car, charging_point, disability_adapted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                for sector_name in sector_names: #going through all sectors
                    occupied = now_occupied_places.pop(0) #getting current number of occupied places in the sector
                    i = places_in_sector.pop(0) #getting how many places in total are in the sector
                    for number in range(0,i): #going through all places in the sector
                        ID_place=sector_name+'P'+str(number+1)
                        place_status = 'free'
                        occupying_car = None
                        date_of_occupation = None
                        predicted_departure_time = None
                        options = False, True
                        charging_point = random.choices(options, weights=(50, 50))
                        disability_value = random.choices(options, weights=(90, 10))
                        if occupied > 0:
                            occupying_car=random.choice(ID_car)
                            occupied=occupied-1
                            ID_car.remove(occupying_car)
                            place_status = 'occupied'
                            update_script='''UPDATE CAR SET current_location=%s WHERE "ID_car"=%s'''
                            cur.execute(update_script, (ID_place, occupying_car))
                        insert_values = (sector_name, ID_place, place_status, date_of_occupation, predicted_departure_time, occupying_car, charging_point[0], disability_value[0])
                        cur.execute(insert_script, insert_values)
                cur.execute('SELECT * FROM place')
                # for record in cur.fetchall():
                #     print(record)

    #################################adding foreign key to table car########################################
                create_script='''ALTER TABLE car ADD
                    CONSTRAINT car_current_location_fkey FOREIGN KEY (current_location)
                            REFERENCES public.place ("ID_place") MATCH SIMPLE
                            ON UPDATE NO ACTION
                            ON DELETE NO ACTION
                            NOT VALID'''
                cur.execute(create_script)
    ########################################################################################################################

    ##################################################trigger##############################################################

    #function counting occupied places and updating tables sector and places
                create_script=''' CREATE OR REPLACE FUNCTION public.count_occupied_places_function()
                                    RETURNS trigger
                                    LANGUAGE 'plpgsql'
                                    COST 100
                                    VOLATILE NOT LEAKPROOF
                                AS $BODY$
                                BEGIN
                                UPDATE sector SET number_of_occupied_places=(SELECT COUNT(sector_name) FROM place WHERE place.sector_name=sector.sector_name AND place_status='occupied' GROUP BY sector_name);
                                UPDATE parking SET number_of_occupied_places=(SELECT SUM(number_of_occupied_places) FROM sector WHERE parking."ID_parking"=sector."ID_parking" GROUP BY "ID_parking");
                                RETURN NULL;
                                END
                                $BODY$;
    
                                ALTER FUNCTION public.count_occupied_places_function()
                                    OWNER TO postgres;'''
                cur.execute(create_script)


    #creating the trigger to execute function every time a place status is changed
                create_script='''CREATE TRIGGER count_occupied_places_trigger
                                    AFTER INSERT OR DELETE OR UPDATE OF place_status
                                    ON public.place
                                    FOR EACH ROW
                                    EXECUTE FUNCTION public.count_occupied_places_function();'''
                cur.execute(create_script)

    ################################################################################################################################


        conn.commit()
    except Exception as error:
        print(error)
        print("Remember to create an empty database!!")
        print("If the database is created and you are putting correct values for db name and password, then maybe you need to change some connection data (username etc.) 'by hand' in init_database.py ")
    finally:
        if conn is not None:
            conn.close()
