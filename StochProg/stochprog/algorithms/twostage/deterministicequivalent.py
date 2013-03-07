import sys

from coopr.pyomo import *
from coopr.opt import SolverFactory

from stochprog.problemreader.twostageproblem.twostageproblem import TwoStageProblem
from stochprog.problemreader.smpstotwostagebuilder import SmpsToTwoStageBuilder
from stochprog.problemreader.twostageproblem.constraint import ConstraintType


class DeterministicEquivalent(object):
    
    def __init__(self, two_stage_instance):
        self._instance = two_stage_instance
        #self._instance = TwoStageProblem()
    
    
    def create_model(self):
        print 'Creating Deterministic Equivalent Model'
        
        root_scenario = self._instance.get_root_scenario()        
        first_stage_vars = root_scenario.get_vars_from_stage(1)
        second_stage_vars = root_scenario.get_vars_from_stage(2)
        scenarios = self._instance.get_scenarios()
        
        #var_by_name = {}
        var_by_id = {}
        for var in root_scenario.get_variables():
            #var_by_name[var.get_name()] = var
            var_by_id[var.get_id()] = var
            
        #constr_by_name ={}
        constr_by_id = {}
        for constr in root_scenario.get_constraints():
            #constr_by_name[constr.get_name()] = constr
            constr_by_id[constr.get_id()] = constr
            
        model = ConcreteModel()
        model.x = Var([var.get_id() for var in first_stage_vars], within=NonNegativeReals)
        model.y = Var(range(len(scenarios)), [var.get_id() for var in second_stage_vars], within=NonNegativeReals)
        
        def obj_rule(model):
            expr = sum(root_scenario.get_var_cost(var.get_id()) * model.x[var.get_id()] for var in first_stage_vars)
            for scen in range(len(scenarios)):                
                expr += sum(scenarios[scen].get_var_cost(var.get_id()) * model.y[scen, var.get_id()] for var in second_stage_vars)             
            return expr
        model.obj = Objective(rule=obj_rule)
        
        def first_stage_constraints(model, constr_id):
            constr = constr_by_id[constr_id]
            rhs = root_scenario.get_constr_rhs(constr.get_id())
            
            vars_and_coefs = []
            for var_id, coef in root_scenario.get_constr_var_coefs(constr.get_id()).items():                
                vars_and_coefs.append((var_id, coef))
            expr = sum(coef * model.x[var_id] for var_id, coef in vars_and_coefs)
            
            if constr.get_type() == ConstraintType.E:
                return expr == rhs
            elif constr.get_type() == ConstraintType.GE:
                return expr >= rhs
            elif constr.get_type() == ConstraintType.GT:
                return expr > rhs
            elif constr.get_type() == ConstraintType.LE:
                return expr <= rhs
            elif constr.get_type() == ConstraintType.LT:
                return expr < rhs
        model.constr_first_stage = Constraint([constr.get_id() for constr in root_scenario.get_constrs_of_stage(1)], 
                                              rule=first_stage_constraints)
        
        def second_stage_constraints(model, scen, constr_id):
            scenario = scenarios[scen]
            constr = scenario.get_constraint_by_id(constr_id)
            rhs = scenario.get_constr_rhs(constr_id)
            
            expr = None
            for i, (var_id, coef) in enumerate(scenario.get_constr_var_coefs(constr_id).items()):
                var = var_by_id[var_id]
                if var.get_stage() == 1:
                    if i == 0:
                        expr = coef * model.x[var.get_id()]
                    else:
                        expr += coef * model.x[var.get_id()]
                else:
                    if i == 0:
                        expr = coef * model.y[scen, var.get_id()]
                    else:
                        expr += coef * model.y[scen, var.get_id()]
            
            if expr is None:
                return Constraint.Skip
            
            if constr.get_type() == ConstraintType.E:
                return expr == rhs
            elif constr.get_type() == ConstraintType.GE:
                return expr >= rhs
            elif constr.get_type() == ConstraintType.GT:
                return expr > rhs
            elif constr.get_type() == ConstraintType.LE:
                return expr <= rhs
            elif constr.get_type() == ConstraintType.LT:
                return expr < rhs
        model.constr_second_stage = Constraint(range(len(scenarios)), 
                                               [constr.get_id() for constr in root_scenario.get_constrs_of_stage(2)],
                                               rule=second_stage_constraints)
        self._model = model
        self._det_equiv_instance = self._model.create()        
        #self._det_equiv_instance.pprint()
        
        print '\tNumber of Variables:', (len(model.x) + len(model.y))
        print '\tNumber of Constraints:', (len(model.constr_first_stage) + len(model.constr_second_stage))
        print ''
        
        return model
    
    
    def solve(self, solver):
        print 'Solving Deterministic Equivalent Model'        
        opt = solver
        
        results = opt.solve(self._det_equiv_instance)        
        self._det_equiv_instance.load(results)
        model = self._det_equiv_instance
        
        root_scenario = self._instance.get_root_scenario()        
        first_stage_vars = root_scenario.get_vars_from_stage(1)
        second_stage_vars = root_scenario.get_vars_from_stage(2)
        scenarios = self._instance.get_scenarios()
        
        # Print variables with cost in objective function
#        for var in first_stage_vars:
#            if var.get_cost() != 0.0:
#                print var.get_name(), " = " , model.x[var.get_name()].value, " * ", var.get_cost()
#        for scen in range(len(scenarios)):
#            for var in second_stage_vars:
#                if scenarios[scen].get_var_cost(var) != 0.0:
#                    print var.get_name(), " = ", model.y[scen, var.get_name()].value, " * ", scenarios[scen].get_var_cost(var) 
                    
        #results.write()
        print '\tOptimal Solution: ', value(model.obj)
        print ''

def _main(argv):  
    print 'Arguments:', argv
    if len(argv) < 5:
        print 'Error: missing command line arguments'
        print 'Specify: files_directory_path core_file time_file stoch_file'        
        return
        
    dir_path = argv[1]
    if not dir_path.endswith('/'):
        dir_path += '/'
    
    CORE_FILE_PATH = dir_path + argv[2]
    TIME_FILE_PATH = dir_path + argv[3]
    STOCH_FILE_PATH = dir_path + argv[4]
        
    two_stage_builder = SmpsToTwoStageBuilder(CORE_FILE_PATH, TIME_FILE_PATH, STOCH_FILE_PATH)
    two_stage_problem = two_stage_builder.build_two_stage_instance()
    
    det_equiv = DeterministicEquivalent(two_stage_problem)
    model = det_equiv.create_model()
    
    #solver = SolverFactory('cplex', solver_io='python')
    solver = SolverFactory('cplex')
    
    #model.pprint()
    #det_equiv.solve('cbc')
    det_equiv.solve(solver)
    #det_equiv.solve()


if __name__ == "__main__":
    _main(sys.argv)
    
    
    
    