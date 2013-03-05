
from stochprog.problemreader.smpsreader.smpsreader import SMPSReader
from stochprog.problemreader.twostageproblem.twostageproblem import TwoStageProblem


class SmpsToTwoStageBuilder(object):
    
    def __init__(self, core_file_path, time_file_path, stoch_file_path):
        self._smps_reader = SMPSReader(core_file_path, time_file_path, stoch_file_path)
        self._two_stage_problem = None
                

    def _add_vars_from_cols(self, var_by_col, obj, cols, stage):
        for col in cols:
            cost = obj.get_coef_of_column(col)
            var_id = self._two_stage_problem.add_root_variable(col.get_name(), cost, stage)
            var_by_col[col] = var_id
        
        
    def _add_constrs_from_rows(self, var_by_col, constr_by_row, rows, stage):
        for row in rows:
            vars_and_coefs = [(var_by_col[col], coef) for col, coef in row.get_columns_and_coefs()]
            constr_id = self._two_stage_problem.add_root_constraint(row.get_name(), row.get_type(), vars_and_coefs, row.get_rhs(), stage)
            constr_by_row[row] = constr_id        
    
    
    def _generate_scenarios(self, random_events, realizations, prob, cost_changes, coef_changes, rhs_changes):
        n = len(random_events)
        prof = len(realizations)
        
        if n == prof:
            scen = self._two_stage_problem.add_scenario(prob, cost_changes, coef_changes, rhs_changes) 
            print '.',
            if scen.get_id() % 40 == 0:                
                print '\n\t',
            return
        
        for realization in random_events[prof]:
            prob_rea, cost_rea_changes, coef_rea_changes, rhs_rea_changes = realization 
            ncost_rea_changes, ncoef_rea_changes, nrhs_rea_changes = len(cost_rea_changes), len(coef_rea_changes), len(rhs_rea_changes)
            
            realizations.append(realization)
            
            cost_changes.extend(cost_rea_changes)
            coef_changes.extend(coef_rea_changes)
            rhs_changes.extend(rhs_rea_changes)
            
            self._generate_scenarios(random_events, realizations, prob * prob_rea, cost_changes, coef_changes, rhs_changes)
            
            cost_changes = cost_changes[:len(cost_changes) - ncost_rea_changes]
            coef_changes = coef_changes[:len(coef_changes) - ncoef_rea_changes]
            rhs_changes = rhs_changes[:len(rhs_changes) - nrhs_rea_changes]
            
            realizations.pop()
    
    
    def build_two_stage_instance(self):
        self._two_stage_problem = TwoStageProblem()
        self._smps_reader.read()
        
        print 'Generating Problem Instance'
        print '\tCreating Core Scenario'
        
        # TODO: Use the TwoStageProblem class interface to build an instance from smps_reader data
        var_by_col = {}
        constr_by_row = {}
        
        rhs_name = self._smps_reader.get_rhs_name()
        obj = self._smps_reader.get_objective_function()
        
        first_stage_cols = self._smps_reader.get_columns_of_stage(1)
        second_stage_cols = self._smps_reader.get_columns_of_stage(2)
        first_stage_rows = self._smps_reader.get_rows_of_stage(1)
        second_stage_rows = self._smps_reader.get_rows_of_stage(2)
        
        self._add_vars_from_cols(var_by_col, obj, first_stage_cols, 1)
        self._add_vars_from_cols(var_by_col, obj, second_stage_cols, 2)
            
        self._add_constrs_from_rows(var_by_col, constr_by_row, first_stage_rows, 1)
        self._add_constrs_from_rows(var_by_col, constr_by_row, second_stage_rows, 2)
        
        print '\tGenerating Random Events'
        blocks = self._smps_reader.get_blocks()
        indeps = self._smps_reader.get_indeps()
        
        random_events = []
        for bl in blocks:
            realizations = []
            elements = bl.get_coef_elements()
            n_rea = bl.get_number_of_realizations()
            for i in xrange(n_rea):
                (prob, coefs) = bl.get_realization(i)
                cost_changes = [] 
                coefficient_changes = [] 
                rhs_changes = []
                for i, (col_name, row_name) in enumerate(elements):
                    col = self._smps_reader.get_column_by_name(col_name)
                    row = self._smps_reader.get_row_by_name(row_name)
                    var_id = var_by_col.get(col, None)
                    constr_id = constr_by_row.get(row, None)
                    if col_name == rhs_name: # rhs_change
                        rhs_changes.append((constr_id, coefs[i])) 
                    elif row_name == obj.get_name(): # cost change
                        cost_changes.append((var_id, coefs[i]))  
                    else: # coef change                    
                        coefficient_changes.append((var_id, constr_id, coefs[i])) 
                realizations.append((prob, cost_changes, coefficient_changes, rhs_changes))
            random_events.append(realizations)
        
        for indep in indeps:            
            col_name = indep.get_col_name()
            row_name = indep.get_row_name()
            col = self._smps_reader.get_column_by_name(col_name)
            row = self._smps_reader.get_row_by_name(row_name)
            var_id = var_by_col.get(col, None)
            constr_id = constr_by_row.get(row, None)
            
            if col_name == rhs_name: # rhs_change
                random_events.append([(prob, [], [], [(constr_id, coef)]) for prob, coef in indep.get_realizations()]) 
            elif row_name == obj.get_name(): # cost change
                random_events.append([(prob, [(var_id, coef)], [], []) for prob, coef in indep.get_realizations()])  
            else: # coef change
                random_events.append([(prob, [], [(var_id, constr_id, coef)], []) for prob, coef in indep.get_realizations()])
                
        print '\tGenerating Scenarios'
        print '\t',
        self._generate_scenarios(random_events, [], 1.0, [], [], [])        
        
        print '\n\tTotal Number of Scenarios: ', len(self._two_stage_problem.get_scenarios())
        print ''         
         
        return self._two_stage_problem 
    
    
    