import simpy
import random
import statistics
import matplotlib.pyplot as plt

RANDOM_SEED = 42
SIM_TIME = 480 
ORDER_INTERVAL = 5 
DELIVERY_TIME = (15, 25)

wait_times = []
delivery_times = []

def monitor_queue(env, drivers,time_stamps,queue_length_over_time):

    while True:
        queue_length_over_time.append(len(drivers.queue))
        time_stamps.append(env.now)
        yield env.timeout(5)

def delivery_order(env, drivers):
    arrival_time = env.now
    with drivers.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        
        service_time = random.uniform(*DELIVERY_TIME)
        yield env.timeout(service_time)
        delivery_times.append(env.now - arrival_time)

def order_generator(env, drivers):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / ORDER_INTERVAL))
        i += 1
        env.process(delivery_order(env, f"Order {i}", drivers))
    
def run_simulation(num_drivers):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    drivers = simpy.Resource(env, capacity=num_drivers)
    time_stamps = []
    queue_length_over_time = []
    env.process(order_generator(env, drivers))
    env.process(monitor_queue(env, drivers, time_stamps, queue_length_over_time))
    env.run(until=SIM_TIME)

    avg_wait = statistics.mean(wait_times)
    avg_delivery = statistics.mean(delivery_times)
    utilization = (sum(delivery_times) / (SIM_TIME * num_drivers)) * 100

    return avg_wait, avg_delivery, utilization, time_stamps, queue_length_over_time