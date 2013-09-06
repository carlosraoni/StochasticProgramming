import sys
import cplex

from cplex._internal._matrices import SparsePair
from liftandprojectcuts import generate_lift_and_project_cuts
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


# Cutting plane loop
iteration = 0
previous_obj = 0.0
while iteration < __MAX_ITER:        
    print "-------------------------- Iteration", iteration, "------------------------------------------------"
    # Save current model to a file
    #master_prob.write('./output/problem_'+str(iteration)+'.lp')
    
    # Optimize current model
    master_prob.solve()    
    solution = master_prob.solution
    current_obj = solution.get_objective_value()
    print "Cpx Solution status: " , solution.status[solution.get_status()]    
    print "Cpx Objective value: " , current_obj
    
    x_values = solution.get_values(x)
    print "Solution: ", x_values
    print
    
    #if abs(previous_obj - current_obj) < 1e-15:
    #    break
    previous_obj = current_obj
    
    print 'Running lift and project separation'
    iteration_cuts = generate_lift_and_project_cuts(master_prob)
    if len(iteration_cuts) == 0:
        print "No cut found! Finishing Algorithm!"
        print "---------------------------------------------------------------------------------------"
        break
    
    print "Adding cuts to the master problem"
    deepest_cut = iteration_cuts[0]
    for cut in iteration_cuts:
        if cut['obj'] > deepest_cut['obj']:
            deepest_cut = cut
        master_prob.linear_constraints.add(lin_expr = [cplex.SparsePair(cut['vars'], cut['coefs'])], senses = [cut['sense']], rhs = [cut['rhs']])
    #master_prob.linear_constraints.add(lin_expr = [cplex.SparsePair(deepest_cut['vars'], deepest_cut['coefs'])], senses = [deepest_cut['sense']], rhs = [deepest_cut['rhs']])
    print "---------------------------------------------------------------------------------------"
    iteration += 1


# Optimize last model
master_prob.write('./output/master_problem.lp')
master_prob.solve()

print
print 'Final Solution:'
print

solution = master_prob.solution
print "\tCpx Objective value: " , current_obj
    
x_values = solution.get_values(x)
print "\tSolution: ", x_values

print
print 'Total Exectution Time:', time.time() - start_time, 'seconds'