from stochprog.problemreader.smpsreader.exception import FormatError

class Block(object):
    
    def __init__(self, name, period):
        self._name = name
        self._period = period
        self._coef_elements = [] # array of tuples of column row associations
        self._coef_realizations = [] # array of realizations of coefficients of elements of coef_elements
        self._realization_prob = [] # probability of each realization
        
    def get_name(self):
        return self._name
    
    def get_period(self):
        return self._period
    
    def get_coef_elements(self):
        return self._coef_elements
    
    def set_coef_elements(self, coef_elements):
        self._coef_elements = coef_elements
        
    def get_realizations(self):
        return self._coef_realizations
        
    def add_realization(self, elements, prob, realization):
        if elements != self._coef_elements:
            raise FormatError('Wrong block specification', 'Elements of realization different from original block elements or in different order')
        self._coef_realizations.append(realization)
        self._realization_prob.append(prob)
    
    def get_realization_probabilities(self): 
        return self._realization_prob
        
    def __str__(self):
        result = "BLOCK %s (%s)\n" % (self._name, self._period)
        result += "Realizations: %d\n" % len(self._coef_realizations)
        result += "Probabilities: %s\n" % self._realization_prob
        for i, ele in enumerate(self._coef_elements):
            result += "(%s, %s) =" % (ele[0], ele[1])
            for rea in self._coef_realizations:
                result += " %.2f" % rea[i]
            result += '\n'
        return result   
