from mesa import Agent
import mesa.space

# cAMP agent, one is assigned per cell and it has the amount of cAMP
class cAMP(Agent):
    def __init__(self, pos, model, unique_id, amount):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = amount

    def getX(self):
        return self.pos[0]

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
    def __init__(self, pos, model, unique_id):
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = unique_id

    # Get agent's Unique ID
    def getUniqueID(self):
        return self.unique_id

    # Get agent's X coord
    def getX(self):
        return self.pos[0]

    # Get agent's Y coord
    def getY(self):
        return self.pos[1]

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

    def step(self):
        pass
