import psycopg2.extras
import random
import string

#TODO trzeba wpisać swoje dane żeby się połączyć
hostname = 'localhost'
database = 'baza'
username = 'postgres'
pwd = '***'
port_id = 5432
conn = None

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
            with open('parkingi.txt') as f: #wczytuje z pliku i tworzy wiersze w tabeli
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
            places_in_sector=[] #przechowuje po kolei ilosc miejsc w kazdym sektorze
            sector_names=[] #przechowuje nazwy sektorów
            now_occupied_places=[] #przechowuje ilosc zajmowanych miejsc w kazdym z sektorów
            with open('sector.txt') as f: #wczytuje z pliku info o sektorach i tworzy wiersze
                #TODO dodać do pliku txt reszte sektorów,a tam gdzie nie ma być sektorów moze po prostu nazwe sektoru jako 00,
                # czy coś w tym stylu? (myśle zeby dodac sektory mimo wszystko, zeby miec wspolrzedne poczatku i konca itp,
                # i też w sumie nazywałam miejsca przy użyciu nazw sektorów, taki miałam na to pomysł)
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
            ID_car=[] #przechowuje ID wszystkich samochodow

            def random_ID(): #funkcja do tworzenia unikalnego ID samochodu
                letters = string.ascii_uppercase
                return str(random.choice(car_marka)) + random.choice(letters) + random.choice(letters) + str(random.randrange(100, 1000, 3))

            for i in range(0,sum(now_occupied_places)): #losuje/tworzy tyle aut ile jest aktualnie zajetych miejsc we wszystkich sektorach==parkingach
                auto = random_ID()
                while auto in ID_car: #walidacja czy juz takie ID istnieje, jeśli tak to jeszcze raz losuje
                    auto=random_ID()
                ID_car.append(auto)
                options = False, True
                disability_value = random.choices(options, weights=(90, 10)) #disability_value = losowanie False /True z prawdopodobienstwem 0.9, że nie jest niepelnosprawny
                location='NULL'
                insert_values = (auto, location, bool(disability_value)) #TODO obczaić jak wstawiać boole do postgresa tak żeby faktycznie wstawialo sie True lub False
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
            for sector_name in sector_names: #przechodzi przez wszystkie sektory
                occupied=now_occupied_places.pop(0) #pobiera ilość aktualnie zajętych miejsc w danym sektorze
                i = places_in_sector.pop(0) #pobiera ilosc miejsc w danym sektorze
                for number in range(0,i): #przez wszystkie miejsca w sektorze
                    ID_place=sector_name+'P'+str(number+1)
                    place_status = 'free'
                    occupying_car = 'NULL'
                    date_of_occupation='2020-10-01 00:00:00-00' #TODO powstawiać sensowne timestampy jak to zrobić, żeby przyjmowało NULLa bo potrzebujemy tego gdy place jest free
                    predicted_departure_time='2020-10-01 00:00:00-00' #TODO jak to zrobić, żeby przyjmowało NULLa gdy place jest free albo po prostu nie wiemy
                    options = False, True
                    charging_point = random.choices(options, weights=(50, 50)) #TODO obczaić jak wstawiać boole do postgresa tak żeby faktycznie wstawialo sie True lub False
                    disability_value = random.choices(options, weights=(90, 10))
                    if occupied > 0:
                        occupying_car=random.choice(ID_car)
                        occupied=occupied-1
                        ID_car.remove(occupying_car)
                        place_status = 'occupied'
                        #TODO update wartości w tabeli car.location gdzie ID_car==occupying car bo tak jakby "parkujemy to auto"
                    insert_values = (sector_name, ID_place, place_status, date_of_occupation, predicted_departure_time, occupying_car, bool(charging_point), bool(disability_value))
                    cur.execute(insert_script, insert_values)
            cur.execute('SELECT * FROM place')
            # for record in cur.fetchall():
            #     print(record)

#################################dodanie klucza obcego do tabeli car########################################
            create_script='''ALTER TABLE car ADD
                CONSTRAINT car_current_location_fkey FOREIGN KEY (current_location)
                        REFERENCES public.place ("ID_place") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION
                        NOT VALID'''
            cur.execute(create_script)
########################################################################################################################

    conn.commit()
except Exception as error:
    print(error)
finally:
    if conn is not None:
        conn.close()