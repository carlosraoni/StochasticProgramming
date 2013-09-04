import sys
import cplex
from cplex._internal._matrices import SparsePair

# global constants
__MAX_ITER = 1 # Max number of iterations for the cutting plane algorithm

# global instance data structures
triples = []
triples_by_node = []
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
        triples_by_node = [[] for i in xrange(n)]       
                
        for i in range(m):
            line_fields = instance.readline().split()
            triple = (int(line_fields[0]) - 1, int(line_fields[1]) - 1, int(line_fields[2]) - 1)
            triples[i] = triple
            triples_by_node[triple[0]].append(i)
            triples_by_node[triple[1]].append(i)
            triples_by_node[triple[2]].append(i)
                
    return n, m, triples            


# create alpha subproblem vars (cut coefficients variables)
def create_alpha_vars(subprob, masterprob, mp_var_indices, mp_var_names):
    alpha_vars_dict = {} 
    for var_index, var_name in zip(mp_var_indices, mp_var_names):
        alpha_var_name = 'a_' + var_name
        alpha_var_index = subprob.variables.get_num()
        subprob.variables.add(obj=[-masterprob.solution.get_values(var_index)], names=[alpha_var_name])
        alpha_vars_dict[var_index] = (alpha_var_name, alpha_var_index)
        
    return alpha_vars_dict
        
        
# create beta subproblem var (cut rhs variable)
def create_beta_var(subprob):
    beta_var_name = 'b'
    beta_var_index = subprob.variables.get_num()
    subprob.variables.add(obj=[1.0], names=[beta_var_name])
    return beta_var_name, beta_var_index


# create subproblem u vars (constraint linear combination vars)
def create_u_vars(subprob, master_prob, mp_var_indices, mp_var_names, mp_constr_names, mp_constr_indices):
    pass


# create subproblem v vars ()
def create_v_vars(subprob):
    v_vars_dict = {}
    v1_var_name = 'v1'
    v1_var_index = subprob.variables.get_num()
    subprob.variables.add(names=[v1_var_name])
    v_vars_dict[1] = (v1_var_name, v1_var_index) 
    
    v2_var_name = 'v2'
    v2_var_index = subprob.variables.get_num()
    subprob.variables.add(names=[v2_var_name])
    v_vars_dict[2] = (v2_var_name, v2_var_index)
    
    return v_vars_dict


# separation algorithm to generate lift and project cut for a particular variable (var_index)
def generate_lift_and_project_cut(master_prob, var_index, subproblem_label='lift_and_project_subproblem', save_subproblem_lp=False):    
    var_names = master_prob.variables.get_names()
    var_indices = master_prob.variables.get_indices(var_names)
    constr_names = master_prob.linear_constraints.get_names()
    constr_indices = master_prob.linear_constraints.get_indices(constr_names)
    
    subprob = cplex.Cplex()
    subprob.objective.set_sense(subprob.objective.sense.maximize)    
    
    alpha_vars_dict = create_alpha_vars(subprob, master_prob, var_indices, var_names)
    beta_var_name, beta_var_index = create_beta_var(subprob)
    u_vars_dict = create_u_vars(subprob, master_prob, var_indices, var_names, constr_names, constr_indices)
    v_vars_dict = create_v_vars(subprob)
    
    return None, 0.0


# method to add a cut to a problem
def add_cut_to_problem(prob, cut):
    pass


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
    master_prob.write('./output/problem_'+str(iteration)+'.lp')
    
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
            print 'Variable x_' + str(i) +' fractional = ' + str(val)
            print 'Running lift and project separation for x_' + str(i)
            subproblem_label = 'iter_' + str(iteration) + '_subproblem_x_' + str(i)
            cut, sub_problem_obj = generate_lift_and_project_cut(master_prob, x[i], subproblem_label, True)
            if cut is not None and sub_problem_obj > 0.0:
                iteration_cuts.append(cut)
        else:
            print 'Variable x_' + str(i) +' integer = ' + str(val)
    
    if len(iteration_cuts) == 0:
        print "No cut found! Finishing Algorithm!"
        print "---------------------------------------------------------------------------------------"
        break
    
    print "Adding cuts to the master problem"
    for cut in iteration_cuts:
        add_cut_to_problem(master_prob, cut)
        
    print "---------------------------------------------------------------------------------------"
    iteration += 1


print
print 'Final Solution:'
print

solution = master_prob.solution
print "\tCpx Objective value: " , solution.get_objective_value()
    
x_values = solution.get_values(x)
print "\tSolution: ", x_values
