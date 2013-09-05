import sys
import cplex

from cplex._internal._matrices import SparsePair
from liftandprojectcuts import generate_lift_and_project_cut

# global constants
__MAX_ITER = 100 # Max number of iterations for the cutting plane algorithm

# global instance data structures
triples = []
n = 0
m = 0

# global model variables
x = [] 

# method to read instance files
def read_instance(file_path):
    with open(file_path) as instance:
        line_fields = instance.readline().split()
        n = int(line_fields[0])
        m = int(line_fields[1])
        triples = [None for i in xrange(m)]
        for i in range(m):
            line_fields = instance.readline().split()
            triple = (int(line_fields[0]) - 1, int(line_fields[1]) - 1, int(line_fields[2]) - 1)
            triples[i] = triple            
                
    return n, m, triples            


# Parse argument
if len(sys.argv) < 2:
    print 'Usage: ', sys.argv[0],' instance'
    exit(1)
    
n, m, triples = read_instance(sys.argv[1])
print 'n =', n
print 'm = ', m
print triples

master_prob = cplex.Cplex()

# Create problem variables
for i in range(n):
    var_index = master_prob.variables.get_num()
    var_name = 'x_' + str(i)
    x.append(var_index)
    #master_prob.variables.add(obj = [1.0], lb = [0.0], ub = [1.0], types = ['B'], names = [var_name])
    master_prob.variables.add(obj = [1.0], lb = [0.0], ub = [1.0], names = [var_name])
    
# Create problem constraints
for i in range(m):
    vars = [x[triples[i][0]], x[triples[i][1]], x[triples[i][2]]]
    coefs = [1.0, 1.0, 1.0]    
    master_prob.linear_constraints.add(lin_expr = [cplex.SparsePair(vars, coefs)], senses = ['G'], rhs = [1.0], names = ['T_'+str(i)])


# Cutting plane loop
iteration = 0
while iteration < __MAX_ITER:        
    print "-------------------------- Iteration", iteration, "------------------------------------------------"
    # Save current model to a file
    #master_prob.write('./output/problem_'+str(iteration)+'.lp')
    
    # Optimize current model
    master_prob.solve()
    
    solution = master_prob.solution
    print "Cpx Solution status: " , solution.status[solution.get_status()]
    print "Cpx Objective value: " , solution.get_objective_value()
    
    x_values = solution.get_values(x)
    print "Solution: ", x_values
    print
    
    iteration_cuts = []
    for i in range(n):
        val = x_values[x[i]]
        if val > 0.0 and val < 1.0:
            #print 'Variable x_' + str(i) +' fractional = ' + str(val)
            print 'Running lift and project separation for x_' + str(i)
            subproblem_label = 'iter_' + str(iteration) + '_subproblem_x_' + str(i)
            cut = generate_lift_and_project_cut(master_prob, x[i], subproblem_label, save_subproblem_lp=False)
            if cut is not None:
                iteration_cuts.append(cut)
        else:
            print 'Variable x_' + str(i) +' integer = ' + str(val)
    
    if len(iteration_cuts) == 0:
        print "No cut found! Finishing Algorithm!"
        print "---------------------------------------------------------------------------------------"
        break
    
    print "Adding cuts to the master problem"
    for cut in iteration_cuts:
        master_prob.linear_constraints.add(lin_expr = [cplex.SparsePair(cut['vars'], cut['coefs'])], senses = [cut['sense']], rhs = [cut['rhs']])
        
    print "---------------------------------------------------------------------------------------"
    iteration += 1


master_prob.write('./output/master_problem.lp')
# Optimize current model
master_prob.solve()

print
print 'Final Solution:'
print

solution = master_prob.solution
print "\tCpx Objective value: " , solution.get_objective_value()
    
x_values = solution.get_values(x)
print "\tSolution: ", x_values
