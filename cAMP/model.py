from mesa import Model
from mesa.time import RandomActivation
from mesa.space import Grid

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import random
import math

import numpy as np
from agent import SlimeAgent

''' This program runs but does not correctly display the model '''

class SlimeModel(Model):
    def __init__(self, height, width):
        # number of agents per tile
        self.n = 2
        # rate of cAMP decay
        self.k = .01
        # diffusion constant of cAMP
        self.Dc = .03
        # spatial resolution for cAMP simulation
        self.Dh = .03
        # time resolution for cAMP simulation
        self.Dt = .5
        # rate of cAMP secretion by an agent
        self.f = 5
        # number of rows/columns in spatial array
        self.w = 2

        # height of grid
        self.height = 200
        # width of grid
        self.width = 200

        # counter for generating sequential unique id's
        self.j = 0

        # Create randomly ordered scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = Grid(self.height, self.width, torus=False)

#        self.datacollector = DataCollector({})
        
        # Initialize list of agents
        self.agents = list()

        # Initial loop to create agents and fill agents list with them
        for (contents, x, y) in self.grid.coord_iter():
            # Secondary loop
            for i in range(1):
                if(random.random() < .5):
                # Create object of type SlimeAgent
                    ag = SlimeAgent(self.j, random.randint(0, self.w), random.randint(0, self.w))
                # Add new SlimeAgent object to agents list
                    self.agents.append(ag)
                # Place agent onto grid at coordinates x, y
                    self.grid._place_agent((x, y), ag)
                # Add agent to schedule
                    self.schedule.add(ag)
                # Increment j (unique_id variable)
                    self.j += 1

        # Create environment variable as array filled with zeros w x w
        self.env = np.zeros([self.w, self.w])
        # Create next environemnt variable as array filled with zeros and dimensions w x w
        self.nextenv = np.zeros([self.w, self.w])
        # Print out number of agents
        print(self.j)

        self.running = True

    # Step function
    def step(self):
        ''' Create new references to w, k, Dc, Dt, and f to make equations more legible '''
        w = self.w
        k = self.k
        Dc = self.Dc
        Dt = self.Dt
        f = self.f

        # Calculations for cAMP molecule agent movements
        for x in range(self.w):
            for y in range(self.w):
                # Agent and its neighbors
                C, R, L, U, D = self.env[x, y], self.env[(x+1)%w, y], self.env[(x - 1)%w, y], self.env[x, (y+1)%w], self.env[x, (y-1)%w]
                # Curviture of the concentration
                lap = (R + L + U + D - 4 * C)/(self.Dh**2)

                # Move environments along one
                # -k * C = decay | Dc * lap = diffusion of cAMP | Dt = time
                self.nextenv[x, y] = self.env[x, y] + (-k * C + Dc * lap) * Dt
        
        self.env, self.nextenv = self.nextenv, self.env

        # Loop to simulate secretions of cAMP by an agent
        for ag in self.agents:
            # Just secreting some cAMP
            self.env[ag.x-1, ag.y-1] += f * Dt

            # Agent deciding to move
            newx, newy = (ag.x + random.randint(-1, 2)) % w, (ag.y + random.randint(-1, 2)) % w
            diff = (self.env[newx-1, newy-1] - self.env[ag.x-1, ag.y-1]) / 0.1

            # Redundancy for insane values of diff
            if diff > 10:
                diff = 10
            elif diff < -10:
                diff = -10
            if random.random() < np.exp(diff) / (1 + np.exp(diff)):
                ag.x, ag.y = newx, newy

            # Increment number of agents (for testing purposes)
            self.j += 1
#            self.grid._place_agent((x, y), ag)

        # Print out new number of agents (testing)
        print(self.j)
        # Add step to schedule
        self.schedule.step()

# Function for defining portayal
def cAMP_portrayal(molecule):
    # Dictionary for setting portrayal settings of agents
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    # Setting x coordinate of agent in portrayal dict
    portrayal["x"] = SlimeAgent.getX
    # Setting y coordinate of agent in portrayal dict
    portrayal["y"] = SlimeAgent.getY
    # Setting agent color to hex 43566c (a lightish navy)
    portrayal["color"] = "43566c"

    return portrayal

# Telling mesa to create a grid with the agent
canvas_element = CanvasGrid(cAMP_portrayal, 200, 200, 600, 600)

# Setting size of model
model_params = {"height": 200, "width": 200}

# Creating ModularServer
server = ModularServer(SlimeModel, [canvas_element], "cAMP Aggregation Model", model_params)
# Launching Server
server.launch()
