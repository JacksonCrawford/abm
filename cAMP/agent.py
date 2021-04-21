from mesa import Agent
import mesa.space
''' This Agent will run with model.py, but it does not actually display the model. '''
class SlimeAgent(Agent):
    def __init__(self, unique_id, xParam, yParam):
        self.unique_id = unique_id
        self.x = xParam
        self.y = yParam

    def getUniqueID():
        return self.unique_id

    def getX():
        return self.x

    def getY():
        return self.y

class cAMP(Agent):
    def __init__(self, pos, model, unique_id, amount):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = amount

    def getAmt(self):
        return self.amount

    def add(self, amt):
        self.amount += amt

    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)

''' This agent is a work in progress and works with newModel.py '''
class SlimyAgent(Agent):
    def __init__(self, pos, model, unique_id):
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = unique_id
#        self.x = xParam
#        self.y = yParam

        # Number of agents per tile
        self.n = 1
        # Rate of cAMP decay
        self.k = .01
        # Diffusion constant of cAMP
        self.Dc = .03
        # Spatial resolution for cAMP simulation
        self.Dh = .03
        # Time resolution for cAMP simulation
        self.Dt = .5
        # Rate of cAMP secretion by an agent
        self.f = 5
        # Number of rows/columns in spatial array
        self.w = 20



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

    def getNeighbors(self):
        return self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)


    # Step function
    ''' This was originally copied from what I have in model.py, and I am trying to work it into this step method '''
    def step(self):
        # Create new references to w, k, Dc, Dt, and f to make equations more legible
        w = self.w
        k = self.k
        Dc = self.Dc
        Dt = self.Dt
        f = self.f
        Dh = self.Dh

        lap = 0

        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
#        print(neighbors)
#        print("\n")
#        for neighbor in neighbors:
#            lap += neighbor.getUniqueID()
#        lap = (lap - 4 * self.unique_id)/(Dh**2)
#        print(lap)

        

        # Calculations for cAMP molecule agent movements
        '''for x in range(w):
            for y in range(w):
                # Agent and its neighbors
                C, R, L, U, D = self.env[x, y], self.env[(x+1)%w, y], self.env[(x - 1)%w, y], self.env[x, (y+1)%w], self.env[x, (y-1)%w]
                # Curviture of the concentration
                lap = (R + L + U + D - 4 * C)/(self.Dh**2)

                # Move environments along one
                # -k * C = decay | Dc * lap = diffusion of cAMP | Dt = time
                self.nextenv[x, y] = self.env[x, y] + (-k * C + Dc * lap) * Dt

        self.env, self.nextenv = self.nextenv, self.env

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
        self.grid._place_agent((x, y), ag)

        # Print out new number of agents (testing)
        print(self.j)'''
        # Add step to schedule
        #self.schedule.step()
