import psycopg2.extras
import random
from datetime import date, timedelta
from datetime import datetime
import string
import initial_database

conn = psycopg2.connect(dbname=initial_database.database, user=initial_database.username, password=initial_database.pwd)

#parkings that are close to places that have a high influence of traffic
school = [11,13]
hospital =[1]
church = [15]
main_road = [3,4,6,7,8,10]
shops_nearby = [2,7,9,10,3,12]

def clear_database(conn): #clears table place and truncates table car
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""UPDATE place SET place_status='free', date_of_occupation=%s, predicted_departure_time=%s, occupying_car=%s""",(None,None,None))
        cur.execute("""TRUNCATE car""")
                     
    conn.commit() 
          
#calculates percent of places taken and possible departure time of a car depending on where parking is located
def percent_of_places_taken(parking_nr,time_a_day, day):
    percent = 30
    hour,minutes = time_a_day.split(':')
    predicted_departure_time = random.randint(5,100)
    time=int(hour) 
    if time>8 and time<19:
        percent+=10
    if day==5 or day==6:
        percent+=10
    if parking_nr in church and day==6 and (time==7 or time==10 or time==12 or time==16):
        percent=70 
        predicted_departure_time = random.randint(15,60)
    elif parking_nr in shops_nearby and day==5 and time>6 and time<21:
        percent=75
        if time==12 or time==13:
            percent+=10
        predicted_departure_time = random.randint(1,150)
    elif parking_nr in school and (day!=5 and day!=6):
        if time==8 or time==9:
            percent=65
        elif time==14 or time==15:
            percent=80
        predicted_departure_time = random.randint(1,30)
    elif parking_nr in hospital:
        percent+=20
        predicted_departure_time=random.randint(60,600)
        if day==6 and time>14 and time<17:
            percent=80
            predicted_departure_time = random.randint(4,120)
    if parking_nr in main_road and time>7 and time<20:
        percent+=10
        if random.randint(0,3)==2:
            predicted_departure_time = random.randint(1,60)

    return percent, predicted_departure_time  

#returns random arrival time of a car
def rand_arrival_time(predicted_departure_time):
    arrival_time_ago = 0
    if predicted_departure_time>100:
        arrival_time_ago = random.randint(1,30)
    else:
        arrival_time_ago = random.randint(10,100)
    return arrival_time_ago

#calculates the date of car's arrival
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

    d = str(date.today())
    if cur_h-hours<0:
        cur_h=24-abs(cur_h-hours)
        d=str(date.today()-timedelta(days=1))
    else:   
        cur_h-=hours      
    date_of_arrival="{} {}:{}:00-00".format(d,cur_h,cur_min)
    return date_of_arrival

#calculates the date of car's departure 
def date_of_departure(predicted_dep_time, time):
    hours = int(predicted_dep_time/60)
    minutes = int(predicted_dep_time%60)
    
    cur_h,cur_min = time.split(':')
    cur_h,cur_min=int(cur_h),int(cur_min)
    if cur_min+minutes>=60:
        cur_min=cur_min+minutes-60
        hours+=1
    else:
        cur_min+=minutes

    d = str(date.today())
    if cur_h+hours>=24:
        cur_h=cur_h+hours-24
        d=str(date.today()+timedelta(days=1))
    else:
        cur_h+=hours   
    departure_time="{} {}:{}:00-00".format(d,cur_h,cur_min)
    return departure_time

#returns a random ID of a car
def random_ID(): 
    letters = string.ascii_uppercase
    return str(random.choice(car_marka)) + random.choice(letters) + random.choice(letters) + str(random.randrange(100, 1000, 3))

try:
    with psycopg2.connect(
        host=initial_database.hostname,
        dbname=initial_database.database,
        user=initial_database.username,
        password=initial_database.pwd,
        port=initial_database.port_id) as conn:

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            clear_database(conn)
            current_time = "12:00"
            day_of_week = 5

           # print("1. Decide the time and the day of the week")
           # print("2. Get the today's date and time")
           # print("Choice (1 or 2)")
           # choice = input()
            
           # if choice=='1':
           #     print("Day of the week (Mon=0, Tue=1, Wed=2, Thurs=3, Fri=4, Sat=5, Sun=6):")
           #     day_of_week=int(input())
           #     print("Time (hh:mm):")
           #     current_time = input()
           # if choice=='2':
            dt = datetime.now()
            day_of_week = dt.weekday()
            current_time = dt.strftime("%H:%M")
            
            cur.execute('SELECT "ID_parking", place.sector_name,"ID_place",charging_point,disability_adapted FROM place JOIN sector ON place.sector_name=sector.sector_name')
            for record in cur: 
                
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
                        
                    insert_values = (auto, record[2], disability_value)
                    cur_place.execute("""UPDATE place SET occupying_car=%s WHERE "ID_place"= %s""",(auto,record[2]))
                    cur_place.execute('INSERT INTO car ("ID_car", current_location, disability_adapted) VALUES (%s, %s, %s)',insert_values)

    conn.commit() 
          
except Exception as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
