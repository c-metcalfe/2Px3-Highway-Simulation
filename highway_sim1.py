import random

"""
2PX3 Highway Simulation Starting Code 

Simulation for a fast/slow highway driver. Modelling choices:
1) Cars will cruise via their speed and safe follow distance
2) If a car cannot maintain its speed, it will desire to change lanes

See the video for more detail.

Dr. Vincent Maccio 2022-02-01 
"""

EMPTY = " "
#You can think of these speeds as 125 and 100 km/hr
FAST = 5
SLOW = 4
SAFE_FOLLOW = 4
LEFT = 0
RIGHT = 1
CRUISE = "Cruise"
LANE_CHANGE = "Lane Change"
OFFSET = 5 #The last OFFSET indices of the road are not considered to avoid out of bounds errors
CAR_PROBABILITY = 0.25
FAST_PROBABILITY = 0.5
PRINT_ROAD = True
HIGHWAY_LENGTH = 110

#Class for each car
class Driver:

    def __init__(self, speed, arrive_time):
        self.speed = speed
        self.safe_follow = SAFE_FOLLOW
        self.desire = CRUISE
        self.arrive_time = arrive_time
        

#Highway class
class Highway:

    def __init__(self, length):
        self.road = [[], []] #2d array representing highway (each secondary array within the main array represents a lane- here we have 2)
        self.length = length
        for _ in range(length):
            self.road[0].append(EMPTY)
            self.road[1].append(EMPTY)
    
    #For you to edit as you see fit
    def can_lane_change(self, lane, i):
        return

    #Returns the value at the specified position within the specified lane
    def get(self, lane, index):
        return self.road[lane][index]

    #Sets the value at the specified position within the specified lane
    def set(self, lane, index, value):
        self.road[lane][index] = value

    #Returns the distance until the next car, from index i within k; returns k if all spots are EMPTY
    def safe_distance_within(self, lane, index, k):
        x = 0
        for i in range(index + 1, index + k + 1):
            if i >= self.length:
                return k
            if self.road[lane][i] != EMPTY:
                return x
            x += 1
        return x

    #Returns true if it is safe to switch to right lane (spot adjacent to the car's current position in the right lane is free, and so are the next 2 spaces)
    #Returns false otherwise
    def safe_right_lane_change(self, i):
        return self.road[RIGHT][i] == EMPTY and self.road[RIGHT][i+1] == EMPTY and self.road[RIGHT][i+2] == EMPTY
    
    #Returns true if it is safe to switch to left lane (spot adjacent to the car's current position in the left lane is free, and so are the next 2 spaces)
    #Returns false otherwise
    def safe_left_lane_change(self, i):
        return self.road[LEFT][i] == EMPTY and self.road[LEFT][i+1] == EMPTY and self.road[LEFT][i+2] == EMPTY

    #Prints the current state of the highway- good to see the visual representation and for debugging
    def print(self):
        s = "\n"
        #There is one for statement for each lane here- if you are changing the number of lanes you will need to modify this code
        for i in range(self.length):
            if self.road[0][i] == EMPTY:
                s += "_"
            else:
                s += "C"
        s += "\n"
        for i in range(self.length):
            if self.road[1][i] == EMPTY:
                s += "_"
            else:
                s += "C"
        print(s)

