import random
import matplotlib.pyplot as plt

"""
2PX3 Highway Simulation Starting Code 

Simulation for a fast/slow highway driver. Modelling choices:
1) Cars will cruise via their speed and safe follow distance
2) If a car cannot maintain its speed, it will desire to change lanes

See the video for more detail.

Dr. Vincent Maccio 2022-02-01 
"""

EMPTY = " "

"""
The following variables control the different factors of the simulation.
Play around with them to see how a highway might behave.
For an extra challenge modify the class methods to make a more accurate simulation.
"""

#You can think of these speeds as 125 and 100 km/hr
FAST = 5
SLOW = 4

#Highway options
HIGHWAY_LENGTH = 110
NUM_LANES = 4

#Follow distance for normal cars and for self driving cars
HUMAN_SAFE_FOLLOW = 4
SDC_SAFE_FOLLOW = 2
LANE_CHANGE_SAFE_BACK = FAST
LANE_CHANGE_SAFE_FORWARD = FAST

#Desires:
CRUISE = "Cruise"
LANE_CHANGE = "Lane Change"
LANE_CHANGE_LEFT = "Left Lane Change"
LANE_CHANGE_RIGHT = "Right Lane Change"
LEFT_LANE_CHANGE_PROBABILITY = 0.5 #Probability that a car that wants to perform a lane change will pick to go left

#Car generation options
CAR_PROBABILITY = 0.25
FAST_PROBABILITY = 0.5
IS_HUMAN_PROBABILITY = 0.5

#Simulation options
NUM_TIME_STEPS = 10000
PRINT_ROAD = True
NUM_BARS = 15 #Number of bars in the output bar graph

#Class for each car
class Driver:

    def __init__(self, car_id, speed, arrive_time, is_human):
        self.id = car_id
        self.desire = CRUISE
        self.is_human = is_human
        self.speed = speed
        if is_human:
            self.safe_follow = HUMAN_SAFE_FOLLOW
        else:
            self.safe_follow = SDC_SAFE_FOLLOW
        self.arrive_time = arrive_time
        self.final_time = 0
        self.travel_time = 0
        self.final_dist = 0
        self.avg_speed = speed

    #Outputs an array with all of the data for the car
    def output_data(self):
        output_data = [self.id,
                       self.speed,
                       self.is_human,
                       self.arrive_time,
                       self.final_time,
                       self.travel_time,
                       self.final_dist,
                       self.avg_speed]
        return output_data

#Highway class
class Highway:

    def __init__(self, length, num_lanes):
        self.num_lanes = num_lanes
        self.road = [] #2d array representing highway (each secondary array within the main array represents a lane)
        for _ in range(num_lanes):
            self.road.append([]) #appends the number of lanes specified
        self.length = length
        for _ in range(length):
            for i in range(num_lanes):
                self.road[i].append(EMPTY)

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
    def safe_right_lane_change(self, lane, i):
        if lane == self.num_lanes - 1:
            return False
        safe_lane_change = True
        if self.road[lane + 1][i] != EMPTY:
            safe_lane_change = False
        for k in range(i - 1, i - LANE_CHANGE_SAFE_BACK - 1, -1):
            if self.road[lane + 1][k] != EMPTY:
                safe_lane_change = False
        for k in range(i + 1, i + LANE_CHANGE_SAFE_FORWARD + 1):
            if self.road[lane + 1][k] != EMPTY:
                safe_lane_change = False
        return safe_lane_change

    #Returns true if it is safe to switch to left lane (spot adjacent to the car's current position in the left lane is free, and so are the next 2 spaces)
    #Returns false otherwise
    def safe_left_lane_change(self, lane, i):
        if lane == 0:
            return False
        safe_lane_change = True
        if self.road[lane - 1][i] != EMPTY:
            safe_lane_change = False
        for k in range(i - 1, i - LANE_CHANGE_SAFE_BACK - 1, -1):
            if self.road[lane - 1][k] != EMPTY:
                safe_lane_change = False
        for k in range(i + 1, i + LANE_CHANGE_SAFE_FORWARD + 1):
            if self.road[lane - 1][k] != EMPTY:
                safe_lane_change = False
        return safe_lane_change
    
    #Prints the current state of the highway- good to see the visual representation and for debugging
    def print(self):
        s = "\n\n"
        for k in range(self.num_lanes):
            for i in range(self.length):
                if self.road[k][i] == EMPTY:
                    s += "_"
                else:
                    s += "C"
            s += "\n"
        print(s)

