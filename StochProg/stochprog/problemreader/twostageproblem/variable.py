

class VariableType(object):
    REAL, BINARY, INTEGER  = range(3)
    
    
class Variable(object):
    
    def __init__(self, id, name, stage, type=VariableType.REAL):
        self._id = id
        self._name = name
        self._type = type        
        self._stage = stage
        
        
    def get_id(self):
        return self._id
    
    
    def get_name(self):
        return self._name
        
    
    def get_type(self):
        return self._type


    def get_stage(self):
        return self._stage
    

    def is_first_stage(self):
        return self._stage == 1
    
    
    def is_second_stage(self):
        return self._stage == 2
    
    
    def __str__(self):
        return "id: %s, name: %s, cost: %f, stage: %d" % (self._id, self._name, self._cost, self._stage)
    