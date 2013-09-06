import sys
import cplex

from cplex._internal._matrices import SparsePair
from liftandprojectcuts import generate_lift_and_project_cuts,\
    lift_and_project_cutting_plane_loop
import time

__MAX_ITER = 100 # Max number of iterations for the cutting plane algorithm

# method to read instance files
def read_instance(file_path):
    with open(file_path) as instance:
        line_fields = instance.readline().split()
        n = int(line_fields[0])
        m = int(line_fields[1])
        edges = [None for i in xrange(m)]
        for i in range(m):
            line_fields = instance.readline().split()
            triple = (int(line_fields[0]) - 1, int(line_fields[1]) - 1, int(line_fields[2]) - 1)
            edges[i] = triple            
                
    return n, m, edges            


# Parse argument
if len(sys.argv) < 2:
    print 'Usage: ', sys.argv[0],' instance'
    exit(1)

start_time = time.time()
    
n, m, edges = read_instance(sys.argv[1])
print 'n =', n
print 'm = ', m
print edges

master_prob = cplex.Cplex()

x = []
# Create problem variables
for i in range(n):
    var_index = master_prob.variables.get_num()
    var_name = 'x_' + str(i)
    x.append(var_index)
    #master_prob.variables.add(obj = [1.0], lb = [0.0], ub = [1.0], types = ['B'], names = [var_name])
    master_prob.variables.add(obj = [1.0], lb = [0.0], ub = [1.0], names = [var_name])
    
# Create problem constraints
for i in range(m):
    vars = [x[edges[i][0]], x[edges[i][1]], x[edges[i][2]]]
    coefs = [1.0, 1.0, 1.0]    
    master_prob.linear_constraints.add(lin_expr = [cplex.SparsePair(vars, coefs)], senses = ['G'], rhs = [1.0], names = ['T_'+str(i)])

# lift and project loop
lift_and_project_cutting_plane_loop(master_prob, __MAX_ITER)

#master_prob.variables.set_types([(var_name, 'B') for var_name in master_prob.variables.get_names()])
#master_prob.solve()

print
print 'Final Solution:'
print

solution = master_prob.solution
print "\tCpx Objective value: " , solution.get_objective_value()
    
x_values = solution.get_values(x)
print "\tSolution: ", x_values

print
print 'Total Execution Time:', time.time() - start_time, 'seconds'