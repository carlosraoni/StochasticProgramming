

class RowType(object):
    LT, LE, E, GE, GT, N = range(6)
    
    @staticmethod
    def type_name_to_row_type(type_name):
        return {'G': RowType.GE,
                'L': RowType.LE,
                'E': RowType.E,
                'N': RowType.N}.get(type_name, None)

class Row(object):
    
    def __init__(self, id, name, type):
        self._id = id
        self._name = name
        self._type = type
        
        self._coefficients = {}
        self._rhs = 0
        self._rhs_name = ''
        
    def get_id(self):
        return self._id
        
    def add_coef_to_column(self, column, coef):
        self._coefficients[column] = coef
        
    def set_rhs(self, rhs_name, coef):
        self._rhs_name = rhs_name
        self._rhs = coef
