from Coordinate import Coordinate
from Node import *
import time

class Request(object):

    def __init__(self, id, origin, destination, earliest, latest, demand):
        self.id = id
        self.destination = destination
        self.origin = origin
        self.earliest = earliest
        self.latest = latest
        self.demand = demand
        self.travel_t = -1
        self.arrival_t = -1
    
    def get_earliest_tstamp(self):
        return int(time.mktime(self.earliest.timetuple()))
    
    @classmethod
    def factory_request(self, type, id, origin, destination, earliest, latest, demand):
        if type == 'DARP':
            return Request(id, origin, destination, earliest, latest, demand)
        elif type == 'SARP_PL':
            return RequestPL(id, origin, destination, earliest, latest, demand)
    @classmethod
    def factory_request_coord(self,
                              type,
                              id,
                              x_origin,
                              y_origin,
                              x_destination,
                              y_destination,
                              earliest, latest,
                              demand):
        
        if type == 'DARP':
            destination_demand = -demand
            return Request(id,
                           Node.factory_node('PK',
                                             None,
                                             x_origin,
                                             y_origin,
                                             demand),
                           Node.factory_node('DL',
                                             None,
                                             x_destination,
                                             y_destination),
                           earliest,
                           latest,
                           demand)
        elif type == 'SARP_PL':
            # Invert the demand for destination nodes, ex.: from(p1:1, p2:2) and to(p1:-1, p2:-2)
            destination_demand = {id:-demand[id] for id in demand.keys()}

            return RequestPL(id,
                             Node.factory_node('PK',
                                               None,
                                               x_origin,
                                               y_origin,
                                               demand),
                             Node.factory_node('DL',
                                               None,
                                               x_destination,
                                               y_destination,
                                               destination_demand),
                             earliest,
                             latest,
                             demand)
    
    def get_id(self):
        return self.id

    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_earliest(self):
        return self.earliest
    
    def get_earliest_total(self):
        return self.earliest

    def get_latest(self):
        return self.latest

    def get_demand(self):
        return self.demand
    # Remove demands = 0
    def get_demand_short(self):
        return str({id:int(self.demand[id]) for id in self.demand.keys() if int(self.demand[id])>0})
    
    def set_travel_t(self, travel_t):
        self.travel_t = travel_t
    
    def set_arrival_t(self, arrival_t):
        self.arrival_t = arrival_t
    
    def __repr__(self):
        return '<' + self.id + ', '\
                   + str(self.demand) + ','\
                   + str(self.origin) + ', '\
                   + str(self.destination) + ', '\
                   + str(self.earliest) + ', '\
                   + str(self.latest) + ', '\
                   + str(self.arrival_t)+', '\
                   + str(self.travel_t)+'>'

class RequestPL(Request):
    def __init__(self, id, origin, destination, earliest, latest, demand):
        super().__init__(id, origin, destination, earliest, latest, demand)
    
    def __str__(self):
        return '########' + self.id + '########\n'\
               + str(self.origin) + '\n'\
               + str(self.destination) + '\n '\
               + 'Earliest: '\
               + str(self.earliest) + '\n '\
               + 'Latest: '\
               + str(self.latest) + '\n '\
               + 'Arrival t.: '\
               + str(self.arrival_t)+ '\n '\
               + 'Travel d.: '\
               + str(self.travel_t)
    
    def __repr__(self):
         return '########' + self.id + '########\n'\
               + str(self.origin) + '\n'\
               + str(self.destination) + '\n '\
               + 'Earliest: '\
               + str(self.earliest) + '\n '\
               + 'Latest: '\
               + str(self.latest) + '\n '\
               + 'Arrival t.: '\
               + str(self.arrival_t)+ '\n '\
               + 'Travel d.: '\
               + str(self.travel_t)