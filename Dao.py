from Request import Request
from Vehicle import Vehicle
from Coordinate import Coordinate
from Node import *
import pprint
import copy
import urllib.request
import json
import csv
import time
from datetime import datetime, date, time, timedelta




class Dao(object):

    MAX_TRIP_SIZE = 10000

    @classmethod
    def DaoBasicTest(self):

        self.nodes_dic = {}
        # start and end depots
        self.start_depot = Node.factory_node('DP', None, 5, 2, None)
        self.end_depot = Node.factory_node('DP', None, 7, 2, None)

        self.nodes_dic[self.start_depot.get_id()] = self.start_depot
        self.nodes_dic[self.end_depot.get_id()] = self.end_depot

        # self, id, pos, capacity
        self.vehicle_list = [Vehicle.factory_vehicle('DARP', 'AV1', self.start_depot, 4),
                             Vehicle.factory_vehicle(
                                 'DARP', 'AV2', self.start_depot, 2),
                             Vehicle.factory_vehicle(
                                 'DARP', 'AV3', self.start_depot, 2),
                             Vehicle.factory_vehicle('DARP', 'AV4', self.start_depot, 2)]

        self.vehicle_dic = {v.get_id(): v for v in self.vehicle_list}

        # id, origin, destination, earliest, latest, demand
        self.request_list = [Request('$H_1$', Node.factory_node('PK', None, 7, 5, None),
                                     Node.factory_node('DL', None, 3.77, 0.20, None), 100, 100, 1),
                             Request('$H_2$', Node.factory_node('PK', None, 9, 0.5, None),
                                     Node.factory_node('DL', None, 7.38, 7, None), 100, 100, 1),
                             Request('$H_3$', Node.factory_node('PK', None, 10, 4, None),
                                     Node.factory_node('DL', None, 5, 4, None), 30, 30, 1),
                             Request('$H_4$', Node.factory_node('PK', None, 5, 5.85, None),
                                     Node.factory_node('DL', None, 3, 3, None), 200, 200, 1),
                             Request('$H_5$', Node.factory_node('PK', None, 2, 8, None),
                                     Node.factory_node('DL', None, 2.00, 1.91, None), 400, 400, 1)]

        for r in self.request_list:
            self.nodes_dic[r.get_origin().get_id()] = r.get_origin()
            self.nodes_dic[r.get_destination().get_id()
                           ] = r.get_destination()

        self.request_dic = {
            r.get_origin().get_id(): r for r in self.request_list}

        print("REQUEST DICTIONARY")
        print(self.request_dic)

        # Number of passengers picked-up or delivered:
        # pk = load and dl = -load
        # se (start/end) = 0
        self.pk_load = {p.get_origin().get_id(): p.get_demand()
                        for p in self.request_list}
        self.dl_load = {p.get_destination().get_id(): -p.get_demand()
                        for p in self.request_list}
        self.se_load = {self.start_depot.get_id(): 0,
                        self.end_depot.get_id(): 0}

        # Nodes pickup and delivery demands
        self.pk_dl = dict(list(self.pk_load.items()) +
                          list(self.dl_load.items()) +
                          list(self.se_load.items()))

        duration_pk_dl = 10
        duration_service = 0

        self.service_t = {key: duration_pk_dl
                          for key in self.nodes_dic.keys()
                          if key in self.pk_load.keys()
                          or key in self.dl_load.keys()}

        self.service_t[self.start_depot.get_id()] = 0
        self.service_t[self.end_depot.get_id()] = 0

        # Define earliest latest times to attend request
        self.earliest_t = {p.get_origin().get_id(): p.get_earliest()
                           for p in self.request_list}

        # Set of pick-up points (human)
        self.pk_points_list = [p.get_origin().get_id()
                               for p in self.request_list]

        # Set of drop-off points (human)
        self.dl_points_list = [p.get_destination().get_id()
                               for p in self.request_list]

        # List of pk and dp points
        self.pd_nodes = []
        self.pd_nodes.extend(self.pk_points_list)
        self.pd_nodes.extend(self.dl_points_list)

        # List of pickup/delivery tuples from requests
        self.pd_tuples = [(p.get_origin().get_id(), p.get_destination(
        ).get_id()) for p in self.request_list]

        # Dictionary of pickup/delivery tuples from requests
        self.pd_pairs = {p.get_origin().get_id(): p.get_destination().get_id()
                         for p in self.request_list}

        self.T = {k.get_id(): Dao.MAX_TRIP_SIZE for k in self.vehicle_list}

        # Max load per vehicle dictionary
        self.capacity_vehicles = {k.get_id(): k.get_capacity()
                                  for k in self.vehicle_list}
        return Dao()

    def get_distance_matrix(self):
        return self.distance_matrix

    def get_capacity_vehicles(self):
        return self.capacity_vehicles

    def get_earliest_t_dic(self):
        return self.earliest_t
    
    def get_earliest_tstamp_dic(self):
        return self.earliest_tstamp

    def get_pk_points_list(self):
        return self.pk_points_list

    def get_dl_points_list(self):
        return self.dl_points_list

    def get_pd_nodes_list(self):
        return self.pd_nodes

    def get_request_dic(self):
        return self.request_dic

    def get_pd_tuples(self):
        return self.pd_tuples

    def get_pd_pairs(self):
        return self.pd_pairs

    def get_start_point(self):
        return self.start_depot

    def get_service_t(self):
        return self.service_t

    def get_vehicle_dic(self):
        return self.vehicle_dic

    def get_pk_dl(self):
        return self.pk_dl

    def get_end_depot(self):
        return self.end_depot

    def get_vehicle_list(self):
        return self.vehicle_list

    def get_request_list(self):
        return self.request_list

    def get_vehicle_list(self):
        return self.vehicle_list

    def get_nodes_dic(self):
        return self.nodes_dic

    def __init__(self):
        print("START POINT:" + str(self.start_depot))
        print("END POINT:" + str(self.end_depot))
        print("REQUESTS:")
        pprint.pprint(self.request_list)

        self.request_map = {(r.get_origin().get_id(), r.get_destination(
        ).get_id()): r for r in self.request_list}

        print("REQUEST MAP")
        print(self.request_map)

        # Origin dictionary: origin:request
        self.origin_dic = {r.get_origin().get_id(): r
                           for r in self.request_list}

        # Destination dictionary: destination:request
        self.destination_dic = {r.get_destination().get_id(): r
                                for r in self.request_list}

        # Graph NxN - Remove self connections and arcs arriving in end depot
        self.graph = {p1: [p2 for p2 in self.nodes_dic.keys()
                           if p1 != p2
                           and p2 != self.start_depot.get_id()]
                      for p1 in self.nodes_dic.keys()
                      if p1 != self.end_depot.get_id()}

        # There are no arcs departing from the end depot
        self.graph[self.end_depot.get_id()] = []

        print("GRAPH")
        print(self.request_map)

        """
        self.distance_matrix = ({(p1, p2): int(self.nodes_dic[p1].get_coord()
                                               .get_manhattan_dist(
            self.nodes_dic[p2]
            .get_coord()))
            for p1 in self.graph.keys()
            for p2 in self.graph[p1]})
        """

        self.distance_matrix = ({(p1, p2): int(self.nodes_dic[p1].get_coord()
                                               .get_distance_online(
            self.nodes_dic[p2]
            .get_coord()))
            for p1 in self.graph.keys()
            for p2 in self.graph[p1]})

    def copy(self):
        return copy.deepcopy(self)

    def get_graph(self):
        return self.graph




