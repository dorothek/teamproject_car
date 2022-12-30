import psycopg2.extras
import random
from datetime import date
import string

hostname = 'localhost'
database = 'baza'
username = 'postgres'
pwd = '***'
port_id = 5432
conn = None


school = [11,13]
hospital =[1]
church = [15]
main_road = [3,4,6,7,8,10]
shops_nearby = [2,7,9,10,3,12]


def percent_of_places_taken(parking_nr,time_a_day, day):
    percent = 20
    hour,minutes = time_a_day.split(':')
    predicted_departure_time = random.randint(5,100)
    time=int(hour) 
    if parking_nr in church and day=="Sun" and (time==7 or time==10 or time==12 or time==16):
        percent=70 
        predicted_departure_time = random.randint(15,60)
    elif parking_nr in shops_nearby and day=="Sat" and time>6 and time<21:
        percent=75
        if time==12 or time==13:
            percent+=10
        predicted_departure_time = random.randint(1,150)
    elif parking_nr in school and (day!="Sat" and day!="Sun"):
        if time==8 or time==9:
            percent=65
        elif time==14 or time==15:
            percent=80
        predicted_departure_time = random.randint(1,30)
    elif parking_nr in hospital:
        percent+=20
        predicted_departure_time=0
        if day=="Sun" and time>14 and time<17:
            percent=80
            predicted_departure_time = random.randint(4,120)
    if parking_nr in main_road and time>7 and time<20:
        percent+=10
        if random.randint(0,3)==2:
            predicted_departure_time = random.randint(1,60)

    return percent, predicted_departure_time  

def rand_arrival_time(predicted_departure_time):
    arrival_time_ago = 0
    if predicted_departure_time>100:
        arrival_time_ago = random.randint(1,30)
    else:
        arrival_time_ago = random.randint(10,100)
    return arrival_time_ago

def date_of_arrival(arrival_time_ago, time):
    hours = int(arrival_time_ago/60)
    minutes = int(arrival_time_ago%60)
    cur_h,cur_min = time.split(':')
    cur_h,cur_min=int(cur_h),int(cur_min)
    if cur_min-minutes<0:
        cur_min=cur_min-minutes+60
        hours+=1
    else:
        cur_min-=minutes
    cur_h-=hours

    today = str(date.today())
    date_of_arrival="{} {}:{}:00-00".format(today,cur_h,cur_min)
    return date_of_arrival

def date_of_departure(departure_time, time):
    hours = int(predicted_dep_time/60)
    minutes = int(predicted_dep_time%60)
    h,min = current_time.split(':')
    h,min=int(h),int(min)
    if min+minutes>=60:
        min+=minutes-60
        hours+=1
    else:
        min+=minutes
        h+=hours

    today = str(date.today())
    departure_time="{} {}:{}:00-00".format(today,h,min)
    return departure_time

def random_ID(): 
    letters = string.ascii_uppercase
    return str(random.choice(car_marka)) + random.choice(letters) + random.choice(letters) + str(random.randrange(100, 1000, 3))

try:
    with psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id) as conn:

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT "ID_parking", place.sector_name,"ID_place",charging_point,disability_adapted FROM place JOIN sector ON place.sector_name=sector.sector_name')
            for record in cur: 
                current_time = "12:00"
                day_of_week = "Sat"
                ID_car=[]
                percent, predicted_dep_time = percent_of_places_taken(record[0],current_time, day_of_week) 
                rand = random.randint(1,100)

                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur_place:
                 if percent>rand:
                    command = """UPDATE place SET place_status='occupied' WHERE "ID_place"= %s"""
                    cur_place.execute(command,[record[2]])
                    
                    arrival_time_ago = rand_arrival_time(predicted_dep_time)
                    rand_arrival_date = date_of_arrival(arrival_time_ago,current_time)
                    cur_place.execute("""UPDATE place SET date_of_occupation=%s WHERE "ID_place"= %s""",(rand_arrival_date,record[2]))
                    
                    
                    if predicted_dep_time!=0:
                        command="""UPDATE place SET predicted_departure_time=%s WHERE "ID_place"= %s"""
                        departure_time=date_of_departure(predicted_dep_time,current_time)
                        cur_place.execute(command,(departure_time,record[2]))
                    else:
                        cur_place.execute("""UPDATE place SET predicted_departure_time=%s WHERE "ID_place"= %s""",(None,record[2]))
                        
                    car_marka = ['Toyota', 'Citroen', 'Peugeot', 'Renault', 'Kia', 'Honda', 'Hyundai', 'Audi', 'Volkswagen', 'BMW', 'Tesla']

                    auto = random_ID()
                    while auto in ID_car: 
                        auto=random_ID()
                    ID_car.append(auto)
                    
                    disability_value=False
                    if record[4]==True:
                        disability_value = True
                    location='NULL'
                    insert_values = (auto, record[2], disability_value)
                    cur_place.execute("""UPDATE place SET occupying_car=%s WHERE "ID_place"= %s""",(auto,record[2]))
                    #cur.execute("""INSERT INTO car ("ID_car", current_location, disability_adapted) VALUES (%s, %s, %s)"""",insert_values)

                        
                 else: #clear 
                    cur_place.execute("""UPDATE place SET place_status='free' WHERE "ID_place"= %s""",[record[2]])
                    cur_place.execute("""UPDATE place SET date_of_occupation=%s WHERE "ID_place"= %s""",(None,record[2]))
                    cur_place.execute("""UPDATE place SET predicted_departure_time=%s WHERE "ID_place"= %s""",(None,record[2]))
                    cur_place.execute("""UPDATE place SET occupying_car=%s WHERE "ID_place"= %s""",(None,record[2]))
                    
    conn.commit() 
          
except Exception as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