#Simulation class
class Simulation:

    def __init__(self, time_steps):
        self.road = Highway(HIGHWAY_LENGTH)
        self.time_steps = time_steps
        self.current_step = 0
        self.data = []

    #Method that runs the simulation
    def run(self):
        while self.current_step < self.time_steps:
            self.execute_time_step()
            self.current_step += 1
            if PRINT_ROAD:
                self.road.print()

    #Move forward by one time unit
    def execute_time_step(self):

        #Traverse through the length of the highway, beginning from the end and working backwards
        for i in range(self.road.length - 1, -1, -1):

            #If there is a driver at this position in the left lane, move them and attempt to perform their desired actions
            if self.road.get(LEFT, i) != EMPTY:
                self.sim_left_driver(i)

            #If there is a driver at this position in the right lane, move them and attempt to perform their desired actions
            if self.road.get(RIGHT, i) != EMPTY:
                self.sim_right_driver(i)

        #Generate some new drivers at the beginning of the highway
        self.gen_new_drivers()

    #Given the index, get the driver at that position in the right lane and advance them forward by their speed
    def sim_right_driver(self, i):
        driver = self.road.get(RIGHT, i)

        #If the driver will reach the end of the highway in their next move, remove from the lane array and record time taken to exit highway
        if driver.speed + i >= self.road.length - 1:
            self.road.set(RIGHT, i, EMPTY)
            self.data.append(self.current_step - driver.arrive_time)
            return #Car reaches the end of the highway

        #If the driver wants to change lanes
        #If you have more than 2 lanes, you will need additional logic for the center lane in order to keep track of which lane the driver is switching to
        if driver.desire == LANE_CHANGE:
            #check if it is safe to do so
            if self.road.safe_left_lane_change(i):
                #If it is safe, switch driver lane to left and set driver objective to cruise (stay in the same lane)
                self.road.set(LEFT, i, driver)
                self.road.set(RIGHT, i, EMPTY)
                driver.desire = CRUISE
                self.sim_cruise(LEFT, i)
            else:
                self.sim_cruise(RIGHT, i)
        elif driver.desire == CRUISE:
            self.sim_cruise(RIGHT, i)

    #Given the index, get the driver at that position in the left lane and advance them forward by their speed
    def sim_left_driver(self, i):
        driver = self.road.get(LEFT, i)

        #If the driver will reach the end of the highway in their next move, remove from the lane array and record time taken to exit highway
        if driver.speed + i >= self.road.length - 1:
            self.road.set(LEFT, i, EMPTY)
            self.data.append(self.current_step - driver.arrive_time)
            return #Car reaches the end of the highway

        #If the driver wants to change lanes
        #If you have more than 2 lanes, you will need additional logic for the center lane in order to keep track of which lane the driver is switching to
        if driver.desire == LANE_CHANGE:

            #check if it is safe to do so
            if self.road.safe_right_lane_change(i):

                #If it is safe, switch driver lane to right and set driver objective to cruise (stay in the same lane)
                self.road.set(RIGHT, i, driver)
                self.road.set(LEFT, i, EMPTY)
                driver.desire = CRUISE
                self.sim_cruise(RIGHT, i)
            else:
                self.sim_cruise(LEFT, i)
        elif driver.desire == CRUISE:
            self.sim_cruise(LEFT, i)
            
    #Car continues in the same lane
    def sim_cruise(self, lane, i):

        #Get car information for specific lane and position
        driver = self.road.get(lane, i)

        x = self.road.safe_distance_within(lane, i, driver.speed + driver.safe_follow)

        #If there is enough room for the car to move forward at full speed
        if x == driver.speed + driver.safe_follow:
            self.road.set(lane, i + driver.speed, driver) #Car moves forward by full speed
        
        #If the car is not within unsafe following distance but cannot move forward by it's full speed
        elif x > driver.safe_follow:
            driver.desire = LANE_CHANGE
            self.road.set(lane, i + x - driver.safe_follow, driver) #Car moves forward just enough to maintain safe_distance
        else:
            driver.desire = LANE_CHANGE
            self.road.set(lane, i + 1, driver) #Car moves forward by just 1 spot
        self.road.set(lane, i, EMPTY)

    #Randomly generate new drivers entering the highway
    def gen_new_drivers(self):

        #Left lane
        r = random.random()

        #Can adjust car probability in order to have a higher chance of generating a car each time
        if r < CAR_PROBABILITY:
            r = random.random()

            #Can adjust fast probability in order to have a higher chance of generating a fast or slow car each time
            if r < FAST_PROBABILITY:
                self.road.set(LEFT, 0, Driver(FAST, self.current_step))
            else:
                self.road.set(LEFT, 0, Driver(SLOW, self.current_step))

        #Right lane
        r = random.random()

        #Can adjust car probability in order to have a higher chance of generating a car each time
        if r < CAR_PROBABILITY:
            r = random.random()

            #Can adjust fast probability in order to have a higher chance of generating a fast or slow car each time
            if r < FAST_PROBABILITY:
                self.road.set(RIGHT, 0, Driver(FAST, self.current_step))
            else:
                self.road.set(RIGHT, 0, Driver(SLOW, self.current_step))

    def average_time(self):
        return sum(self.data)/len(self.data)
    


def main():
    sim = Simulation(25)
    sim.run()

main()
