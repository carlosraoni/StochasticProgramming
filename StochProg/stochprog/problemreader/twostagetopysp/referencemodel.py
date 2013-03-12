from coopr.pyomo import *

class ReferenceModel(object):
    
    def __init__(self):
        pass
    
    def create_model(self):
        model = AbstractModel()
        
        # Sets definitions
        model.var_set = Set()
        model.var_set_first_stage = Set(within=model.var_set)
        model.var_set_second_stage = Set(within=model.var_set)
        model.constr_set = Set()
        
        # Param definitions
        model.constr_type = Param(model.constr_set)
        model.cost = Param(model.var_set, default=0.0)
        model.rhs = Param(model.constr_set, default=0.0)
        model.coef = Param(model.constr_set, model.var_set, default=0.0)
        
        # Var definitions
        model.x = Var(model.var_set_first_stage)
        model.y = Var(model.var_set_second_stage)
        model.first_stage_cost = Var()
        model.second_stage_cost = Var()
        
        # Constraint definitions
        def constrs_rule(model, constr):
            expr = summation((model.coef[constr,var], model.x[var]) 
                                for var in model.var_set_first_stage if model.coef[constr, var] != 0.0 )
            expr += summation((model.coef[constr,var], model.y[var]) 
                                for var in model.var_set_second_stage if model.coef[constr, var] != 0.0 )
            if expr is None:
                return Constraint.Skip
            
            rhs = model.rhs[constr]
            constr_type = model.constr_type[constr]
            if constr_type == 'E':
                return expr == rhs
            elif constr_type == 'GE':
                return expr >= rhs
            elif constr_type == 'GT':
                return expr > rhs
            elif constr_type == 'LE':
                return expr <= rhs
            elif constr_type == 'LT':
                return expr < rhs
            return Constraint.Skip
        model.constraints = Constraint(model.constr_set, rule=constrs_rule)
        
        # Objective function definitions
        def constr_cost_first_stage_rule(model):
            expr = summation((model.cost[var], model.x[var])
                                for var in model.var_set_first_stage if model.cost[var] != 0.0)
            return model.first_stage_cost - expr == 0.0
        model.constr_cost_first_stage = Constraint(rule=constr_cost_first_stage_rule)
        
        def constr_cost_second_stage_rule(model):
            expr = summation((model.cost[var], model.y[var])
                                for var in model.var_set_second_stage if model.cost[var] != 0.0)
            return model.second_stage_cost - expr == 0.0
        model.constr_cost_second_stage = Constraint(rule=constr_cost_second_stage_rule)
                
        def obj_rule(model):
            return model.first_stage_cost + model.second_stage_cost
        model.obj = Objective(rule=obj_rule)
        
                
        
        