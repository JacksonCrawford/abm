from mesa import Agent
import mesa.space
from colour import Color

# Agent for visualizing row amounts of cAMP
class DataVis(Agent):
    def __init__(self, pos, model, unique_id):
        self.pos = pos
        self.rowAmt = 0
        self.color = Color("blue")

    # Method to get X coord
    def getX(self):
        return self.pos[0]

    # Method to get Y coord
    def getY(self):
        return self.pos[1]

    # Method to get the row amount value
    def getRowAmt(self):
        return self.rowAmt

    # Method to set the row amount for color decisions
    def setRowAmt(self, amt):
        self.rowAmt = amt

    # Method to get color for portrayal
    def getColor(self):
        # Change increment size here (a bit buggy :/)
        inc = 1

        '''formula = (self.rowAmt * .025) / inc
        if formula > 1:
            self.color.saturation = formula
        else:
            self.color = Color("red")'''

        if self.rowAmt < inc:
            self.color.saturation = 0.027
        elif self.rowAmt < (2 * inc):
            self.color.saturation = 0.054
        elif self.rowAmt < (3 * inc):
            self.color.saturation = 0.081
        elif self.rowAmt < (4 * inc):
            self.color.saturation = 0.108
        elif self.rowAmt < (5 * inc):
            self.color.saturation = 0.135
        elif self.rowAmt < (6 * inc):
            self.color.saturation = 0.162
        elif self.rowAmt < (7 * inc):
            self.color.saturation = 0.189
        elif self.rowAmt < (8 * inc):
            self.color.saturation = 0.216
        elif self.rowAmt < (9 * inc):
            self.color.saturation = 0.143
        elif self.rowAmt < (10 * inc):
            self.color.saturation = 0.27
        elif self.rowAmt < (11 * inc):
            self.color.saturation = 0.297
        elif self.rowAmt < (12 * inc):
            self.color.saturation = 0.324
        elif self.rowAmt < (13 * inc):
            self.color.saturation = 0.351
        elif self.rowAmt < (14 * inc):
            self.color.saturation = 0.378
        elif self.rowAmt < (15 * inc):
            self.color.saturation = 0.405
        elif self.rowAmt < (16 * inc):
            self.color.saturation = 0.432
        elif self.rowAmt < (17 * inc):
            self.color.saturation = 0.459
        elif self.rowAmt < (18 * inc):
            self.color.saturation = 0.486
        elif self.rowAmt < (19 * inc):
            self.color.saturation = 0.513
        elif self.rowAmt < (20 * inc):
            self.color.saturation = 0.540
        elif self.rowAmt < (21 * inc):
            self.color.saturation = 0.567
        elif self.rowAmt < (22 * inc):
            self.color.saturation = 0.594
        elif self.rowAmt < (23 * inc):
            self.color.saturation = 0.621
        elif self.rowAmt < (24 * inc):
            self.color.saturation = 0.648
        elif self.rowAmt < (25 * inc):
            self.color.saturation = 0.675
        elif self.rowAmt < (26 * inc):
            self.color.saturation = 0.702
        elif self.rowAmt < (27 * inc):
            self.color.saturation = 0.729
        else:
            self.color = Color("black")

        return self.color.hex_l

# Agent to represent numerical data of row amounts of cAMP alongside color
class NumDataVis:
    def __init__(self, pos, model, unique_id):
        self.pos = pos
        self.rowAmt = 0
        self.color = Color("blue")

    # Method to get X coord
    def getX(self):
        return self.pos[0]

    # Method to get Y coord
    def getY(self):
        return self.pos[1]

    # Method to get the row amount value
    def getRowAmt(self):
        return self.rowAmt

    # Method to set the row amount for color decisions
    def setRowAmt(self, amt):
        self.rowAmt = amt

    # Method to get the sliced number for rowAmt
    def getNum(self):
        amt = str(self.rowAmt)
        return amt[0:4:]


# cAMP agent, one is assigned per cell and it has the amoumt of cAMP
class cAMP(Agent):
    def __init__(self, pos, model, unique_id, amount, decRate):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = amount
        self.decay = decRate

    # Get X coordinate of agent
    def getX(self):
        return self.pos[0]

    # Get Y coordinate of agent
    def getY(self):
        return self.pos[1]

    # Get current amount of cAMP
    def getAmt(self):
        return self.amount

    # Get decay rate
    def getDecayRate(self):
        return self.decay

    # Add some amount of cAMP
    def add(self, amt):
        if (self.amount + amt) > 0:
            self.amount += amt
        else:
            self.amount = 0

    # Get immediate neighbors without center or diagonals
    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)


    # Set decay rate
    def setDecayRate(self, drParam):
        self.decay = drParam

# Slime Mold agent that interacts with the environment made up of cAMP agents
class SlimeAgent(Agent):
    def __init__(self, pos, model, unique_id, secRate, color):
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = unique_id
        self.color = color
        self.secRate = 2

        if color == "Red":
            self.shade = "#720000"
        elif color == "Green":
            self.shade = "#00741c"
        else:
            self.shade = "#4a7d8e"

        self.secRate = 1

        self.layer = 1

    # Get agent's Unique ID
    def getUniqueID(self):
        return self.unique_id

    # Get agent's X coord
    def getX(self):
        return self.pos[0]

    # Get agent's Y coord
    def getY(self):
        return self.pos[1]

    # Get agent's color (string colorname)
    def getColor(self):
        return self.color

    # Get shade of agent's color (hex)
    def getShade(self):
        return self.shade

    # Get list of shades based on string colorname
    def getShades(self):
        if self.color == "Red":
            return ["#720000", "#8b0000", "#9b0000", "#a90000", "#bd0000", "#cd0000", "#e60000", "#ff0000"]
        elif self.color == "Green":
            return ["#00741c", "#00821f", "#009121", "#00a825", "#00b427", "#00d72e", "#00e632", "#00f735"]

        return ["#4a7d8e", "#438094", "#4693ac", "#45a0be", "#41b1d6", "#35b9ef", "#1fbef1", "#02c1ff"]

    # Get layer of agent
    def getLayer(self):
        return self.layer

    # Get secretion rate
    def getSecRate(self):
        return self.secRate;

    # Increment layer by 1
    def addLayer(self):
        self.layer += 1

    # Set agent's Unique ID
    def setUniqueID(self, uParam):
        self.unique_id = uParam

    # Set agent's X coord
    def setX(self, xParam):
        self.x = xParam

    # Set agent's Y coord
    def setY(self, yParam):
        self.y = yParam

    # Set secretion rate
    def setSecRate(self, srParam):
        self.secRate = srParam

    # Get immediate neighbors without center or diagonals
    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)

    # Get immediate SlimeAgent neighbors without center or diagonals
    def getSlimeNeighbors(self):
        slimeNeighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        i = 0;
        for agent in slimeNeighbors:
            if type(agent) is cAMP:
                slimeNeighbors.pop(i)
            i += 1
#            if type(agent) is cAMP:
#                slimeNeighbors.remove(agent)


        return slimeNeighbors

    # Move to a specified position
    def move(self, newPos):
        self.model.grid.move_agent(self, newPos)

    # Set string colorname for agent
    def setColor(self, colorName):
        self.color = colorName

    # Set agent's shade in hex
    def setShade(self, hexCode):
        self.shade = hexCode

    # All step interaction is done with the environment, and is therefore calculated in the Model itself
    def step(self):
        pass
