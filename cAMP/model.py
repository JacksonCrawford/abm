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

'''
    Change only the value of masterHeight to change the dimensions of the grid
        because it must always be a square.
'''

masterHeight = 50
masterWidth = masterHeight

class SlimeModel(Model):
    def __init__(self, height, width, color, numAgents, gDense, kRate, dcDiffu, dhRes, dtRes, secRate):
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
        self.w = masterHeight
        # agent color
        self.color = color

        # height of grid
        self.height = masterHeight
        # width of grid
        self.width = masterWidth

        # counter for generating sequential unique id's
        self.j = 0

        # Create randomly ordered scheduler
        self.schedule = SimultaneousActivation(self)
        # Create grid (of type MultiGrid to support multiple agents per cell
        self.grid = MultiGrid(self.height, self.width, torus=False)

        # Initialize list of cAMP molecules
        self.cAMPs = list()

        # Create datacollector to retrieve total amount of cAMP on the grid
        self.datacollector = DataCollector({
            "Total Amount of cAMP": self.getAmts
        })
        
        # Variable for storing random numbers
        r = 0
    
        # Initial loop to create agents and fill agents list with them
        for (contents, x, y) in self.grid.coord_iter():
            # Create object of type cAMP
            cell = cAMP([x, y], self, self.j, 0)
            # Add random amoutn of cAMP to cell (<1)
            cell.add(random.random())
            # Place cAMP onto grid at coordinates x, y
            self.grid._place_agent((x, y), cell)
            # Add cAMP molecule to list
            self.cAMPs.append(cell)

            # Loop to create SlimeAgents
            if self.gD % 1 != 0:
                r = random.random()
                if r <= self.gD:
                    for i in range(self.n):
                        # Create object of type SlimeAgent
                        ag = SlimeAgent([x, y], self, self.j, self.color)
                        # Place agent onto grid at coordinates x, y
                        self.grid.place_agent(ag, tuple([x, y]))
                        # Add agent to schedule
                        self.schedule.add(ag)
                        # Increment j (unique_id variable)
                        self.j += 1
            else:
                for i in range(self.n):
                    # Create object of type SlimeAgent
                    ag = SlimeAgent([x, y], self, self.j, self.color)
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

    # Method for getting total cAMP amount
    def getAmts(self):
        # Initialize empty total variable
        total = 0
        # Loop to get total amount of cAMP from cAMPs list
        for molecule in self.cAMPs:
            total += molecule.getAmt()

        return total

    # Step method
    def step(self):
        cNeighbors = list()
        neighbors = list()
        lap = 0
        amt = 0
        cAMPobj = cAMP
        newDiag = 0
        oldDiag = 0
        nAgents = 0
        layer = 1

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
                nAgents = len(contents) - 1
                for agent in contents[1::]:
                    agent.addLayer()
                    layer = agent.getLayer()
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

                    # Only change color of agent that is on top of a stack
                    if layer >= nAgents:
                        self.pickColor(agent, nAgents)

        # Add step to schedule
        self.schedule.step()
        # Collect new data
        self.datacollector.collect(self)


    def pickColor(self, topAgent, nAgents):
        shade = topAgent.getShades()
        if nAgents <= 2:
            topAgent.setShade(shade[0])
        elif nAgents == 3:
            topAgent.setShade(shade[1])
        elif nAgents == 4:
            topAgent.setShade(shade[2])
        elif nAgents == 5:
            topAgent.setShade(shade[3])
        elif nAgents == 6:
            topAgent.setShade(shade[4])
        elif nAgents == 7:
            topAgent.setShade(shade[5])
        elif nAgents == 8:
            topAgent.setShade(shade[6])
        elif nAgents == 9:
            topAgent.setShade(shade[7])


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
        portrayal["Color"] = agent.getShade()
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

# Create a chart to represent total amount of cAMP on the grid
chart_element = ChartModule([{"Label":"Total Amount of cAMP", "Color":"#85c6e7"}])

# Setting size of model
model_params = {
        "height": 200,
        "width": 200,
        "numAgents": UserSettableParameter("slider", "Number of Agents", 1, 1, 10, 1),
        "gDense": UserSettableParameter("slider", "Density of Agents on Grid", .5, 0, 1, .1),
        "kRate": UserSettableParameter("slider", "Rate of cAMP decay", 1, 0, 5, .5),
        "dcDiffu": UserSettableParameter("slider", "Diffusion Constant of cAMP", .001, 0, .01, .001),
        "dhRes": UserSettableParameter("slider", "Spatial Resolution for cAMP Simulation", .01, 0, .1, .01),
        "dtRes": UserSettableParameter("slider", "Time Resolution for cAMP Simulation", .01, .01, .1, .01),
        "secRate": UserSettableParameter("slider", "Rate of cAMP Secretion by an Agent", 1, 0, 15, 1),
        "color": UserSettableParameter("choice", "Agent Color", value="Blue", choices=["Blue", "Red", "Green"])
        }

# Create grid for agents of size 550px x 550px, with 50 tiles along x and 50 along y
canvas_element = CanvasGrid(cAMP_portrayal, masterHeight, masterWidth, 550, 550)


# Creating ModularServer
server = ModularServer(SlimeModel, [canvas_element, chart_element], "Keller-Segel Slime Mold Aggregation Model", model_params)
# Launching Server
server.launch()
