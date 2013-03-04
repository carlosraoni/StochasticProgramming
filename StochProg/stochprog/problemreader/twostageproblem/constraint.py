
class ConstraintType(object):
    LT, LE, E, GE, GT, N = range(6)
    
    @staticmethod
    def get_constraint_type_by_name(type_name):
        return {'G': ConstraintType.GE,
                'L': ConstraintType.LE,
                'E': ConstraintType.E,
                'N': ConstraintType.N}.get(type_name, None)


class Constraint(object):
    
    def __init__(self, id, name, stage, type):
        self._id = id
        self._type = type
        self._name = name
        self._stage = stage
        
    
    def get_id(self):
        return self._id

    
    def get_type(self):
        return self._type
    
    
    def get_name(self):
        return self._name
    
    
    def get_stage(self):
        return self._stage
    

    def is_first_stage(self):
        return self._stage == 1 
    



