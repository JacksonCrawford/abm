from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from mesa.visualization.modules import CanvasGrid, ChartModule, BarChartModule
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

        # Initialize dict for datacollector with total datacollector
        dc = {"Total Amount of cAMP": self.getAmts}

        # Initialize for iterating through columns (x) and rows (y)
        self.x = 0
        self.y = 0

        # Loop to fill datacollector dictionary with dict entries for each column and row
        for x in range(masterWidth):
            dc.update({("x: " + str(x)): self.getColAmts})
            dc.update({("y: " + str(x)): self.getRowAmts})

        # Create datacollector to retrieve total amounts of cAMP from dc dict created above
        self.datacollector = DataCollector(dc)

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

    def getRowAmts(self):
        total = 0
        for x in range(masterWidth):
            try:
                total += self.grid.get_cell_list_contents((x, self.y))[0].getAmt()
            except IndexError:
                continue

        if self.y == 49:
            self.y = 0
        else:
            self.y += 1

        return total

    def getColAmts(self):
        total = 0
        for y in range(masterHeight):
            try:
                total += self.grid.get_cell_list_contents((self.x, y))[0].getAmt()
            except IndexError:
                continue

        if self.x == 49:
            self.x = 0
        else:
            self.x += 1

        return total

    # Step method
    def step(self):
        cNeighbors = list()
        neighbors = list()
        lap = 0
        amtSelf = 0
        cAMPobj = cAMP
        newDiag = 0
        oldDiag = 0
        nAgents = 0
        layer = 1

        ''' Perform cAMP decay and diffusion actions '''
        for (contents, x, y) in self.grid.coord_iter():
            # Initialize number of agents for layer coloring
            nAgents = len(contents) - 1
            # Reset lap to 0
            lap = 0 

            # Set cAMPobj to current tile's cAMP agent
            cAMPobj = contents[0]
            # Set neighbors to cAMPobj's neighbors (Von Neumann)
            neighbors = cAMPobj.getNeighbors()
            # Add cAMP objects form neighbors to cNeighbors
            for neighbor in neighbors:
                if type(neighbor) is cAMP:
                    cNeighbors.append(neighbor)

            # Add sum of neighbors to lap
            for mol in cNeighbors:
                lap += mol.getAmt()

            amtSelf = cAMPobj.getAmt()
            # Reassign lap to the laplacian (using previous neighbor sum value)
            lap = (lap - 4 * amtSelf)/(self.Dh**2)
            # Add decay to current cAMP object
            cAMPobj.add((-self.k * amtSelf + self.Dc * lap) * self.Dt)

            # Wipe cNeighbors
            cNeighbors.clear()

            # Iterate through all contents of a grid cell
            for agent in contents[1::]:
                # Get all neighbors (excuding self)
                neighbors = agent.getNeighbors()
                # Examine each neighbor
                for neighbor in neighbors:
                    # Add cAMP neighbors to list
                    if type(neighbor) is cAMP:
                        cNeighbors.append(neighbor)

                # Add cAMP secretion to the cell that the agent shares with a cAMP object
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

                # Layers for coloring agents based on density
                agent.addLayer()
                layer = agent.getLayer()
                # Only change color of agent that is on top of a stack
                if layer >= nAgents:
                    self.pickColor(agent, nAgents)

                # Wipe cNeighbors
                cNeighbors.clear()

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
        elif amt < 1:
            portrayal["Color"] = "#f5f5f5"
        elif amt < 2:
            portrayal["Color"] = "#e9e9e9"
        elif amt < 3:
            portrayal["Color"] = "#d9d9d9"
        elif amt < 4:
            portrayal["Color"] = "#cccccc"
        elif amt < 5:
            portrayal["Color"] = "#c1c1c1"
        elif amt < 6:
            portrayal["Color"] = "#b4b4b4"
        elif amt < 7:
            portrayal["Color"] = "#a3a3a3"
        elif amt < 8:
            portrayal["Color"] = "#949494"
        elif amt < 9:
            portrayal["Color"] = "#8a8a8a"
        elif amt < 10:
            portrayal["Color"] = "#787878"
        elif amt < 11:
            portrayal["Color"] = "#696969"
        elif amt < 12:
            portrayal["Color"] = "#5b5b5b"
        elif amt < 13:
            portrayal["Color"] = "#505050"
        elif amt < 14:
            portrayal["Color"] = "#464646"
        elif amt < 15:
            portrayal["Color"] = "#3c3c3c"
        elif amt < 16:
            portrayal["Color"] = "#313131"
        elif amt < 17:
            portrayal["Color"] = "#282828"
        elif amt < 18:
            portrayal["Color"] = "#1d1d1d"
        elif amt < 19:
            portrayal["Color"] = "#1515150"
        elif amt < 20:
            portrayal["Color"] = "#0c0c0c"
        elif amt < 21:
            portrayal["Color"] = "#090909"
        else:
            portrayal["Color"] = "#000000"

    return portrayal

# Create list of datacollectors
xCollectors = list()
yCollectors = list()

# Loop to create bars for bar graphs
coord = 0
for x in range(masterHeight):
    xCollectors.append({"Label": ("x: " + str(coord)), "Color": "#85c6e7"})
    coord += 1

coord = 0
for y in range(masterWidth):
    yCollectors.append({"Label": ("y: " + str(coord)), "Color": "#85c6e7"})
    coord += 1

# Create a bar charts to represent column and row amounts of relative to grid
bar_chart_element_col = BarChartModule(xCollectors, canvas_width = 550)
bar_chart_element_row = BarChartModule(yCollectors, canvas_width = 550)

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
server = ModularServer(SlimeModel, [canvas_element, bar_chart_element_col, bar_chart_element_row, chart_element], "Keller-Segel Slime Mold Aggregation Model", model_params)
# Launching Server
server.launch()
