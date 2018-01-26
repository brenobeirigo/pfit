import random
class Vehicle(object):
    
    def __init__(self, type, id, pos, capacity):
        self.id = id
        self.pos = pos
        self.capacity = capacity
        self.path = dict()
        self.type = type

        # Color of vehicle path
        self.color = str("#%06x" % random.randint(0, 0xFFFFFF))
        
    @classmethod
    def factory_vehicle(self, type, id, pos, capacity):
        if type == 'DARP':
            return Vehicle(type, id, pos, capacity)
        elif type == 'SARP_PL':
            return VehicleParcelLockers(type, id, pos, capacity)

    def get_id(self):
        return self.id

    def get_color(self):
        return self.color
    
    def add_node(self, node):
        self.path[node.get_id()] = node

    def get_pos(self):
        return self.pos

    def get_capacity(self):
        return self.capacity

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def __str__(self):
        current_node = self.pos.get_id()
        print(self.path.keys())
        s = '#' + self.get_id() + ':\n'
        while current_node in self.path.keys():
            next_node = self.path[current_node].get_id_next()
            s += str(current_node) + ' -> ' + str(next_node)\
                + ': ' + str(self.path[current_node]) + '\n'
            current_node = next_node
        return s
    
    def __repr__(self):
        print ("VHEAAA")
        current_node = self.pos.get_id()
        print(self.path.keys())
        s = '#' + self.get_id() + ':\n'
        while current_node in self.path.keys():
            next_node = self.path[current_node].get_id_next()
            s += str(current_node) + ' -> ' + str(next_node)\
                + ': ' + str(self.path[current_node]) + '\n'
            current_node = next_node
        return s

class VehicleParcelLockers(Vehicle):

    def __init(self, type, id, pos, capacity):
        super().__init__(type, id, pos, capacity)
    
    def __str__(self):
        current_node = self.pos.get_id()
        s = '# VEH' + self.get_id() + ' - ' + str(self.pos) + ' \n ' + str(self.capacity) + ':\n'

        while current_node in self.path.keys():
            next_node = self.path[current_node].get_id_next()
            s += str(current_node) + ' -> ' + str(next_node)\
                + ': ' + str(self.path[current_node]) + '\n'
            current_node = next_node
        return s
    def __repr__(self):
        current_node = self.pos.get_id()
        s = '# VEH' + self.get_id() + ' - ' + str(self.pos) + ' \n ' + str(self.capacity) + ':\n'

        while current_node in self.path.keys():
            next_node = self.path[current_node].get_id_next()
            s += str(current_node) + ' -> ' + str(next_node)\
                + ': ' + str(self.path[current_node]) + '\n'
            current_node = next_node
        return s