import random
import math
import numpy as np

import pygame
from pygame.color import THECOLORS

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw

# /home/root/Kfolder/reinforcement-learning-car-master/flat_game

# /home/root/.local/lib/python3.6/site-packages/pymunk

# PyGame init
width = 1300
height = 100
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Turn off alpha since we don't use it.
screen.set_alpha(None)

# Showing sensors and redrawing slows things down.
show_sensors = True
draw_screen = True
go_left = False
go_right = True
last_distance = 0

goal = 1290

class GameState:

    def __init__(self):
        # Global-ish.
        self.crashed = False

        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create the car.
        self.create_car(50, 30, 0.0)
        #self.create_box()
        # Record steps.
        self.num_steps = 0
        self.last_steps = 0

        # Create walls.
        static = [
            pymunk.Segment(
                self.space.static_body,
                (0, 1), (0, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, height), (width, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (width-1, height), (width-1, 1), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, 1), (width, 1), 1)
        ]
        for s in static:
            s.friction = 1.
            s.group = 1
            s.collision_type = 1
            s.color = THECOLORS['red']
        self.space.add(static)

    #    Create some obstacles, semi-randomly.
    #    We'll create three and they'll move around to prevent over-fitting.
        self.obstacles = []
        # self.obstacles.append(self.create_obstacle(600, 50, 10))
        # self.obstacles.append(self.create_obstacle(500, 60, 10))
        # self.obstacles.append(self.create_obstacle(200, 90, 20))
        # self.obstacles.append(self.create_obstacle(100, 30, 20))
        # self.obstacles.append(self.create_obstacle(300, 20, 10))
        # self.obstacles.append(self.create_obstacle(400, 30, 20))
        # self.obstacles.append(self.create_obstacle(900, 40, 20))
        # self.obstacles.append(self.create_obstacle(1000, 55, 15))
        # self.obstacles.append(self.create_obstacle(1100, 35, 30))
        # self.obstacles.append(self.create_obstacle(1200, 60, 20))
        
        # Create a cat.
        #self.create_cat()

    def create_obstacle(self, x, y, r):
        c_body = pymunk.Body(pymunk.inf, pymunk.inf)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body

    def create_cat(self):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.cat_body = pymunk.Body(1, inertia)
        self.cat_body.position = 1100, 50
        self.cat_shape = pymunk.Circle(self.cat_body, 20)
        self.cat_shape.color = THECOLORS["orange"]
        self.cat_shape.elasticity = 1.0
        self.cat_shape.angle = 0.5
        direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.space.add(self.cat_body, self.cat_shape)

    def create_box(self):
        inertia = pymunk.moment_for_box(10.0, 80, 40)
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = 100, 150
        self.car_shape = pymunk.Poly.create_box(self.car_body, (80, 40))
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = 0.5
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse(driving_direction)
        self.space.add(self.car_body, self.car_shape)

    def create_car(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 5, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 10)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = r
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse(driving_direction)
        self.space.add(self.car_body, self.car_shape)

    def frame_step(self, action):

        global last_distance
        global goal
        global width

        if action == 0:  
            self.car_body.angle -= .157
        elif action == 1:
            self.car_body.angle += .157

        # Move obstacles.
        # if self.num_steps % 100 == 0:
        #     self.move_obstacles()

        # Move cat.
#        if self.num_steps % 5 == 0:
#            self.move_cat()

        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.velocity = 20*driving_direction

        # Update the screen and stuff.
        screen.fill(THECOLORS["black"])
        draw(screen, self.space)
        self.space.step(1.0/10)
        if draw_screen:
            pygame.display.flip()
        clock.tick()

        # Get the current location and the readings there.
        x, y = self.car_body.position

        orientation = self.car_body.angle

        distance = math.fabs(x - goal)

        readings = self.get_sonar_readings(x, y, self.car_body.angle)
        normalized_readings = [(x-20.0)/20.0 for x in readings]
        normalized_readings.append(orientation)
        normalized_readings.append(-orientation)
        normalized_readings.append(distance)
        state = np.array([normalized_readings])

        # Set the reward.
        # Car crashed when any reading == 1
        if self.car_is_crashed(readings):
            self.crashed = True
            reward = -500
            self.recover_from_crash(driving_direction, action)
        else:
            # Higher readings are better, so return the sum.
