#!/usr/bin/python

import sys
import math
import random
import networkx as nx

from gurobipy import *


def build_adj_matrix(edges):
    adj = [[] for i in range(n)]
    for i, j in edges:
        adj[i].append(j)      
    return adj

        
def rec_dfs(adj, curr, visited, comp):
    visited[curr] = True
    comp.append(curr)
    for dest in adj[curr]:
        if not visited[dest]:
            rec_dfs(adj, dest, visited, comp)


def dfs(edges, source=None):
    visited = [False] * n    
    adj = build_adj_matrix(edges)
    
    if source is not None:
        component = []
        rec_dfs(adj, source, visited, component)
        return component
    
    components = []    
    for i in range(n):
        if visited[i]:
            break
        new_component = []
        rec_dfs(adj, i, visited, new_component)
        components.append(new_component)        
    
    return components


# Given a list of edges, finds the shortest subtour
def subtour(edges):
    components = dfs(edges)
    lengths = [len(comp) for comp in components]    
    return components[lengths.index(min(lengths))]


def generate_subtour_cut(model):
    selected = []
    # make a list of edges selected in the solution
    for i in range(n):
        sol = model.cbGetSolution([model._vars[i, j] for j in range(n)])
        selected += [(i, j) for j in range(n) if sol[j] > 0.5]

    # find the shortest cycle in the selected edge list
    tour = subtour(selected)    
    if len(tour) < n:
        print 'Subtour cut generated: ', tour
        expr = 0
        for i in range(len(tour)):
            for j in range(i + 1, len(tour)):
                expr += model._vars[tour[i], tour[j]]                
        return expr <= len(tour) - 1
    return None


def mincut(edges):    
    G = nx.DiGraph()
    for i in range(n):
        G.add_node(i) 
    for i, j, cap in edges:
        if abs(cap - 1.0) <= 1e-9:
            cap = 1.0
        G.add_edge(i, j, capacity=cap)        
    
    source = 0
    min_flow = None
    edges_min_flow = None
    sink_min_flow = None
    for sink in range(1, n):                
        flow, F = nx.ford_fulkerson(G, source, sink)
        if sink_min_flow is None or flow < min_flow:
            sink_min_flow = sink
            min_flow = flow
            edges_min_flow = F.copy()            
    
    residual_edges = []
    for i, j, edge_capacity in edges:            
        edge_flow = edges_min_flow[i][j]            
        if abs(edge_capacity - edge_flow) > 1e-9:
            residual_edges.append((i, j))
    
    source_component = dfs(residual_edges, source)
    print 'MinFlow:', min_flow
    print 'Component MinFlow:', source_component
    
    return source_component, min_flow
    

def generate_mincut_cut(model):
    selected = []        
    for i in range(n):
        for j in range(n):
            xij = model.cbGetNodeRel(model._vars[i, j])                
            if xij > 0.0:
                selected.append((i, j, xij))            
              
    source_component, min_flow = mincut(selected)
    if len(source_component) == n or min_flow >= 2.0:
        return None
    
    comp_set = set(source_component)
    expr = 0
    for i in source_component:
        for j in range(n):
            if j not in comp_set:
                expr += model._vars[i, j]
    return expr >= 2.0


def cut_generation_callback(model, where):
    if where == GRB.callback.MIPSOL:
        print 'Cut Generation at Integer Solution'
        cut = generate_subtour_cut(model)
        if cut is not None:        
            print cut
            model.cbLazy(cut)
         
    if where == GRB.callback.MIPNODE:
        status = model.cbGet(GRB.callback.MIPNODE_STATUS)        
        if status != GRB.OPTIMAL:
            return
        print 'Cut Generation at Fractional Solution'
        cut = generate_mincut_cut(model)
        if cut is not None:
            print cut
            model.cbCut(cut)
                   
# Euclidean distance
def euc_distance(points, i, j):
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return int(math.sqrt(dx * dx + dy * dy))

