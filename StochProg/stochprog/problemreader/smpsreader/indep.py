
class Indep(object):
    
    def __init__(self, col_name, row_name, period):
        self._col_name = col_name
        self._row_name = row_name
        self._period = period
        self._realizations = [] # array of realizations of coefficients of elements of coef_elements
        self._realization_prob = [] # probability of each realization
        
    def add_realization(self, prob, value):
        self._realizations.append(value)
        self._realization_prob.append(prob)
        
    def __str__(self):
        result = "INDEP (%s,%s) (%s)\n" % (self._col_name, self._row_name, self._period)
        result += "Realizations: %d\n" % len(self._realizations)
        result += "Probabilities: %s\n" % self._realization_prob
        result += "(%s, %s) = %s\n" % (self._col_name, self._row_name, self._realizations)
        return result