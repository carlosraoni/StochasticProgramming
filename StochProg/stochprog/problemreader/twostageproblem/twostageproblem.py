import copy
from stochprog.problemreader.twostageproblem.variable import Variable
from stochprog.problemreader.twostageproblem.variable import VariableType
from stochprog.problemreader.twostageproblem.constraint import Constraint
from stochprog.problemreader.twostageproblem.scenario import Scenario

class TwoStageProblem(object):
    
    def __init__(self):
        self._root_scenario = Scenario(0)
        self._scenarios = []
    
        
    def get_root_scenario(self):
        return self._root_scenario


    def get_scenarios(self):
        return self._scenarios 
    
        
    def add_root_variable(self, name, cost, stage, var_type=VariableType.REAL):
        var_id = len(self._root_scenario.get_variables())
        var = Variable(var_id, name, stage, var_type)
        
        self._root_scenario.add_var(var)
        self._root_scenario.set_var_cost(var_id, cost)
        
        return var_id
    
    
    def add_root_constraint(self, name, constr_type, vars_and_coefficients, rhs, stage):
        constr_id = len(self._root_scenario.get_constraints())
        constr = Constraint(constr_id, name, stage, constr_type)        
            
        self._root_scenario.add_constraint(constr)
        self._root_scenario.set_constr_rhs(constr_id, rhs)
        for var_id, coef in vars_and_coefficients:
            self._root_scenario.set_var_coef_in_constr(var_id, constr_id, coef)
        
        return constr_id
    
    
    def add_scenario(self, probability, cost_changes, coefficient_changes, rhs_changes):
        scen = Scenario(len(self._scenarios) + 1, probability, self._root_scenario)
        
        for var_id, cost in cost_changes:
            scen.set_var_cost(var_id, cost)                
        
        for var_id, constr_id, coef in coefficient_changes:            
            scen.set_var_coef_in_constr(var_id, constr_id, coef)
        
        for constr_id, rhs in rhs_changes:
            scen.set_constr_rhs(constr_id, rhs)
    
        self._scenarios.append(scen)
        
        return scen

    
    def print_instance(self):
        print 'Num Scenarios', len(self._scenarios)
        
