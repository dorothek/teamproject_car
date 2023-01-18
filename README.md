# Team project on autonomous cars

## Project idea

We have developed a program that is a better solution to the current parking systems.
Our project simulates a car/cars looking for a parking place that is closest to them, or near the set destination. This program could work in synergy with (for instance) Google Maps to help drivers find the best parking place. 

### How does it work? 

After the driver decides to park, our system will search its database for the nearest parking lot with a vacant space and reserve that space for him, as well as transmit to his autonomous car the data for travelling to that location. 
In addition, the car closest to the reserved spot will verify whether the spot is free (if, for example, a dumpster has fallen on it, or a tree has fallen there). 
This is the operating scheme for large parking lots. 
We have assumed that if the parking lot is small (for example, the one by the local grocery store) then there is no need to store its scheme - in this case, data sufficient to identify a vacant space is the information about how many cars can park there on the average, and sensor readings.

## Tech stack 

Python 
