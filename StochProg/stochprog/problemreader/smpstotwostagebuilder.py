from sets import Set

from stochprog.problemreader.smpsreader.smpsreader import SMPSReader
from stochprog.problemreader.twostageproblem.twostageproblem import TwoStageProblem

class SmpsToTwoStageBuilder(object):
    
    def __init__(self, core_file_path, time_file_path, stoch_file_path):
        self._smps_reader = SMPSReader(core_file_path, time_file_path, stoch_file_path)
        self._two_stage_problem = TwoStageProblem()
                

    def add_vars_from_cols(self, var_by_col, obj, cols, stage):
        for col in cols:
            cost = obj.get_coef_of_column(col)
            var_id = self._two_stage_problem.add_root_variable(col.get_name(), cost, stage)
            var_by_col[col] = var_id
        
        
    def add_constrs_from_rows(self, var_by_col, constr_by_row, rows, stage):
        for row in rows:
            vars_and_coefs = [(var_by_col[col], coef) for col, coef in row.get_columns_and_coefs()]
            constr_id = self._two_stage_problem.add_root_constraint(row.get_name(), row.get_type(), vars_and_coefs, row.get_rhs(), stage)
            constr_by_row[row] = constr_id        


    def build_two_stage_instance(self):
        print 'Loading SMPS Files'
        self._smps_reader.read()
        
        # TODO: Use the TwoStageProblem class interface to build an instance from smps_reader data
        var_by_col = {}
        constr_by_row = {}
        
        obj = self._smps_reader.get_objective_function()
        
        first_stage_cols = Set(self._smps_reader.get_columns_of_stage(1))
        second_stage_cols = Set(self._smps_reader.get_columns_of_stage(2))
        first_stage_rows = Set(self._smps_reader.get_rows_of_stage(1))
        second_stage_rows = Set(self._smps_reader.get_rows_of_stage(2))
        
        self.add_vars_from_cols(var_by_col, obj, first_stage_cols, 1)
        self.add_vars_from_cols(var_by_col, obj, second_stage_cols, 2)
            
        self.add_constrs_from_rows(var_by_col, constr_by_row, first_stage_rows, 1)
        self.add_constrs_from_rows(var_by_col, constr_by_row, second_stage_rows, 2)


            
        
            