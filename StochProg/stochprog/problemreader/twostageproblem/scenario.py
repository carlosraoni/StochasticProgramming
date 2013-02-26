

class Scenario(object):
    
    def __init__(self, id):
        self._id = id
        self._variables = []
        self._variables_by_id = {}
        self._constraints = []
        self._constraints_by_id = {}
        self._probability = 1
        
    
    def get_id(self):
        return self._id
        
    
    def get_var_cost(self, var):
        return self._variables_by_id[var.get_id()].get_cost()
    
    
    def set_probability(self, prob):
        self._probability = prob
    
    
    def update_second_stage_costs(self):
        for var in self._variables:
            if var.is_second_stage():
                var.set_cost(var.get_cost() * self._probability)
    
    
    def set_var_coef(self, var):
        self._variables.append(var)
        self._variables_by_id[var.get_id()] = var
    
    
    def add_constraint(self, constr):
        self._constraints.append(constr)
        self._constraints_by_id[constr.get_id()] = constr
        
        
    def get_variables(self):
        return self._variables
    
    
    def get_constraints(self):
        return self._constraints
    
    
    def get_constraint_by_id(self, constr_id):
        return self._constraints_by_id.get(constr_id, None)
    
    
    def set_constr_rhs(self, constr_id, rhs):
        constr = self._constraints_by_id[constr_id]
        constr.set_rhs(rhs)
        
        
    def set_var_coef_in_constr(self, var_id, constr_id, coef):
        constr = self._constraints_by_id[constr_id]
        constr.set_var_coef(var_id, coef)
        
        
    def set_var_cost(self, var_id, cost):
        var = self._variables_by_id[var_id]
        var.set_cost(cost) 
        
        
    def get_vars_from_stage(self, stage):
        return [var for var in self._variables if var.get_stage() == stage]
    
    
    def get_constrs_of_stage(self, stage):
        return [constr for constr in self._constraints if constr.get_stage() == stage]
        
        
    