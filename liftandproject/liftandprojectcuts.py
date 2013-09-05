import cplex

# create alpha subproblem vars (cut coefficients variables)
def create_alpha_vars(subprob, masterprob, mp_var_indices, mp_var_names):
    alpha_vars_dict = {} 
    for var_index, var_name in zip(mp_var_indices, mp_var_names):
        alpha_var_name = 'a_' + var_name
        alpha_var_index = subprob.variables.get_num()
        subprob.variables.add(obj=[-masterprob.solution.get_values(var_index)], names=[alpha_var_name])
        alpha_vars_dict[var_index] = alpha_var_index
        
    return alpha_vars_dict
        
        
# create beta subproblem var (cut rhs variable)
def create_beta_var(subprob):
    beta_var_name = 'b'
    beta_var_index = subprob.variables.get_num()
    subprob.variables.add(obj=[1.0], lb=[-cplex.infinity], ub=[cplex.infinity], names=[beta_var_name])
    return beta_var_name, beta_var_index


# create subproblem u vars (constraint linear combination vars)
def create_u_vars(subprob, master_prob, mp_var_indices, mp_var_names, mp_constr_names, mp_constr_indices):
    u_vars_dict = {}
    int_values = [0, 1]
    for constr_index, constr_name in zip(mp_constr_indices, mp_constr_names):
        for i in int_values:
            u_var_name = 'u_' + str(i)+ '_c_' + constr_name
            u_var_index = subprob.variables.get_num()
            subprob.variables.add(lb=[0.0], ub=[cplex.infinity], names=[u_var_name])
            u_vars_dict[(i, 'c', constr_index)] = u_var_index
    
    bound_constr_types = ['lb', 'ub']        
    for var_index, var_name in zip(mp_var_indices, mp_var_names):
        for i in int_values:
            for type in bound_constr_types:
                u_var_name = 'u_' + str(i) + '_' + type + '_' + var_name
                u_var_index = subprob.variables.get_num()
                subprob.variables.add(lb=[0.0], ub=[cplex.infinity], names=[u_var_name])
                u_vars_dict[(i, type, var_index)] = u_var_index
                
    return u_vars_dict


# create subproblem v vars ()
def create_v_vars(subprob):
    v_vars_dict = {}
    int_values = [0, 1]
    for i in int_values:
        v_var_name = 'v_' + str(i)
        v_var_index = subprob.variables.get_num()
        subprob.variables.add(lb=[-cplex.infinity], ub=[cplex.infinity], names=[v_var_name])
        v_vars_dict[i] = v_var_index     
    return v_vars_dict


# create constraints alpha = uAt + vei
def create_cut_coefficients_constraints(subprob, master_prob, alpha_vars_dict, u_vars_dict, v_vars_dict, cut_var_index, var_indices):
    int_values = [0, 1]
    for var_index in var_indices:
        constr_pairs = master_prob.variables.get_cols(var_index)
        constr_indices = constr_pairs.ind
        constr_coefs = constr_pairs.val
        #print constrs
        #print coefs
        for int_value in int_values:
            vars = [alpha_vars_dict[var_index]]
            coefs = [1.0]
            for constr_index, coef in zip(constr_indices, constr_coefs):
                u_var_index = u_vars_dict[(int_value, 'c', constr_index)]
                vars.append(u_var_index)
                coefs.append(-coef)
            u_var_index = u_vars_dict[(int_value, 'lb', var_index)]
            vars.append(u_var_index)
            coefs.append(-1.0)
            u_var_index = u_vars_dict[(int_value, 'ub', var_index)]
            vars.append(u_var_index)
            coefs.append(1.0)
            if var_index == cut_var_index:
                v_var_index = v_vars_dict[int_value]
                vars.append(v_var_index)
                coefs.append(-1.0)            
            subprob.linear_constraints.add(lin_expr = [cplex.SparsePair(vars, coefs)], senses = ['E'], rhs = [0.0], names = ['Alpha_'+str(var_index)+'_'+str(int_value)])


