from Node import *
from Dao import Dao
import pprint


class Response(object):

    def __init__(self, vehicles, arcs, rides, travel_t, load, arrival_t, DAO):
        self.vehicles = vehicles
        self.DAO = DAO
        self.arcs = arcs
        self.rides = rides
        self.travel_t = travel_t
        self.load = load
        self.arrival_t = arrival_t
        self.path = None
        self.create_path()

    # Creates a response for a method, placing the step-by-step information
    # in each node.
    def create_path(self):
        vehicles_dic = self.DAO.get_vehicle_dic()
        # Go through variables k (vehicles), i,j (nodes)
        for k in self.vehicles:
            for i, j in self.arcs:
                # If there is a path from i to j by vehicle k
                if self.rides[k, i, j] > 0:
                    # Departure node
                    dep_node = self.DAO.get_nodes_dic()[i]
                    arr_node = self.DAO.get_nodes_dic()[j]
                    
                    # Current vehicle
                    vehicle = vehicles_dic[k]

                    # If departure node is a pickup point
                    if isinstance(dep_node, NodePK):
                        dep_node.set_arrival_t(self.arrival_t[k, i])
                        dep_node.set_vehicle(vehicle)
                        for c in vehicles_dic[k].get_capacity().keys():
                            dep_node.get_load()[c] = self.load[c, k, i]
                        dep_node.set_id_next(j)
                        vehicle.add_node(dep_node)
                    
                    # If departure node is a delivery point
                    elif isinstance(dep_node, NodeDL):
                        dep_node.set_arrival_t(self.arrival_t[k, i])
                        dep_node.set_vehicle(vehicle)
                        for c in vehicles_dic[k].get_capacity().keys():
                            dep_node.get_load()[c] = self.load[c, k, i] 
                        dep_node.set_id_next(j)
                        vehicle.add_node(dep_node)
                    
                    # If departure node is a starting point
                    elif isinstance(dep_node, NodeDepot):
                        start_node = Node.copy_node(dep_node)
                        start_node.set_arrival_t(self.arrival_t[k, i])
                        start_node.set_vehicle(vehicle)
                        for c in vehicles_dic[k].get_capacity().keys():
                            dep_node.get_load()[c] = self.load[c, k, i]
                        start_node.set_id_next(j)
                        vehicle.add_node(start_node)
                    
                    # If departure node is a starting point
                    if isinstance(arr_node, NodeDepot):
                        end_node = Node.copy_node(arr_node)
                        end_node.set_arrival_t(self.arrival_t[k, j])
                        end_node.set_vehicle(vehicle)
                        #start_node.set_id_next("*")
                        vehicle.add_node(end_node)

        # Print data in vehicles
        print('################### VEHICLE DATA #####################')
        for v in vehicles_dic:
            print(vehicles_dic[v])