#            reward = -5 + int(self.sum_readings(readings)/10)

            if distance < last_distance:
                reward = last_distance - distance
            else:
                reward = distance - last_distance


        if distance < 10:
            goal = width - goal
            reward = self.last_steps - self.num_steps # reward for reaching the objective faster than last round (may want to scale this)
            self.last_steps = self.num_steps 
            self.num_steps = 0

        self.num_steps += 1
        last_distance = distance

        return reward, state, distance

    def move_obstacles(self):
        # Randomly move obstacles around.
        for obstacle in self.obstacles:
            speed = random.randint(1, 2)
            direction = Vec2d(1, 0).rotated(self.car_body.angle + random.randint(-2, 2))
            obstacle.velocity = speed * direction

    def move_cat(self):
        speed = random.randint(20, 30)
        self.cat_body.angle -= random.randint(-1, 1)
        direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.cat_body.velocity = speed * direction

    def car_is_crashed(self, readings):
        if readings[0] == 2 or readings[1] == 2 or readings[2] == 2:
            return True
        else:
            return False

    def recover_from_crash(self, driving_direction, action):
        """
        We hit something, so recover.
        """

        # angles = [-0.157,0.157]
        # angle = random.randint(0, 1)

        while self.crashed:
            # Go backwards.
            self.car_body.velocity = -20*driving_direction
            self.crashed = False

            # if action == 0:  
            #     self.car_body.angle -= .15707
            # elif action == 1:
            #     self.car_body.angle += .15707

#            for i in range(10):

            self.car_body.angle += .157  # Turn a little.
            screen.fill(THECOLORS["grey7"])  # Red is scary!
            draw(screen, self.space)
            self.space.step(1./10)
            if draw_screen:
                pygame.display.flip()
            clock.tick()
   
    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        tot = 0
        for i in readings:
            tot += i
        return tot

    def get_sonar_readings(self, x, y, angle):
        readings = []
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
        # Make our arms.
        arm_left = self.make_sonar_arm(x, y)
        arm_middle = arm_left
        arm_right = arm_left

        # Rotate them and get readings.
        readings.append(self.get_arm_distance(arm_left, x, y, angle, 0.75))
        readings.append(self.get_arm_distance(arm_middle, x, y, angle, 0))
        readings.append(self.get_arm_distance(arm_right, x, y, angle, -0.75))

        if show_sensors:
            pygame.display.update()

        return readings

    def get_arm_distance(self, arm, x, y, angle, offset):
        # Used to count the distance.
        i = 0

        # Look at each point and see if we've hit something.
        for point in arm:
            i += 1

            # Move the point to the right spot.
            rotated_p = self.get_rotated_point(
                x, y, point[0], point[1], angle + offset
            )

            # Check if we've hit something. Return the current i (distance)
            # if we did.
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= width or rotated_p[1] >= height:
                return i  # Sensor is off the screen.
            else:
                obs = screen.get_at(rotated_p)
                if self.get_track_or_not(obs) != 0:
                    return i

            if show_sensors:
                pygame.draw.circle(screen, (255, 255, 255), (rotated_p), 2)

        # Return the distance for the arm.
        return i

    def make_sonar_arm(self, x, y):
        spread = 5  # Default spread.
        distance = 5  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 40):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = height - (y_change + y_1)
        return int(new_x), int(new_y)

    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1

# if __name__ == "__main__":
#     game_state = GameState()
#     while True:
#     #for i in range(2000):
#         #game_state = GameState()
#         game_state.frame_step((random.randint(0, 2)))
