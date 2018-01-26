from Coordinate import Coordinate
from datetime import *
import time


# Class node
class Node(object):
    # Number of pickup/delivery nodes
    n_nodes = 1
    # Number of depots
    d_nodes = 1
    
    def __init__(self, type, id, x, y, demand):
        self.type = type
        self.id = id
        self.coord = Coordinate(x, y)
        self.arrival_t = 0
        self.load =  {'p1': 0,
                      'p2': 0,
                      'p3': 0,
                      'p4': 0,
                      's1': 0,
                      's2': 0,
                      's3': 0}        
        self.id_next = None
        self.demand = demand
    
    def get_demand(self):
        return self.demand
    
    def get_load(self):
        return self.load
    def get_type(self):
        return self.type
    
    def set_type(self, type):
        self.type = type

    def get_id_next(self):
        return self.id_next

    def set_id_next(self, id_next):
        self.id_next = id_next 

    def set_arrival_t(self, arrival_t):
        self.arrival_t = arrival_t

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle

    def set_load(self, load):
        self.load = load

    def get_id(self):
        return self.id

    def get_arrival_t(self):
        return self.arrival_t
    
    def get_load(self):
        return self.load

    def get_load_0(self):
        return {id:int(self.load[id]) for id in self.load.keys() if int(self.load[id])>0}

    def get_coord(self):
        return self.coord

    @classmethod
    def increment_id(self):
        Node.n_nodes = Node.n_nodes + 1

    @classmethod
    def increment_id_depot(self):
        Node.d_nodes = Node.d_nodes + 1

    @classmethod
    def get_n_nodes(self):
        return Node.n_nodes

    @classmethod
    def get_d_nodes(self):
        return Node.d_nodes
    


    @classmethod
    def factory_node(self, type, id, x, y, demand):
        if type == 'DL':
            return NodeDL(type, id, x, y, demand)
        elif type == 'PK':
            return NodePK(type, id, x, y, demand)
        elif type == 'DP':
            return NodeDepot(type, id, x, y, demand)
        else:
            return None
    
    @classmethod
    def copy_node(self, node):
        return Node.factory_node(node.get_type(), node.get_id(), node.get_coord().get_x(), node.get_coord().get_y(), node.get_demand())
    
    def __str__(self):
        return " "+str(self.get_id()) + str(self.coord) + " " + str({id:int(self.demand[id]) for id in self.demand.keys() if int(self.demand[id])!=0 })

# Pickup node
class NodePK(Node):
    def __init__(self, type, id, x, y, demand):
        new_id = id
        if new_id == None:
            new_id = "pk" + str(Node.get_n_nodes())
        Node.increment_id()
        Node.__init__(self, type, new_id, x, y, demand)

    def set_arrival_t(self, arrival_t):
        self.arrival_t = arrival_t

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle

    def set_load(self, load):
        self.load = load



    def __str__(self):
        return '|PK|' + super().__str__() + ' - LOAD: ' + str({id:int(self.load[id]) for id in self.load.keys() if int(self.load[id])>0}) + ' - ARR: ' + datetime.fromtimestamp(int(self.arrival_t)).strftime('%Y-%m-%d %H:%M')

# Delivery node
class NodeDL(Node):
    def __init__(self, type, id, x, y, demand):
        new_id = id
        if new_id == None:
            new_id = "dl" + str(Node.get_n_nodes())
        Node.increment_id()
        Node.__init__(self, type, new_id, x, y, demand)

    def __str__(self):
        return '|DL|' + super().__str__() + ' - LOAD: ' + str({id:int(self.load[id]) for id in self.load.keys() if int(self.load[id])>0}) + ' - ARR: ' + datetime.fromtimestamp(int(self.arrival_t)).strftime('%Y-%m-%d %H:%M')



# Departure/arrival node
class NodeDepot(Node):
    def __init__(self, type, id, x, y, demand):
        new_id = id
        if new_id == None:
            new_id = "dp" + str(Node.get_d_nodes())
        Node.increment_id_depot()
        Node.__init__(self, type, new_id, x, y, demand)

    def __str__(self):
        # + self.load + self.vehicle + self.arrival_t
        arr = datetime.fromtimestamp(int(self.arrival_t)).strftime('%Y-%m-%d %H:%M')
        if(int(self.arrival_t)==0):
            arr = '0'
        return '|->|' + super().__str__() + ' - LOAD: ' + str({id:int(self.load[id]) for id in self.load.keys() if int(self.load[id])>0}) + ' - ARR: ' + arr
