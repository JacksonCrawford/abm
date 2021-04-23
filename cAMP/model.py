from mesa import Model
from mesa.time import RandomActivation, SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import random
import math

import numpy as np
from agents import SlimeAgent, cAMP

class SlimeModel(Model):
    def __init__(self, height, width, numAgents, gDense, kRate, dcDiffu, dhRes, dtRes, secRate):
        # number of agents per tile
        self.n = numAgents
        # grid density
        self.gD = gDense
        # rate of cAMP decay
        self.k = kRate
        # diffusion constant of cAMP
        self.Dc = dcDiffu
        # spatial resolution for cAMP simulation
        self.Dh = dhRes
        # time resolution for cAMP simulation
        self.Dt = dtRes
        # rate of cAMP secretion by an agent
        self.f = secRate
        # number of rows/columns in spatial array
        self.w = 50

        # height of grid
        self.height = 50
        # width of grid
        self.width = 50

        # counter for generating sequential unique id's
        self.j = 0

        # Create randomly ordered scheduler
        self.schedule = SimultaneousActivation(self)
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
    
        r = 0
    
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
            if self.gD % 1 != 0:
                r = random.random()
                if r <= self.gD:
                    for i in range(self.n):
                        ag = SlimeAgent([x, y], self, self.j)
                        self.agents.append(ag)
                        self.grid.place_agent(ag, tuple([x, y]))
                        self.schedule.add(ag)
                        self.j += 1
            else:
                for i in range(self.n):
                    # Create object of type SlimeAgent
                    ag = SlimeAgent([x, y], self, self.j)
                    # Add new SlimeAgent object to agents list
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
                cNeighbors.clear()
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
    amt = 0
    if type(agent) is SlimeAgent:
        # Dictionary for setting portrayal settings of SlimeAgent agent
        portrayal = {"Shape": "circle", "w": 1, "h": 1, "Filled": "true", "Layer": 1, "r": .65}
        # Setting x coordinate of agent in portrayal dict
        portrayal["x"] = agent.getX()
        # Setting y coordinate of agent in portrayal dict
        portrayal["y"] = agent.getY()
        # Setting agent color to red 
#        portrayal["Color"] = "#357ecb"
        portrayal["Color"] = "red"
    elif type(agent) is cAMP:
        # Dictionary for setting portrayal settings of cAMP agent
        portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
        # Setting x coordinate of agent in portrayal dict
        portrayal["x"] = agent.getX()
        # Setting y coordinate of agent in portrayal dict
        portrayal["y"] = agent.getY()
        # Setting amount of cAMP to amt
        amt = agent.getAmt()

        # Change color to darker shade of gray with increased cAMP amount
        if amt == 0:
            portrayal["Color"] = "white"
        elif amt < 3:
            portrayal["Color"] = "#c3c3c3"
        elif amt < 6:
            portrayal["Color"] = "#b1b1b1"
        elif amt < 9:
            portrayal["Color"] = "#a1a1a1"
        elif amt < 12:
            portrayal["Color"] = "#929292"
        elif amt < 15:
            portrayal["Color"] = "#868686"
        elif amt < 18:
            portrayal["Color"] = "#7b7b7b"
        elif amt < 21:
            portrayal["Color"] = "#6e6e6e"
        else:
            portrayal["Color"] = "#646464"

    return portrayal

# Telling mesa to create a grid with the agent

#chart_element = ChartModule([{"Label": "Molds", "Color":"#43566c"}, {"Label":"cAMP's", "Color":"#acdabd"}])

# Setting size of model
model_params = {
        "height": 200,
        "width": 200,
        "numAgents": UserSettableParameter("slider", "Number of Agents", 1, 1, 10, 1),
        "gDense": UserSettableParameter("slider", "Density of Agents on Grid", .5, 0, 1, .1),
        "kRate": UserSettableParameter("slider", "Rate of cAMP decay", 0.5, 0, 1, .1),
        "dcDiffu": UserSettableParameter("slider", "Diffusion Constant of cAMP", .001, 0, .01, .001),
        "dhRes": UserSettableParameter("slider", "Spatial Resolution for cAMP Simulation", .01, 0, .1, .01),
        "dtRes": UserSettableParameter("slider", "Time Resolution for cAMP Simulation", .01, .01, .1, .01),
        "secRate": UserSettableParameter("slider", "Rate of cAMP Secretion by an Agent", 5, 1, 15, 1)
        }

canvas_element = CanvasGrid(cAMP_portrayal, 50, 50, 550, 550)


# Creating ModularServer
server = ModularServer(SlimeModel, [canvas_element], "Keller-Segel Slime Mold Aggregation Model", model_params)
# Launching Server
server.launch()
