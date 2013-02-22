from stochprog.problemreader.smpsreader.smpsreader import SMPSReader
from stochprog.problemreader.twostageproblem.twostageproblem import TwoStageProblem

class SmpsToTwoStageBuilder(object):
    
    def __init__(self, core_file_path, time_file_path, stoch_file_path):
        self._smps_reader = SMPSReader(core_file_path, time_file_path, stoch_file_path)
        self._two_stage_problem = TwoStageProblem()
        
        
    def build_two_stage_instance(self):
        print 'Loading SMPS Files'
        self._smps_reader.read()
        # TODO: Use the TwoStageProblem class interface to build an instance from smps_reader data
