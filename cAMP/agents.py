from mesa import Agent
import mesa.space

# cAMP agent, one is assigned per cell and it has the amount of cAMP
class cAMP(Agent):
    def __init__(self, pos, model, unique_id, amount):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = amount

    # Get X coordinate of agent
    def getX(self):
        return self.pos[0]

    # Get Y coordinate of agent
    def getY(self):
        return self.pos[1]

    # Get current amount of cAMP
    def getAmt(self):
        return self.amount

    # Add some amount of cAMP
    def add(self, amt):
        self.amount += amt

    # Get immediate neighbors without center or diagonals
    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)

# Slime Mold agent that interacts with the environment made up of cAMP agents
class SlimeAgent(Agent):
    def __init__(self, pos, model, unique_id, color):
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = unique_id
        self.color = color

        if color == "Red":
            self.shade = "#720000"
        elif color == "Green":
            self.shade = "#00741c"
        else:
            self.shade = "#4a7d8e"
        
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

    # Get immediate neighbors without center or diagonals
    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)

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