# Latitude and longitude of a point
PI = 3.141592
def latitude_longitude(x, y):    
    degx = int(x)
    minx = x - degx
    latitude =  (PI * (degx + 5.0*minx/3.0))/180.0
    
    degy = int(y)
    miny = y - degy
    longitude = (PI * (degy + 5.0*miny/3.0))/180.0    
    
    return latitude, longitude
 
# Geographical distance
RRR = 6378.388
def geo_distance(points, i, j):    
    lati, longi = latitude_longitude(points[i][0], points[i][1])
    latj, longj = latitude_longitude(points[j][0], points[j][1])     
    q1 = math.cos(longi - longj)
    q2 = math.cos(lati - latj)
    q3 = math.cos(lati + latj)
    param = 0.5*( ((1.0+q1)*q2) - ((1.0-q1)*q3) )
    
    return int(RRR * math.acos(param) + 1.0)

# Distance between two points depending on the type
def distance(points, i, j, edge_type):
    if edge_type == 'EUC_2D':
        return euc_distance(points, i, j)
    elif edge_type == 'GEO':
        return geo_distance(points, i, j)
    else:
        print 'Type:', edge_type, 'not supported!'        
    return 0

# Reads the header of a tsplib file
def read_file_header(instance):
    fields = instance.readline().split(':')
    params = {}
    while len(fields) == 2:
        section_name = fields[0].strip()
        params[section_name] = fields[1].strip()
        print section_name, ':', params[section_name]
        fields = instance.readline().split(':')
                
    n = int(params.get('DIMENSION'))
    edge_weight_type = params.get('EDGE_WEIGHT_TYPE')
    
    return n, edge_weight_type

# Reads node coordinates section of a tsplib file
def read_node_coords(instance, n):
    # NODE_COORD_SECTION    
    points = []
    for i in range(n):
        fields = instance.readline().split()
        x = float(fields[1])
        y = float(fields[2])
        points.append((x, y))
        print fields[0], ':', x, ',', y
    
    return points

# Read TSP file: euc2d or geo
def read_tsplib_instance(instance_path):    
    with open(instance_path) as instance:
        n, edge_weight_type = read_file_header(instance)        
        points = read_node_coords(instance, n)        
    
    # Calculate the distance matrix
    dist = [[0]*n for i in range(n)]
    for i in range(n):
        for j in range(i + 1):
            dij = distance(points, i, j, edge_weight_type)
            dist[i][j] = dij
            dist[j][i] = dij
    
    return n, dist


# Parse argument
if len(sys.argv) < 2:
    print 'Usage: tsp.py instance'
    exit(1)
    
instance_path = sys.argv[1]
n, dist = read_tsplib_instance(instance_path)

m = Model()

# Create variables
vars = {}
for i in range(n):
    for j in range(i + 1):
        vars[i, j] = m.addVar(obj=dist[i][j], vtype=GRB.BINARY,
                             name='e' + str(i) + '_' + str(j))
        vars[j, i] = vars[i, j]
m.update()

# Add degree-2 constraint, and forbid loops
for i in range(n):
    m.addConstr(quicksum(vars[i, j] for j in range(n)) == 2)
    vars[i, i].ub = 0
m.update()

# Optimize model
m._vars = vars
m.params.LazyConstraints = 1
m.optimize(cut_generation_callback)

solution = m.getAttr('x', vars)
selected = [(i, j) for i in range(n) for j in range(n) if solution[i, j] > 0.5]

opt_tour = subtour(selected)
assert len(opt_tour) == n

cost = 0
for i in range(1, n):
    cost += dist[opt_tour[i-1]][opt_tour[i]]
cost += dist[opt_tour[n-1]][opt_tour[0]]
    
print
print 'Optimal tour:', subtour(selected)
print 'Optimal cost:', m.objVal
print 'Tour cost:', cost
print


        