# create constraints beta <= ub + v
def create_cut_rhs_constraints(subprob, master_prob, beta_var_index, u_vars_dict, v_vars_dict, cut_var_index, var_indices, constr_indices):
    int_values = [0,1]
    for int_value in int_values:
        vars = [beta_var_index, v_vars_dict[int_value]]
        coefs = [1.0, -int_value]
        for constr_index in constr_indices:
            u_var_index = u_vars_dict[(int_value, 'c', constr_index)]
            constr_rhs = master_prob.linear_constraints.get_rhs(constr_index)
            vars.append(u_var_index)
            coefs.append(-constr_rhs)
        for var_index in var_indices:
            # skip lb var constraint because rhs = 0.0
            # add var of ub constraint
            u_var_index = u_vars_dict[(int_value, 'ub', var_index)]            
            vars.append(u_var_index)
            coefs.append(1.0)
        subprob.linear_constraints.add(lin_expr = [cplex.SparsePair(vars, coefs)], senses = ['E'], rhs = [0.0], names = ['Beta_'+str(int_value)])


# create constraint sum(u0) + sum(u1) + v0 + v1 <= 1
def create_normalization_constraint(subprob, master_prob, u_vars_dict, v_vars_dict):
    vars = []
    coefs = []
    for var_index in u_vars_dict.values():
        vars.append(var_index)
        coefs.append(1.0)
    for var_index in v_vars_dict.values():
        vars.append(var_index)
        coefs.append(1.0)
    subprob.linear_constraints.add(lin_expr = [cplex.SparsePair(vars, coefs)], senses = ['L'], rhs = [1.0], names = ['Normalization'])


# separation algorithm to generate lift and project cut for a particular variable (var_index)
def generate_lift_and_project_cut(master_prob, cut_var_index, subproblem_label='lift_and_project_subproblem', save_subproblem_lp=False):    
    var_names = master_prob.variables.get_names()
    var_indices = master_prob.variables.get_indices(var_names)
    constr_names = master_prob.linear_constraints.get_names()
    constr_indices = master_prob.linear_constraints.get_indices(constr_names)
    
    subprob = cplex.Cplex()
    subprob.objective.set_sense(subprob.objective.sense.maximize)    
    
    # create subproblem vars
    alpha_vars_dict = create_alpha_vars(subprob, master_prob, var_indices, var_names)
    beta_var_name, beta_var_index = create_beta_var(subprob)
    u_vars_dict = create_u_vars(subprob, master_prob, var_indices, var_names, constr_names, constr_indices)
    v_vars_dict = create_v_vars(subprob)
    
    # create subproblem constraints
    create_cut_coefficients_constraints(subprob, master_prob, alpha_vars_dict, u_vars_dict, v_vars_dict, cut_var_index, var_indices)
    create_cut_rhs_constraints(subprob, master_prob, beta_var_index, u_vars_dict, v_vars_dict, cut_var_index, var_indices, constr_indices)
    create_normalization_constraint(subprob, master_prob, u_vars_dict, v_vars_dict)
    if save_subproblem_lp:
        subprob.write('output/'+subproblem_label+'.lp')
    
    # solve subproblem
    subprob.set_results_stream(None)
    subprob.solve()
    solution = subprob.solution
    status = solution.get_status()
    obj = solution.get_objective_value()
    
    #solution.write('output/'+subproblem_label+'_solution.out')
    #print
    #print "Subproblem Solution status: " , solution.status[status]
    #print "Subproblem Objective value: " , obj    
    #print
    
    if status != solution.status.optimal or obj <= 0.0:
        print "\t#### No separation cut found!"
        return None
            
    # generate cut
    vars = []
    coefs = []
    for var_index in var_indices:
        vars.append(var_index)
        coefs.append(solution.get_values(alpha_vars_dict[var_index]))
    rhs = solution.get_values(beta_var_index)
    
    #print
    #print '\tCut'
    #print '\tvars', vars
    #print '\tcoefs', coefs
    #print '\trhs', rhs
    #print
        
    return {'vars': vars, 'coefs': coefs, 'sense': 'G', 'rhs': rhs, 'obj': obj}
            
