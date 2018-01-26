from Node import *
from gurobipy import *
import pprint
from Response import *
from Dao import Dao
import matplotlib.pyplot as plt
from datetime import *


class OptMethod(object):

    def __init__(self, DAO):

        self.response = None
        print("INIT OPTMETHOD")
        # Create copy of DAO
        self.DAO = DAO.copy()
        # pprint.pprint(DAO.get_price_parcel_locker())

        self.graph = self.DAO.get_graph()

        # pprint.pprint(self.graph)
        self.requests = self.DAO.get_request_list()
        self.request_dic = self.DAO.get_request_dic()

        self.dist_matrix = self.DAO.get_distance_matrix()

        # All points involving the orders
        self.coord = self.DAO.get_nodes_dic()

        # Define passenger self.requests (order_reveling_time, (start_tw, end_tw),
        # origin, destination, [('type_of_seat', amount),...])

        # Start and end av location
        self.start_depot = self.DAO.get_start_point().get_id()
        self.end_depot = self.DAO.get_end_depot().get_id()

        # List of self.vehicles ids
        self.vehicles = [k.get_id() for k in self.DAO.get_vehicle_list()]
        print('self.vehicles')
        print(self.vehicles)

        self.nodes = list(self.coord.keys())
        print(self.nodes)

        # Set of arcs and list of all arcs and times arcs = [( p9 , p6 ), ( p1  ,
        # p2  ), ...] and times = {('p9', 'p6'): 4.2, ('p1', 'p2'): 5.7, ...}
        self.arcs, self.times = multidict({(p1, p2): self.dist_matrix[p1, p2]
                                           for p1 in self.graph.keys()
                                           for p2 in self.graph[p1]})

        # There is no self.cost to go from start to end depot
        self.times[self.start_depot, self.end_depot] = 0
        
        print('ARCS:')
        print(self.arcs)
        
        print('TIMES:')
        pprint.pprint(self.times)


        self.cost = {(k, p1, p2): self.dist_matrix[p1, p2]
                     for k in self.vehicles
                     for p1, p2 in self.arcs}

        print('COST:')
        pprint.pprint(self.cost)

        # Define earliest latest self.times to attend request
        self.earliest_t = self.DAO.get_earliest_t_dic()

        # Define earliest latest self.times to attend request
        self.earliest_tstamp = self.DAO.get_earliest_tstamp_dic()

        # Set of pick-up points (human)
        self.pk_points = self.DAO.get_pk_points_list()

        # Set of drop-off points (human)
        self.dl_points_list = self.DAO.get_dl_points_list()

        # List of pk and dp points
        self.pd_nodes = self.DAO.get_pd_nodes_list()

        # List of pickup/delivery tuples from self.requests
        self.pd_tuples = self.DAO.get_pd_tuples()

        # Dictionary of pickup/delivery tuples from self.requests
        self.pd_pairs = self.DAO.get_pd_pairs()

        # Each vehicle k ∈ K has a capacity Qk
        self.capacity_vehicle = self.DAO.get_capacity_vehicles()

        # self.nodes pickup and delivery demands
        self.pk_dl = self.DAO.get_pk_dl()

        print("Pickup delivery")
        pprint.pprint(self.pk_dl)

        # self.nodes service duration
        self.service_t = self.DAO.get_service_t()

    def __str__(self):
        str = '################### PRINT ####################################'
        str += "\n\n##### REQUESTS\n"
        str += pprint.pformat(self.pd_tuples, 4)

        str += "\n\n##### PD NODES\n"
        str += pprint.pformat(self.pd_nodes, 4, 4)

        str += "\n\n##### PICKUPS AND DELIVERIES AT EACH POINT P:\n"
        filter_pk_dl = {}
        for i in self.pk_dl.keys():
            if self.pk_dl[i] != 0:
                filter_pk_dl[i] = pk_dl[i]

        str += pprint.pformat(self.pk_dl, 4)

        str += "\n\n##### SERVICE DURATION AT EACH POINT P:\n"
        str += pprint.pformat(self.service_t, 4)

        str += "\n\n##### EARLIEST:\n"
        str += pprint.pformat(self.earliest_t, 4, 4)

        str += "\n\n##### VEHICLE CAPACITY:\n"
        str += pprint.pformat(self.capacity_vehicle, 4)

        return str

    ##########################################################################
    ########################### PLOTTING WITH MATPLOTLIB #####################
    ##########################################################################
    # 1 - Get a scatter plot from coordinates
    def create_scatter_plot(self):
        nodes_dic = self.DAO.get_nodes_dic()
        # Create list of x coordinates
        x_coord = [nodes_dic[key].get_coord().get_x()*1000000
                   for key in nodes_dic.keys()]
        print(x_coord)

        # Create list of y coordinates
        y_coord = [nodes_dic[key].get_coord().get_y()*1000000
                   for key in nodes_dic.keys()]
        print(y_coord)

        # Create scatter distribution on plt (import from matplotlib)
        plt.scatter(x_coord, y_coord)

        return plt

    # 2 - Receive p1, data(p2, arrival_t, load, travel_t) and creates
    # annotations with this information next to the node
    def create_node_info(self):
        # print(self.DAO.get_nodes_dic())
        nodes = self.DAO.get_nodes_dic()
        for n_id in nodes.keys():
            n = nodes[n_id]

            # print(n+":"+str(nodes[n]))

            arrival = n.get_arrival_t()
            load = n.get_load_0()
            tt = 0
            an = ''

            # If travel time is empty => print arrival node
            if isinstance(n, NodeDL):
                arri = datetime.fromtimestamp(arrival).strftime('%H:%M')
                an = 'AR:' + str(arri) + "\nLOAD:" + str(load)

            # If travel time is NOT empty => print departure node
            elif isinstance(n, NodePK):

                # Max travel time of request p1
                max_tt = str(
                    self.dist_matrix[n.get_id(), n.get_id_next()] + self.MAX_LATENESS)

                # Earliest time / Arrival time
                # Load to be picked up in departure node
                # Total travel time of request / Max. travel time allowed
                print(self.earliest_t[n.get_id()])
                arri = datetime.fromtimestamp(arrival).strftime('%H:%M')
                ear = self.earliest_t[n.get_id()].strftime('%H:%M')
                an = 'ARRIVAL:' + str(ear) + '/' + str(arri)\
                    + '\nLOAD:' + str(load)\
                    #+ '\nTT:' + str(tt) + '/' + max_tt

            # Create annotation to show node info
            plt.annotate(an,
                         (n.get_coord().get_x()*1000000, n.get_coord().get_y()*1000000),
                         xytext=(25, -25),
                         textcoords='offset points',
                         ha='left',
                         va='bottom',
                         fontsize=10,
                         bbox=dict(boxstyle='round4,pad=0.1',
                                   fc='white',
                                   color='white',
                                   alpha=50))

    # 3 - Create nodes with text inside above each point
    def create_nodes(self):

        nodes_dic = self.DAO.get_nodes_dic()

        plt, self.DAO.get_nodes_dic()
        for p in nodes_dic.keys():
            plt.annotate("$"+nodes_dic[p].get_id()[0:2]+"_"+nodes_dic[p].get_id()[2:]+"$",
                         (nodes_dic[p].get_coord().get_x()*1000000,
                          nodes_dic[p].get_coord().get_y()*1000000),
                         xytext=(0, 0),
                         textcoords='offset points',
                         ha='center',
                         va='bottom',
                         fontsize=18,
                         bbox=dict(boxstyle='circle, pad=0.3',
                                   fc='white',
                                   alpha=1))

    # 4 - Draw vehicle arrows
    def create_arrows(self):
        vehicle_dic = self.DAO.get_vehicle_dic()
        for k in vehicle_dic.keys():
            veh = vehicle_dic[k]
            p1 = veh.get_pos().get_id()
            path = veh.get_path()
            p2 = path[p1].get_id_next()
            while p1 in path.keys() and p2 != None:
                # From/to coordinates
                p1_coord = path[p1].get_coord()
                p2_coord = path[p2].get_coord()

                # x, y coordinates From/to
                p1_x = p1_coord.get_x()*1000000
                p1_y = p1_coord.get_y()*1000000
                p2_x = p2_coord.get_x()*1000000
                p2_y = p2_coord.get_y()*1000000

                plt.arrow(p1_x,
                          p1_y,
                          p2_x - p1_x,
                          p2_y - p1_y,
                          head_width=0.01,
                          head_length=0.1,
                          fc='k',
                          ec=veh.get_color())

                # Get middle point of an arrow
                middle_p = Coordinate.get_middle_point(p1_coord, p2_coord)
                """
                # Annotate the distance between points
                x_ij = '$X_{' + p1[1:] + ',' + p2[1:] + '}'
                plt.annotate(str(x_ij + '(' + str(round(self.DAO.get_distance_matrix()[p1, p2]/60,2))+ ')$'),
                             (middle_p.get_x()*1000000, middle_p.get_y()*1000000),
                             xytext=(0, 0),
                             textcoords='offset points',
                             ha='center',
                             va='bottom',
                             fontsize='10',
                             bbox=dict(boxstyle='round4,pad=0.1',
                                       color='white',
                                       fc='white',
                                       alpha=1))
                """
                p1 = p2
                p2 = path[p1].get_id_next()

    # 5 - Draw requests annotation
    def create_requests(self):
        requests = self.DAO.get_request_list()
        for h in requests:
            p1 = h.get_origin()
            p1_coord = p1.get_coord()
            p2 = h.get_destination()
            p2_coord = p2.get_coord()

            id_origin = p1.get_id()
            id_destination = p2.get_id()

            # Pickup
            plt.annotate("$"+str(h.get_id())+"$" + '(' + str(h.get_demand_short()) + ')',
                         (p1_coord.get_x()*1000000, p1_coord.get_y()*1000000),
                         xytext=(0, 30),
                         textcoords='offset points',
                         ha='center',
                         va='bottom',
                         bbox=dict(boxstyle='round,pad=0.5',
                                   fc='#b2ffb6',
                                   alpha=1))

            # Dropoff
            plt.annotate("$"+str(h.get_id())+"$" + '(' + str(h.get_demand_short()) + ')',
                         (p2_coord.get_x()*1000000,
                          p2_coord.get_y()*1000000),
                         xytext=(0, 30),
                         textcoords='offset points',
                         ha='center',
                         va='bottom',
                         bbox=dict(boxstyle='round4,pad=0.5',
                                   fc='#ffae93',
                                   alpha=1))

    # Plot the result of method
    def plot_result(self):
        if self.response is not None:
            # Create scatter plot in plt from matplotlib
            self.create_scatter_plot()

            # Draw nodes
            self.create_nodes()

            # Draw arrows
            self.create_arrows()

            # Draw requests
            self.create_requests()

            self.create_node_info()
            # Show graph
            plt.axis('off')
            plt.show()
        else:
            print('PLOT IMPOSSIBLE - MODEL IS UNFEASIBLE')

    ##########################################################################
    ##########################################################################
    ##########################################################################


