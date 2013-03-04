

class Scenario(object):
    
    def __init__(self, id, probability=1, base_scenario=None):
        self._id = id
        self._base_scenario = base_scenario
        self._variables_by_id = {}        
        self._constraints_by_id = {}
        
        self._var_cost = {}
        self._constr_rhs = {}        
        self._constr_coefs = {}
        
        self._probability = probability
        
    
    def get_id(self):
        return self._id
        
    
    def get_var_cost(self, var_id):
        cost = self._var_cost.get(var_id, None)
        if cost is None:
            if not self._base_scenario is None:
                return self._base_scenario.get_var_cost(var_id) * self._probability
            else:
                cost = 0.0 
        return cost * self._probability
     
     
    def set_var_cost(self, var_id, cost):
        self._var_cost[var_id] = cost 
           
    
    def get_probability(self):
        return self._probability
                   
    
    def get_variables(self):
        var_set = set(self._variables_by_id.values())
        if not self._base_scenario is None:
            var_set.update(self._base_scenario.get_variables())            
        return var_set
    
    
    def add_var(self, var):        
        self._variables_by_id[var.get_id()] = var
    
    
    def get_constraints(self):
        constr_set = set(self._constraints_by_id.values())
        if not self._base_scenario is None:
            constr_set.update(self._base_scenario.get_constraints())
        return constr_set
    
    
    def add_constraint(self, constr):        
        self._constraints_by_id[constr.get_id()] = constr
        
    
    def get_constraint_by_id(self, constr_id):
        constr = self._constraints_by_id.get(constr_id, None)
        if constr is None and not self._base_scenario is None:
            return self._base_scenario.get_constraint_by_id(constr_id)
        return constr
    
    
    def get_constr_rhs(self, constr_id):
        rhs = self._constr_rhs.get(constr_id, None)
        if rhs is None:
            if not self._base_scenario is None:
                return self._base_scenario.get_constr_rhs(constr_id)
            else:
                rhs = 0.0 
        return rhs
    
    def set_constr_rhs(self, constr_id, rhs):
        self._constr_rhs[constr_id] = rhs
        
        
    def _extend_constr_var_coefs(self, constr_id, var_coefs):
        #print self._id, self._base_scenario
        if not self._base_scenario is None:
            self._base_scenario._extend_constr_var_coefs(constr_id, var_coefs)
        var_coefs_scen = self._constr_coefs.get(constr_id, None)
        if not var_coefs_scen is None:
            var_coefs.update(var_coefs_scen)
    
        
    def get_constr_var_coefs(self, constr_id):
        var_coefs = {}
        self._extend_constr_var_coefs(constr_id, var_coefs)
        return var_coefs
    
        
    def set_var_coef_in_constr(self, var_id, constr_id, coef):
        coef_map = self._constr_coefs.get(constr_id, None)
        if coef_map is None:
            coef_map = {}
            self._constr_coefs[constr_id] = coef_map
        coef_map[var_id] = coef
                
        
    def get_vars_from_stage(self, stage):
        return [var for var in self.get_variables() if var.get_stage() == stage]
    
    
    def get_constrs_of_stage(self, stage):
        return [constr for constr in self.get_constraints() if constr.get_stage() == stage]
        
        
    