class DaoSARPPL(Dao):
    def __init__(self):
        
        self.nodes_dic = {}
        # start and end depots
        self.start_depot = Node.factory_node(
            'DP', None, 5, 2, {'p1': 0, 'p2': 0, 'p3': 0, 'p4': 0, 's1': 0, 's2': 0, 's3': 0})
        self.end_depot = Node.factory_node(
            'DP', None, 7, 2, {'p1': 0, 'p2': 0, 'p3': 0, 'p4': 0, 's1': 0, 's2': 0, 's3': 0})

        self.nodes_dic[self.start_depot.get_id()] = self.start_depot
        self.nodes_dic[self.end_depot.get_id()] = self.end_depot

        # self, id, pos, capacity
        self.vehicle_list = [Vehicle.
                             factory_vehicle('SARP_PL',
                                             'AV1',
                                             self.start_depot,
                                             {'p1': 4,
                                              'p2': 4,
                                              'p3': 4,
                                              'p4': 4,
                                              's1': 4,
                                              's2': 4,
                                              's3': 4}),
                             Vehicle.
                             factory_vehicle('SARP_PL',
                                             'AV2',
                                             self.start_depot,
                                             {'p1': 4,
                                              'p2': 4,
                                              'p3': 4,
                                              'p4': 4,
                                              's1': 4,
                                              's2': 4,
                                              's3': 4}),
                             Vehicle.
                             factory_vehicle('SARP_PL',
                                             'AV3',
                                             self.start_depot,
                                             {'p1': 4,
                                              'p2': 4,
                                              'p3': 4, 
                                              'p4': 4, 
                                              's1': 4, 
                                              's2': 4, 
                                              's3': 4}),
                             Vehicle.
                             factory_vehicle('SARP_PL',
                                             'AV4',
                                             self.start_depot,
                                             {'p1': 4,
                                              'p2': 4,
                                              'p3': 4, 
                                              'p4': 4, 
                                              's1': 4, 
                                              's2': 4, 
                                              's3': 4})]

        self.vehicle_dic = {v.get_id(): v for v in self.vehicle_list}

        # id, origin, destination, earliest, latest, demand
        self.request_list = [Request.factory_request_coord('SARP_PL', '$H_1$', 7, 5, 3.77, 0.20, 100, 100, {'p1': 1}),
                             Request.factory_request_coord(
                                 'SARP_PL', '$H_2$', 9, 0.5, 7.38, 7, 100, 100, {'p2': 1}),
                             Request.factory_request_coord(
                                 'SARP_PL', '$H_3$', 10, 4, 5, 4, 30, 30, {'s1': 2, 's2': 1}),
                             Request.factory_request_coord(
                                 'SARP_PL', '$H_4$', 5, 5.85, 3, 3, 200, 200, {'s3': 1}),
                             Request.factory_request_coord('SARP_PL', '$H_5$', 2, 8, 2.00, 1.91, 400, 400, {'s1': 4})]

        self.price_parcel_locker = {
            'p1': 40, 'p2': 30, 'p3': 20, 'p4': 10, 's1': 10, 's2': 15, 's3': 20}

        print("Demand of requests")
        for r in self.request_list:
            pprint.pprint(r.get_demand())

        print('Parcel locker:')
        pprint.pprint(self.price_parcel_locker.keys())

        print("Req. list")
        # Insert nodes information in dictionary
        for r in self.request_list:
            self.nodes_dic[r.get_origin().get_id()] = r.get_origin()
            self.nodes_dic[r.get_destination().get_id()] = r.get_destination()

        # The compartments not declared in the request have zero demand
        for n in self.nodes_dic.keys():
            for c in self.price_parcel_locker.keys():
                if c not in self.nodes_dic[n].get_demand().keys():
                    self.nodes_dic[n].get_demand()[c] = 0

        print("Demand of nodes")
        for n in self.nodes_dic.keys():
            print(self.nodes_dic[n].get_id())
            pprint.pprint(self.nodes_dic[n].get_demand())
        

        self.request_dic = {
            r.get_origin().get_id(): r for r in self.request_list}

        print("REQUEST DICTIONARY")
        print(self.request_dic)

        # Number of passengers picked-up or delivered:
        # pk = load and dl = -load
        # se (start/end) = 0
        # Nodes pickup and delivery demands
        self.pk_dl = {(p,  c): self.nodes_dic[p].get_demand()[c]
                        for p in self.nodes_dic.keys()
                        for c in self.nodes_dic[p].get_demand().keys()}


        
        print("Pick-up delivery dictionary:")
        for d in self.pk_dl:
            print(d)
        duration_pk_dl = 6000
        duration_service = 0

        self.service_t = {key: duration_pk_dl for key in self.nodes_dic}

        self.service_t[self.start_depot.get_id()] = 0
        self.service_t[self.end_depot.get_id()] = 0

        # Define earliest latest times to attend request
        self.earliest_t = {p.get_origin().get_id(): p.get_earliest()
                           for p in self.request_list}

        # Define earliest latest times to attend request
        self.earliest_tstamp = {p.get_origin().get_id(): p.get_earliest_tstamp()
                                  for p in self.request_list}

        # Set of pick-up points (human)
        self.pk_points_list = [p.get_origin().get_id()
                               for p in self.request_list]

        # Set of drop-off points (human)
        self.dl_points_list = [p.get_destination().get_id()
                               for p in self.request_list]

        # List of pk and dp points
        self.pd_nodes = []
        self.pd_nodes.extend(self.pk_points_list)
        self.pd_nodes.extend(self.dl_points_list)

        # List of pickup/delivery tuples from requests
        self.pd_tuples = [(p.get_origin().get_id(), p.get_destination(
        ).get_id()) for p in self.request_list]

        # Dictionary of pickup/delivery tuples from requests
        self.pd_pairs = {p.get_origin().get_id(): p.get_destination().get_id()
                         for p in self.request_list}

        self.T = {k.get_id(): Dao.MAX_TRIP_SIZE for k in self.vehicle_list}

        # Max load per vehicle dictionary

        self.capacity_vehicles = {(k.get_id(), c): k.get_capacity()[c]
                                  for k in self.vehicle_list
                                  for c in k.get_capacity()}
        super().__init__()
    
    def get_price_parcel_locker(self):
        return self.price_parcel_locker

