from Dao import *
from OptMethod import *

# Every ride can only be MAX_LATENESS seconds over the fastest trip
# Every vehicle must serve a request within MAX_PICKUP_LATENESS seconds
MAX_LATENESS = 600
MAX_PICKUP_LATENESS = 300
MAX_STEPS = 2000000000

# Define parameters of method
max_lateness = MAX_LATENESS
max_pickup_lateness = MAX_PICKUP_LATENESS
max_steps = MAX_STEPS

DAO = DaoSARP_NYC()
darp2 = SARP_PL(DAO, max_lateness, max_pickup_lateness, max_steps)
darp2.plot_result()
#print(darp2)