class DARP(OptMethod):

    def __init__(self, DAO, MAX_LATENESS, MAX_PICKUP_LATENESS, MAX_STEPS):
        self.MAX_LATENESS = MAX_LATENESS
        self.MAX_PICKUP_LATENESS = MAX_PICKUP_LATENESS
        self.MAX_STEPS = MAX_STEPS
        super().__init__(DAO)
        self.start()

    ##########################################################################
    ########################### MILP DARP (DIAL-A-RIDE) ######################
    ##########################################################################
    def start(self):
        try:
            # Big M for model linearization
            M = 10000000

            # Create a new model
            m = Model("DARP")

            #### VARIABLES ####################################################

            # Binary variable, 1 if a vehicle k goes from node i to node j
            ride = m.addVars(self.vehicles, self.arcs,
                             obj=self.cost, vtype=GRB.BINARY, name="x")

            # Arrival time of vehicle k at node i
            arrival_t = m.addVars(self.vehicles, self.nodes,
                                  vtype=GRB.INTEGER, name="u")

            # Load of vehicle k at pickup node i
            load = m.addVars(self.vehicles, self.nodes,
                             vtype=GRB.INTEGER, name="w")

            # Ride time of request i served by vehicle k
            travel_t = m.addVars(
                self.vehicles, self.pk_points, vtype=GRB.INTEGER, name="r")

            #### ROUTING CONSTRAINTS ##########################################

            # (ONLY_PK) = There is only one vehicle leaving a pickup point
            #             to reach only one delivery point
            m.addConstrs((ride.sum('*', i, '*') == 1
                          for i in self.pk_points), "PK")

            # (BEGIN) = Every vehicle leaves the start depot
            m.addConstrs((ride.sum(k, self.start_depot, '*') == 1
                          for k in self.vehicles), "BEGIN")

            # (END) = Every vehicle goes to the end depot
            m.addConstrs((ride.sum(k, '*', self.end_depot) == 1
                          for k in self.vehicles), "END")

            # (OUT_OUT) = If a vehicle leaves a pickup node it also leaves
            #             the corresponding delivery node
            m.addConstrs((ride.sum(k, i, '*') ==
                          ride.sum(k, j, '*')
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "OUT_OUT")

            # (IN_OUT) = self.vehicles enter and leave pk/dl self.nodes
            m.addConstrs((ride.sum(k, '*', i) ==
                          ride.sum(k, i, '*')
                          for k in self.vehicles
                          for i in self.pd_nodes), "IN_OUT")

            # (ARRI_T) = Arrival time at location j (departing from i) >=
            #            arrival time in i +
            #            service time in i +
            #            time to go from i to j
            #            IF there is a ride from i to j
            m.addConstrs((arrival_t[k, j] >=
                          arrival_t[k, i] +
                          self.service_t[i] +
                          self.times[i, j] -
                          M * (1 - ride[k, i, j])
                          for k in self.vehicles
                          for i, j in self.arcs), "ARRI_T")

            #### RIDE TIME CONSTRAINTS ########################################

            # (RIDE_1) = Ride time from i to j >=
            #            time_from_i_to_j
            m.addConstrs((travel_t[k, i] >= self.times[i, j]
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "RIDE_1")

            # (RIDE_2) = Ride time from i to j <=
            #            time_from_i_to_j + MAX_LATENESS
            m.addConstrs((travel_t[k, f] <=
                          self.times[f, t] + self.MAX_LATENESS
                          for k in self.vehicles
                          for f, t in self.pd_tuples), "RIDE_2")

            # (RIDE_3) = Ride time from i to j is >=
            #            arrival_time_j - (arrival_time_i + self.service_time_i)
            m.addConstrs((travel_t[k, i] >=
                          arrival_t[k, j] -
                          (arrival_t[k, i] + self.service_t[i])
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "RIDE_3")

            ### TIME WINDOW CONSTRAINTS #######################################
            #>>>>>> TIME WINDOW FOR PICKUP
            # (EARL) = Arrival time in i >=
            #          earliest arrival time in i
            m.addConstrs((arrival_t[k, i] >=
                          self.earliest_t[i]
                          for k in self.vehicles
                          for i in self.pk_points), "EARL")

            # (LATE) = Arrival time in i >=
            #          earliest arrival time + MAX_PICKUP_LATENESS
            m.addConstrs((arrival_t[k, i] <=
                          self.earliest_t[i] + self.MAX_PICKUP_LATENESS
                          for k in self.vehicles
                          for i in self.pk_points), "LATE")

            #>>>>>> TIME WINDOW FOR MAX. DURATION OF ROUTE
            # (TAXI) = Maximal duration of route k <= T
            """
            m.addConstrs((arrival_t[k, self.end_depot] -
                        arrival_t[k, self.start_depot] <= T[k]
                        for k in avs_ids),"TAXI")
            """
            #### LOADING CONSTRAINTS ##########################################

            # (LOAD) = Load of vehicle k in node j >=
            #               load of vehicle k in node i +
            #               load collected at j
            #               IF there is a ride from i t j
            m.addConstrs((load[k, j] >=
                          load[k, i] +
                          self.pk_dl[j] -
                          M * (1 - ride[k, i, j])
                          for k in self.vehicles
                          for i, j in self.arcs), "LOAD")

            # (LOAD_MIN) = Load of vehicle k in node i >=
            #              MAX(0, PK/DL demand in i)
            m.addConstrs((load[k, i] >= max(0, self.pk_dl[i])
                          for k in self.vehicles
                          for i in self.nodes), "LOAD_MIN")

            # (LOAD_MAX) = Load of vehicle k in node i >=
            #              MIN(MAX_LOAD, MAX_LOAD - DL demand in i)
            m.addConstrs((load[k, i] <=
                          min(self.capacity_vehicle[k],
                              self.capacity_vehicle[k] + self.pk_dl[i])
                          for k in self.vehicles
                          for i in self.nodes), "LOAD_MAX")

            #### FEASIBILITY CONSTRAINTS ######################################

            m.addConstrs((load[k, i] >= 0
                          for k in self.vehicles
                          for i in self.nodes),  "LOAD_0")
            m.addConstrs((arrival_t[k, i] >= 0
                          for k in self.vehicles
                          for i in self.nodes), "ARRI_0")
            m.addConstrs((load[k, i] == 0
                          for k in self.vehicles
                          for i in [self.start_depot, self.end_depot]), "LOAD_DEPOT_0")

            # obj = sum(ride[k, i, j]*self.cost[k, i, j] for k in avs_ids for i,j in self.arcs)
            # print(obj)
            # m.setObjective(obj, GRB.MINIMIZE)

            #### OPTIMIZE MODEL ###############################################
            m.optimize()

            #### SHOW RESULTS #################################################

            # Get constraints
            # constrs = m.getConstrs()

            # Store route per vehicle
            vehicles_route = {}

            # If status is optimal
            if m.status == GRB.Status.OPTIMAL:

                # Get binary variables Xkij
                var_ride = m.getAttr('x', ride)

                # Get travel self.times of each request
                var_travel_t = m.getAttr('x', travel_t)

                # Get load of vehicle at each point
                var_load = m.getAttr('x', load)

                # Get arrival time at each point
                arrival_t = m.getAttr('x', arrival_t)

                # Create DARP answer
                darp_answer = Response(self.vehicles,
                                       self.arcs,
                                       var_ride,
                                       var_travel_t,
                                       var_load,
                                       arrival_t,
                                       self.DAO)
                # Return anwer
                self.response = darp_answer

        except GurobiError:
            print('Error reported')
    ##########################################################################
    ##########################################################################
    ##########################################################################


class SARP_PL(OptMethod):

    def __init__(self, DAO, MAX_LATENESS, MAX_PICKUP_LATENESS, MAX_STEPS):
        self.MAX_LATENESS = MAX_LATENESS
        self.MAX_PICKUP_LATENESS = MAX_PICKUP_LATENESS
        self.MAX_STEPS = MAX_STEPS
        super().__init__(DAO)
        self.start()

    ##########################################################################
    ########### MILP SARP_PL (SHARE-A-RIDE PROBLEM WITH PARCEL LOCKERS) ######
    ##########################################################################
    def start(self):
        try:
            # Big M for model linearization
            M = 20000000

            # Create a new model
            m = Model("SARP_PL")

            # Types of compartments
            Tc = 5

            print('Parcel locker price:')
            pprint.pprint(self.DAO.get_price_parcel_locker())

            # Array of compartments
            comp = [x for x in self.DAO.get_price_parcel_locker().keys()]

            # Array of loads

            #### VARIABLES ####################################################

            # Binary variable, 1 if a vehicle k goes from node i to node j
            ride = m.addVars(self.vehicles, self.arcs,
                             obj=self.cost, vtype=GRB.BINARY, name="x")

            # Arrival time of vehicle k at node i
            arrival_t = m.addVars(self.vehicles, self.nodes,
                                  vtype=GRB.INTEGER, name="u")

            # Load of compartment c of vehicle k at pickup node i
            load = m.addVars(comp, self.vehicles, self.nodes,
                             vtype=GRB.INTEGER, name="w")

            # Ride time of request i served by vehicle k
            travel_t = m.addVars(
                self.vehicles, self.pk_points, vtype=GRB.INTEGER, name="r")

            #### ROUTING CONSTRAINTS ##########################################

            # (ONLY_PK) = There is only one vehicle leaving a pickup point
            #             to reach only one delivery point
            m.addConstrs((ride.sum('*', i, '*') == 1
                          for i in self.pk_points), "PK")

            # (BEGIN) = Every vehicle leaves the start depot
            m.addConstrs((ride.sum(k, self.start_depot, '*') == 1
                          for k in self.vehicles), "BEGIN")

            # (END) = Every vehicle goes to the end depot
            m.addConstrs((ride.sum(k, '*', self.end_depot) == 1
                          for k in self.vehicles), "END")

            # (OUT_OUT) = If a vehicle leaves a pickup node it also leaves
            #             the corresponding delivery node
            m.addConstrs((ride.sum(k, i, '*') ==
                          ride.sum(k, j, '*')
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "OUT_OUT")

            # (IN_OUT) = self.vehicles enter and leave pk/dl self.nodes
            m.addConstrs((ride.sum(k, '*', i) ==
                          ride.sum(k, i, '*')
                          for k in self.vehicles
                          for i in self.pd_nodes), "IN_OUT")

            # (ARRI_T) = Arrival time at location j (departing from i) >=
            #            arrival time in i +
            #            service time in i +
            #            time to go from i to j
            #            IF there is a ride from i to j
            m.addConstrs((arrival_t[k, j] >=
                          arrival_t[k, i] +
                          self.service_t[i] +
                          self.times[i, j] -
                          M * (1 - ride[k, i, j])
                          for k in self.vehicles
                          for i, j in self.arcs), "ARRI_T")

            #### RIDE TIME CONSTRAINTS ########################################

            # (RIDE_1) = Ride time from i to j >=
            #            time_from_i_to_j
            m.addConstrs((travel_t[k, i] >= self.times[i, j]
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "RIDE_1")

            # (RIDE_2) = Ride time from i to j <=
            #            time_from_i_to_j + MAX_LATENESS
            m.addConstrs((travel_t[k, f] <=
                          self.times[f, t] + self.MAX_LATENESS
                          for k in self.vehicles
                          for f, t in self.pd_tuples), "RIDE_2")

            # (RIDE_3) = Ride time from i to j is >=
            #            arrival_time_j - (arrival_time_i + self.service_time_i)
            m.addConstrs((travel_t[k, i] >=
                          arrival_t[k, j] -
                          (arrival_t[k, i] + self.service_t[i])
                          for k in self.vehicles
                          for i, j in self.pd_tuples), "RIDE_3")

            ### TIME WINDOW CONSTRAINTS #######################################
            #>>>>>> TIME WINDOW FOR PICKUP
            # (EARL) = Arrival time in i >=
            #          earliest arrival time in i
            m.addConstrs((arrival_t[k, i] >= self.earliest_tstamp[i]
                          for k in self.vehicles
                          for i in self.pk_points), "EARL")      

            # (LATE) = Arrival time in i <=
            #          earliest arrival time + MAX_PICKUP_LATENESS
            m.addConstrs((arrival_t[k, i] <=
                          self.earliest_tstamp[i] + self.MAX_PICKUP_LATENESS
                          for k in self.vehicles
                          for i in self.pk_points), "LATE")
            
            #>>>>>> TIME WINDOW FOR MAX. DURATION OF ROUTE
            # (TAXI) = Maximal duration of route k <= T
            """
            m.addConstrs((arrival_t[k, self.end_depot] -
                        arrival_t[k, self.start_depot] <= T[k]
                        for k in avs_ids),"TAXI")
            """
            #### LOADING CONSTRAINTS ##########################################

            # (LOAD) = Load of compartment c of vehicle k in node j >=
            #               load of compartment c of vehicle k in node i +
            #               load collected for compartment c at node j
            #               IF there is a ride of vehicle k from i to j
            m.addConstrs((load[c, k, j] >=
                          load[c, k, i] +
                          self.pk_dl[j, c] -
                          M * (1 - ride[k, i, j])
                          for i, j in self.arcs
                          for k in self.vehicles
                          for c in self.DAO.get_vehicle_dic()[k].get_capacity().keys()), "LOAD")
            
            # (LOAD_MIN) = Load of vehicle k in node i >=
            #              MAX(0, PK/DL demand in i)
            m.addConstrs((load[c, k, i] >= max(0, self.pk_dl[i, c])
                          for c in comp
                          for k in self.vehicles
                          for i in self.nodes), "LOAD_MIN")

            # (LOAD_MAX) = Load of vehicle k in node i >=
            #              MIN(MAX_LOAD, MAX_LOAD - DL demand in i)
            m.addConstrs((load[c, k, i] <=
                          min(self.capacity_vehicle[k, c],
                              self.capacity_vehicle[k, c] + self.pk_dl[i, c])
                          for c in comp
                          for k in self.vehicles
                          for i in self.nodes), "LOAD_MAX")

            #### FEASIBILITY CONSTRAINTS ######################################

            m.addConstrs((load[c, k, i] >= 0
                          for c in comp
                          for k in self.vehicles
                          for i in self.nodes),  "LOAD_0")
            m.addConstrs((arrival_t[k, i] >= 0
                          for k in self.vehicles
                          for i in self.nodes), "ARRI_0")
            m.addConstrs((load[c, k, i] == 0
                          for c in comp
                          for k in self.vehicles
                          for i in [self.start_depot, self.end_depot]), "LOAD_DEPOT_0")

            # obj = sum(ride[k, i, j]*self.cost[k, i, j] for k in avs_ids for i,j in self.arcs)
            # print(obj)
            # m.setObjective(obj, GRB.MINIMIZE)

            #### OPTIMIZE MODEL ###############################################
            m.optimize()

            #### SHOW RESULTS #################################################

            # Get constraints
            # constrs = m.getConstrs()

            # Store route per vehicle
            vehicles_route = {}

            # If status is optimal
            if m.status == GRB.Status.OPTIMAL:

                # Get binary variables Xkij
                var_ride = m.getAttr('x', ride)

                # Get travel self.times of each request
                var_travel_t = m.getAttr('x', travel_t)

                # Get load of vehicle at each point
                var_load = m.getAttr('x', load)

                # Get arrival time at each point
                arrival_t = m.getAttr('x', arrival_t)

                # Create DARP answer
                darp_answer = Response(self.vehicles,
                                       self.arcs,
                                       var_ride,
                                       var_travel_t,
                                       var_load,
                                       arrival_t,
                                       self.DAO)
                # Return anwer
                self.response = darp_answer

        except GurobiError:
            print('Error reported')
        
    ##########################################################################
    ##########################################################################
    ##########################################################################