class DaoSARP_NYC(Dao):

    # Read requests from file
    def get_requests_from(self, csv_trips):
        # List of requests
        request_list = []
        
        # Try opening csv file
        with open(csv_trips) as f:
            reader = csv.reader(f)
            header = next(reader)
        
            # Id customer according to number of rows
            id_customer = 0
            
            # For each data row
            for row in reader:
                id_customer+=1
                # Revealing instant
                revealing = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
                # Pickup latitude
                pickup_x = float(row[1])
                # Pickup longitude
                pickup_y = float(row[2])
                # Dropoff latitude
                dropoff_x = float(row[3])
                # Dropoff longitude
                dropoff_y = float(row[4])
                # Order configuration as dictionary, e.g. A=2/C=1 => {'A':2, 'C':1}
                order = {o.split('=')[0]:int(o.split('=')[1]) for o in row[5].split('/')}

                # Create request for data row
                req = Request.factory_request_coord('SARP_PL',
                                                    'H_'+str(id_customer),
                                                    pickup_x,
                                                    pickup_y,
                                                    dropoff_x,
                                                    dropoff_y,
                                                    revealing,
                                                    10000,
                                                    order)
                
                # Append request into list of requests
                request_list.append(req)
        return request_list
    
    # Read requests from file
    def get_requests_from(self, csv_trips):
        # List of requests
        request_list = []
        
        # Try opening csv file
        with open(csv_trips) as f:
            reader = csv.reader(f)
            header = next(reader)
        
            # Id customer according to number of rows
            id_customer = 0
            
            # For each data row
            for row in reader:
                id_customer+=1
                # Revealing instant
                revealing = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
                # Pickup latitude
                pickup_x = float(row[1])
                # Pickup longitude
                pickup_y = float(row[2])
                # Dropoff latitude
                dropoff_x = float(row[3])
                # Dropoff longitude
                dropoff_y = float(row[4])
                # Order configuration as dictionary, e.g. A=2/C=1 => {'A':2, 'C':1}
                order = {o.split('=')[0]:int(o.split('=')[1]) for o in row[5].split('/')}

                # Create request for data row
                req = Request.factory_request_coord('SARP_PL',
                                                    'H_'+str(id_customer),
                                                    pickup_x,
                                                    pickup_y,
                                                    dropoff_x,
                                                    dropoff_y,
                                                    revealing,
                                                    100,
                                                    order)
                
                # Append request into list of requests
                request_list.append(req)
        return request_list

    # Read vehicles from file
    def get_vehicles_from(self, csv_vehicles):
        # List of requests
        request_list = []
        vehicle_list = []
        # Try opening csv file
        with open(csv_vehicles) as f:
            reader = csv.reader(f)
            # Get the first row with headers
            header = next(reader)
            # Get the label of the sizes
            # ex.: ['XS', 'S', 'M', 'L', 'XL', 'A', 'C', 'B', 'I']
            sizes = header[2:len(header)]
            # Id customer according to number of rows
            id_customer = 0
            # For each data row
            for row in reader:
                id_customer+=1
                # Model of vehicle
                model = row[0]
                # Amount of vehicles
                amount = int(row[1])
                # Array of capacities in vehicle
                capacities = row[2:len(row)]
                # Dictionary of capacities
                dic_capacities = {sizes[i]:int(amount)
                                  for i, amount in enumerate(capacities)}
                # Create 'amount' vehicles
                for v in range(0,amount):
                    veh = Vehicle.factory_vehicle('SARP_PL',
                                                  'AV' + model + '_' + str(v),
                                                  self.start_depot,
                                                  dic_capacities)
                    
                    # Add vehicle in list
                    vehicle_list.append(veh)
        return vehicle_list

    def __init__(self):
        self.MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiYnJlbm9iZWlyaWdvIiwiYSI6ImNpeHJiMDNidTAwMm0zNHFpcXVzd2UycHgifQ.tWIDAiRhjSzp1Bd40rxaHw"

        csv_trips = 'trips10.csv'

        self.nodes_dic = {}
        # start and end depots
        # 2010-09-13 12:41,-73.961624,40.774368,-73.954681,40.778942,XL=1
        # 2010-09-13 12:35,-73.970974,40.779803,-73.962158,40.773075,A=1/C=1
        
        self.start_depot = Node.factory_node(
            'DP', None, -73.970974,40.785534, {'XS': 0, 'S': 0, 'M': 0, 'L': 0, 'XL': 0, 'A': 0, 'C': 0, 'B': 0, 'I':0})
        self.end_depot = Node.factory_node(
            'DP', None, -73.954681,40.785534, {'XS': 0, 'S': 0, 'M': 0, 'L': 0, 'XL': 0, 'A': 0, 'C': 0, 'B': 0, 'I':0})
        
        self.nodes_dic[self.start_depot.get_id()] = self.start_depot
        self.nodes_dic[self.end_depot.get_id()] = self.end_depot

        # Load requests from file
        self.request_list =  self.get_requests_from("trips10.csv")
        
        # self, id, pos, capacity
        self.vehicle_list = self.get_vehicles_from("vehicles10.csv")
        
        # Request list
        print("Request list")
        pprint.pprint(self.request_list)
        
        # Vehicle list
        print("Vehicle list")
        pprint.pprint(self.vehicle_list)

        self.vehicle_dic = {v.get_id(): v for v in self.vehicle_list}

        self.price_parcel_locker = {'XS': 2, 'S': 2, 'M': 2, 'L': 2, 'XL': 2, 'A': 1, 'C': 1, 'B': 1, 'I':1}

        print("Demand of requests")
        for r in self.request_list:
            pprint.pprint(r.get_demand())

        print('Parcel locker:')
        pprint.pprint(self.price_parcel_locker.keys())

        print("Req. list")
        # Insert nodes information in dictionary
        for r in self.request_list:
            self.nodes_dic[r.get_origin().get_id()] = r.get_origin()
            self.nodes_dic[r.get_destination().get_id()] = r.get_destination()

        # The compartments not declared in the request have zero demand
        for n in self.nodes_dic.keys():
            for c in self.price_parcel_locker.keys():
                if c not in self.nodes_dic[n].get_demand().keys():
                    self.nodes_dic[n].get_demand()[c] = 0

        print("Demand of nodes")
        for n in self.nodes_dic.keys():
            print(self.nodes_dic[n].get_id())
            pprint.pprint(self.nodes_dic[n].get_demand())
        

        self.request_dic = {
            r.get_origin().get_id(): r for r in self.request_list}

        print("REQUEST DICTIONARY")
        print(self.request_dic)

        # Number of passengers picked-up or delivered:
        # pk = load and dl = -load
        # se (start/end) = 0
        # Nodes pickup and delivery demands
        self.pk_dl = {(p,  c): self.nodes_dic[p].get_demand()[c]
                        for p in self.nodes_dic.keys()
                        for c in self.nodes_dic[p].get_demand().keys()}


        
        print("Pick-up delivery dictionary:")
        for d in self.pk_dl:
            print(str(d)+":"+str(self.pk_dl[d]))
        duration_pk_dl = 10
        duration_service = 0

        self.service_t = {key: duration_pk_dl for key in self.nodes_dic}

        self.service_t[self.start_depot.get_id()] = 0
        self.service_t[self.end_depot.get_id()] = 0

        # Define earliest latest times to attend request
        self.earliest_t = {p.get_origin().get_id(): p.get_earliest()
                           for p in self.request_list}

        # Define earliest latest times to attend request
        self.earliest_tstamp = {p.get_origin().get_id(): p.get_earliest_tstamp()
                                  for p in self.request_list}

        # Set of pick-up points (human)
        self.pk_points_list = [p.get_origin().get_id()
                               for p in self.request_list]

        # Set of drop-off points (human)
        self.dl_points_list = [p.get_destination().get_id()
                               for p in self.request_list]

        # List of pk and dp points
        self.pd_nodes = []
        self.pd_nodes.extend(self.pk_points_list)
        self.pd_nodes.extend(self.dl_points_list)

        # List of pickup/delivery tuples from requests
        self.pd_tuples = [(p.get_origin().get_id(), p.get_destination(
        ).get_id()) for p in self.request_list]

        # Dictionary of pickup/delivery tuples from requests
        self.pd_pairs = {p.get_origin().get_id(): p.get_destination().get_id()
                         for p in self.request_list}

        self.T = {k.get_id(): Dao.MAX_TRIP_SIZE for k in self.vehicle_list}

        # Max load per vehicle dictionary

        self.capacity_vehicles = {(k.get_id(), c): k.get_capacity()[c]
                                  for k in self.vehicle_list
                                  for c in k.get_capacity()}
        super().__init__()
    
    def get_price_parcel_locker(self):
        return self.price_parcel_locker
