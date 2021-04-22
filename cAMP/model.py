from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import random
import math

import numpy as np
from agent import SlimeAgent, cAMP

class SlimeModel(Model):
    def __init__(self, height, width):
        # number of agents per tile
        self.n = 1
        # rate of cAMP decay
        self.k = 1
        # diffusion constant of cAMP
        self.Dc = .001
        # spatial resolution for cAMP simulation
        self.Dh = .01
        # time resolution for cAMP simulation
        self.Dt = .01
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
        '''self.datacollector = DataCollector({
            "Molds": lambda m: m.schedule.get_agent_count(SlimeAgent),
            "cAMP's": lambda m: m.schedule.get_agent_count(cAMP),
            })'''

        # Initialize list of cells and slime agents
        self.cells = list()
        self.agents = list()

        # Initial loop to create agents and fill agents list with them
        for (contents, x, y) in self.grid.coord_iter():
            # Create object of type cAMP
            cell = cAMP([x, y], self, self.j, 0)
            # Add random amoutn of cAMP to cell (<1)
            cell.add(random.random())
            # Add new cell to cells list
            self.cells.append(cell)
            # Place cAMP onto grid at coordinates x, y
            self.grid._place_agent((x, y), cell)

            # Loop to create SlimeAgents            
            for i in range(self.n):
                # Create object of type SlimeAgent
                ag = SlimeAgent([x, y], self, self.j)
                # Add new SlimeAgent object to agents list
                self.agents.append(ag)
                # Place agent onto grid at coordinates x, y
                self.grid._place_agent((x, y), cell)
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
    def step(self):
        cNeighbors = list()
        neighbors = list()
        lap = 0
        amt = 0
        cAMPobj = cAMP
        newDiag = 0
        oldDiag = 0

        ''' Perform cAMP decay and diffusion actions '''
        for (contents, x, y) in self.grid.coord_iter():
            # Iterate through all contents of a grid cell
            for obj in contents:
                # Set cAMP object to first value on cell (always of type cAMP)
                cAMPobj = contents[0]
                # Get all neighbors (excuding self)
                neighbors = obj.getNeighbors()
                # Wipe cNeighbors
                cNeighbors = list()
                # Examine each neighbor
                for neighbor in neighbors:
                    # Add cAMP neighbors to list
                    if type(neighbor) is cAMP:
                        cNeighbors.append(neighbor)

                # Loop through each cAMP neighbor to calculate the laplace
                lap = 0
                for mol in cNeighbors:
                    # Get amount of cAMP
                    amt = mol.getAmt()
                    # Add amount to variable lap
                    lap += amt

                if type(obj) is cAMP:
                    # Get center object's amount of cAMP
                    amt = obj.getAmt()
                    # Calculate laplacian (curviture of the concentration)
                    lap = (lap - 4 * amt)/(self.Dh**2)
                    # Add decay to amount of cAMP for the agent
                    obj.add((-self.k * amt + self.Dc * lap) * self.Dt)
                
                # Loop through each mold agent and move it
                for agent in contents[1::]:
                    # Add cAMP secretion to the cell that the agent shares with a cAMP object (a little confusing on the names, oops!)
                    cAMPobj.add(self.f * self.Dt)
                    # Decide whether or not to move
                    newx = (x + random.randint(-1, 2)) % self.w
                    newy = (y + random.randint(-1, 2)) % self.w

                    # Calculate differences
                    newDiag = ((self.grid[newx-1][newy-1])[0]).getAmt()
                    diff = ((self.grid[x-1][y-1])[0]).getAmt()
                    
                    # Fix if there are crazy values for diff
                    if diff > 10:
                        diff = 10
                    elif diff < 10:
                        diff = -10

                    # Decide to move
                    if random.random() < np.exp(diff) / (1 + np.exp(diff)):                    
                        agent.move(tuple([newx, newy]))

        self.schedule.step()
#        self.datacollector.collect(self)

''' Server elements '''

# Function for defining portayal
def cAMP_portrayal(agent):
    portrayal = dict()
    if type(agent) is SlimeAgent:
        # Dictionary for setting portrayal settings of agents
        portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
        # Setting x coordinate of agent in portrayal dict
        portrayal["x"] = mold.getX
        # Setting y coordinate of agent in portrayal dict
        portrayal["y"] = mold.getY
        # Setting agent color to blue
        portrayal["color"] = "blue"

    return portrayal

# Telling mesa to create a grid with the agent
canvas_element = CanvasGrid(cAMP_portrayal, 50, 50, 500, 500)

#chart_element = ChartModule([{"Label": "Molds", "Color":"#43566c"}, {"Label":"cAMP's", "Color":"#acdabd"}])

# Setting size of model
model_params = {"height": 200, "width": 200}

# Creating ModularServer
server = ModularServer(SlimeModel, [canvas_element], "cAMP Aggregation Model", model_params)
# Launching Server
server.launch()
