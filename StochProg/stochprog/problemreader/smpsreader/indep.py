
class Indep(object):
    
    def __init__(self, col_name, row_name, period):
        self._col_name = col_name
        self._row_name = row_name
        self._period = period
        self._realizations = [] # array of realizations of coefficients of elements of coef_elements
      
    def get_col_name(self):
        return self._col_name
    
    
    def get_row_name(self):
        return self._row_name
    
        
    def add_realization(self, prob, value):
        self._realizations.append((prob, value))
      
      
    def get_number_of_realizations(self):
        return len(self._realizations)


    def get_realization(self, index):
        return self._realization_prob[index]
    
    
    def get_realizations(self):
        return self._realizations 
    
        
    def __str__(self):
        result = "INDEP (%s,%s) (%s)\n" % (self._col_name, self._row_name, self._period)
        result += "Realizations: %d\n" % len(self._realizations)
        result += "(%s, %s) = %s\n" % (self._col_name, self._row_name, self._realizations)
        return result