#Simulation class
class Simulation:
    def __init__(self, time_steps):
        self.road = Highway(HIGHWAY_LENGTH, NUM_LANES)
        self.time_steps = time_steps
        self.current_step = 0
        self.num_cars = 0
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

            for k in range(self.road.num_lanes):
                if self.road.get(k, i) != EMPTY:
                    self.sim_driver(k, i) #Simulates all drivers starting at the end of the highway and starting with the leftmost lane then moving right

        #Generate some new drivers at the beginning of the highway
        self.num_cars = self.gen_new_drivers(self.num_cars)

    def sim_driver(self, lane, i):
        driver = self.road.get(lane, i)

        #If the driver reaches the end of the highway then remove them and store data
        if driver.speed + i >= self.road.length - 1:
            self.road.set(lane, i, EMPTY)
            driver.final_time = self.current_step
            driver.final_dist = HIGHWAY_LENGTH
            driver.travel_time = driver.final_time - driver.arrive_time
            driver.avg_speed = driver.final_dist/driver.travel_time
            self.data.append(driver.output_data())
            return

        #Decides if a car that wants to do a lane change will go left or right
        r = random.random()
        if driver.desire == LANE_CHANGE and r <= LEFT_LANE_CHANGE_PROBABILITY:
            if self.road.safe_left_lane_change(lane, i):
                driver.desire = LANE_CHANGE_LEFT
            elif self.road.safe_right_lane_change(lane, i):
                driver.desire = LANE_CHANGE_RIGHT
        elif driver.desire == LANE_CHANGE and r > LEFT_LANE_CHANGE_PROBABILITY:
            if self.road.safe_right_lane_change(lane, i):
                driver.desire = LANE_CHANGE_RIGHT
            elif self.road.safe_left_lane_change(lane, i):
                driver.desire = LANE_CHANGE_LEFT

        #Performs lane change if necessary then calls cruise method
        if driver.desire == LANE_CHANGE_RIGHT:
            self.road.set(lane + 1, i, driver)
            self.road.set(lane, i, EMPTY)
            driver.desire = CRUISE
            self.sim_cruise(lane + 1, i)
                
        elif driver.desire == LANE_CHANGE_LEFT:
            self.road.set(lane - 1, i, driver)
            self.road.set(lane, i, EMPTY)
            driver.desire = CRUISE
            self.sim_cruise(lane - 1, i)
            
        elif driver.desire == CRUISE or driver.desire == LANE_CHANGE:
            self.sim_cruise(lane, i)

    #Moves car forward depending on its speed and how much room is infront of it, also sets desire to lane change if there is no room in front
    def sim_cruise(self, lane, i):
        driver = self.road.get(lane, i)
        x = self.road.safe_distance_within(lane, i, driver.speed + driver.safe_follow)

        #If there is enough room for the car to move forward at full speed
        if x == driver.speed + driver.safe_follow:
            self.road.set(lane, i + driver.speed, driver) #Car moves forward by full speed
        elif x > driver.safe_follow:
            driver.desire = LANE_CHANGE
            self.road.set(lane, i + x - driver.safe_follow, driver) #Car moves forward just enough to maintain safe_distance
        else:
            driver.desire = LANE_CHANGE
            self.road.set(lane, i + 1, driver) #Car moves forward by just 1 spot
        self.road.set(lane, i, EMPTY)

    #Generates a new driver for each lane depending on the given probabilities
    def gen_new_drivers(self, num_cars):
        is_human = True
        current_car_id = num_cars
        for lane in range(self.road.num_lanes):
            r = random.random()
            #Can adjust car probability in order to have a higher chance of generating a car each time
            if r < CAR_PROBABILITY:
                r = random.random()

                #Can adjust is human probability in order to have a higher chance of generating a human driver each time
                if r < IS_HUMAN_PROBABILITY:
                    is_human = True
                else:
                    is_human = False

                r = random.random()
                
                #Can adjust fast probability in order to have a higher chance of generating a fast or slow car each time
                if r < FAST_PROBABILITY:
                    self.road.set(lane, 0, Driver(current_car_id, FAST, self.current_step, is_human))
                else:
                    self.road.set(lane, 0, Driver(current_car_id, SLOW, self.current_step, is_human))
                current_car_id += 1

        return current_car_id

    #Plots the average speeds of each car in a bar graph
    def plot_avg_speed(self):
        car_IDs = []
        avg_speeds = []
        for i in self.data:
            car_IDs.append(i[0])
            avg_speeds.append(i[-1])
        min_speed = min(avg_speeds)
        max_speed = max(avg_speeds)
        diffs = (max_speed - min_speed)/NUM_BARS
        y_values = []
        for i in range(NUM_BARS):
            y_values.append(0)
            for speed in avg_speeds:
                if i == 0:
                    if speed >= (min_speed + i*diffs) and speed <= (min_speed + (1 + i)*diffs):
                        y_values[i] += 1
                else:
                    if speed > (min_speed + i*diffs) and speed <= (min_speed + (1 + i)*diffs):
                        y_values[i] += 1
        x_values = []
        for i in range(NUM_BARS):
            x_values.append(min_speed + i*diffs)
        plt.bar(x_values, y_values, width = diffs, align = 'edge')
        plt.show()

#Test function
def main():
    sim = Simulation(NUM_TIME_STEPS)
    sim.run()
    sim.plot_avg_speed()

main()
