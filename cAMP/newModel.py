from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import random
import math

import numpy as np
from agent import SlimyAgent, cAMP

''' This is the model where I am playing around with the step function, which I believe to be the problem. '''

class SlimeModel(Model):
    def __init__(self, height, width):
        # number of agents per tile
        self.n = 1
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
        self.height = 20
        # width of grid
        self.width = 20

        # counter for generating sequential unique id's
        self.j = 0

        # Create randomly ordered scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = MultiGrid(self.height, self.width, torus=False)

        # Going to add this functionality once the visualization gets going.
#        self.datacollector = DataCollector({})

        # Initialize list of cells and slime agents
        self.cells = list()
        self.agents = list()

#        x, y = 0, 0
        # Initial loop to create agents and fill agents list with them
        for (contents, x, y) in self.grid.coord_iter():
            # Secondary loop
            for i in range(10):
                if(random.random() < .5):
                    #x, y = random.randint(0, self.w), random.randint(0, self.w)
                    # Create object of type cAMP
                    cell = cAMP([x, y], self, self.j, 0)
                    # Add random amount of cAMP to cell (<1)
                    cell.add(random.random())
                    # Add new Tile object to cells list
                    self.cells.append(cell)
                    # Place cAMP onto grid at coordinates x, y
                    self.grid.place_agent(cell, tuple([x, y]))
                    # Create object of type SlimyAgent
                    ag = SlimyAgent([x, y], self, self.j)
                    # Add new SlimyAgent object to agents list
                    self.agents.append(ag)
                    # Place agent onto grid at coordinates x, y
                    self.grid.place_agent(ag, tuple([x, y]))
                    # Add agent to schedule
                    self.schedule.add(ag)
                    # Increment j (unique_id variable)
                    self.j += 1

        # Create environment variable as array filled with zeros w x w
        self.env = np.zeros([self.w, self.w])
        # Create next environemnt variable as array filled with zeros and dimensions w x w
        self.nextenv = np.zeros([self.w, self.w])
        # Print out number of agents
        print("# of agents:", self.j)

        self.running = True

    # Step function
    ''' 
        Not sure if the environment interaction should go here and the agent to agent interaction should go
            in the agent class, but my principle struggle is dealing with the env aspects of Sayama's code
    '''
    def step(self):
        sNeighbors = list()
        cNeighbors = list()
        neighbors = list()
        lap = 0
        amt = 0

        # Iterate thorugh every grid spot (cuasing inf loop?)
        for (contents, x, y) in self.grid.coord_iter():
            # Iterate through all contents of a grid cell
            for obj in contents:
                # Proceed if objecti s a cAMP molecule
                if type(obj) is cAMP:
                    # Get all neighbors (excuding self)
                    neighbors = obj.getNeighbors()
                    # Examine each neighbor
                    for neighbor in neighbors:
                        # Add SlimyAgent neighbors to sNeighbors and cAMP agents to cNeighbors
                        if type(neighbor) is SlimyAgent:
                            sNeighbors.append(neighbor)
                        else:
                            cNeighbors.append(neighbor)
                    # Loop through each cAMP neighbor
                    for mol in cNeighbors:
                        # Get amount of cAMP
                        amt = mol.getAmt()
                        # Add amount to variable lap
                        lap += amt
                    # Get center object's amount of cAMP
                    amt = obj.getAmt()
                    # Calculate laplacian
                    lap = (lap - 4 * amt)/(self.Dh**2)
                    print(lap)
                    exit()
                    

        self.schedule.step()

''' Server elements '''

# Function for defining portayal
def cAMP_portrayal(molecule):
    # Dictionary for setting portrayal settings of agents
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    # Setting x coordinate of agent in portrayal dict
    portrayal["x"] = SlimyAgent.getX
    # Setting y coordinate of agent in portrayal dict
    portrayal["y"] = SlimyAgent.getY
    # Setting agent color to hex 43566c (a lightish navy)
    portrayal["color"] = "#43566c"

    return portrayal

# Telling mesa to create a grid with the agent
canvas_element = CanvasGrid(cAMP_portrayal, 200, 200, 600, 600)

# Setting size of model
model_params = {"height": 200, "width": 200}

# Creating ModularServer
server = ModularServer(SlimeModel, [canvas_element], "cAMP Aggregation Model", model_params)
# Launching Server
server.launch()
