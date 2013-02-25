
class Period(object):
    
    def __init__(self, name, column_range, row_range):
        self._name = name
        self._column_range = column_range
        self._row_range = row_range
        
        
    def get_name(self):
        return self._name
        
        
    def get_column_range(self):
        return self._column_range
    
    
    def get_row_range(self):
        return self._row_range