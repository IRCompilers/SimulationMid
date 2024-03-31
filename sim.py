import numpy as np
from heapq import heapify, heappush, heappop
import json

# Variables

next_client_dist = np.random.poisson
next_complain_dist = np.random.poisson
claim_dist = np.random.binomial
leave_client_dist = np.random.poisson

N0_CLIENTS = 10
A0_INITIAL_BUDGET = 10_000
COST = 100
MAX_TIME = 1_000_000
MAX_CLAIM = 5_000
CLIENT_THRESHOLD = 0

lambda_next_client = 1
lambda_leave_client = 5
lambda_next_complaint = 5
amount_tries = 10
amount_tests = 50


def generate_complain(distribution_function_complain, distribution_function_claim):
    u = np.random.random()
    time_to_complain = distribution_function_complain(lambda_next_complaint)
    claim_amount = distribution_function_claim(MAX_CLAIM, u)

    return time_to_complain, claim_amount


def generate_client(distribution_function_client, distribution_function_leave):
    next_client = distribution_function_client(lambda_next_client)
    leave_client = distribution_function_leave(lambda_leave_client)

    return next_client, leave_client


def insurance_simulation(next_client_dist, next_complain_dist, claim_dist, leave_client_dist, n0_clients,
                         a0_initial_budget, cost, client_threshold):
    total_clients = n0_clients
    total_complaints = 0
    time = 0
    num_clients = n0_clients
    budget = a0_initial_budget
    clients = [leave_client_dist(lambda_leave_client) for _ in range(num_clients)]

    heapify(clients)

    next_client, leave_client = generate_client(next_client_dist, leave_client_dist)
    next_complaint, claim = generate_complain(next_complain_dist, claim_dist)

    while time < MAX_TIME:

        if num_clients != 0 and next_complaint <= next_client:
            t = next_complaint
            next_client -= t
            budget = budget + num_clients * t * cost
            budget = budget - claim
            total_complaints += 1

            if budget < 0:
                return time, total_clients, total_complaints

            next_complaint, claim = generate_complain(next_complain_dist, claim_dist)

            while len(clients) > client_threshold and clients[0] <= t:
                num_clients -= 1
                heappop(clients)

            for i in range(len(clients)):
                clients[i] -= t

            time = time + t

        else:
            t = next_client
            if next_client < next_complaint:
                next_complaint -= t

            num_clients += 1
            total_clients += 1

            heappush(clients, leave_client)
            budget = budget + num_clients * t * cost
            next_client, leave_client = generate_client(next_client_dist, leave_client_dist)

            while len(clients) > client_threshold and clients[0] <= t:
                num_clients -= 1
                heappop(clients)

            for i in range(len(clients)):
                clients[i] -= t

            time = time + t

    return MAX_TIME, total_clients, total_complaints


results = [insurance_simulation(next_client_dist, next_complain_dist, claim_dist, leave_client_dist, N0_CLIENTS,
                                A0_INITIAL_BUDGET, COST, CLIENT_THRESHOLD) for _ in range(amount_tries)]

total_clientes = [j for i,j,k in results]
total_complaints = [k for i,j,k in results]
max_time = [i for i,j,k in results] 

media_max_time = sum(max_time)/len(max_time)
media_total_clients = sum(total_clientes)/len(total_clientes)
media_total_complaints = sum(total_complaints)/len(total_complaints)

def varianza(media, data):
    return (sum([(i-media)**2 for i in data]))/len(data)

varianza_max_time = np.var(max_time)
varianza_total_clients = np.var(total_clientes)
varianza_total_complaints = np.var(total_complaints)

desv_estan_max_time = varianza_max_time**1/2
desv_estan_total_clients = varianza_total_clients**1/2
desv_estan_total_complaints = varianza_total_complaints**1/2

print(media_max_time, media_total_clients, media_total_complaints)
print(varianza_max_time, varianza_total_clients, varianza_total_complaints)
print(desv_estan_max_time, desv_estan_total_clients, desv_estan_total_complaints)
