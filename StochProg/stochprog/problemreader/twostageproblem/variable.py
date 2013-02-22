

class VariableType(object):
    REAL, BINARY, INTEGER  = range(3)
    
    
class Variable(object):
    
    def __init__(self, id, name, cost, type, stage):
        self._id = id
        self._name = name
        self._type = type
        self._cost = cost
        self._stage = stage
        
        
    def get_id(self):
        return self._id
    
    
    def get_name(self):
        return self._name
    
    
    def get_cost(self):
        return self._cost
        
    
    def get_type(self):
        return self._type


    def get_stage(self):
        return self._stage
    
    
    def set_cost(self, cost):
        self._cost = cost
        

    def is_first_stage(self):
        return self._stage == 1
    
    
    def is_second_stage(self):
        return self._stage == 2