
class Realization(object):
    
    def __init__(self, probability, cost_changes, coefficient_changes, rhs_changes):
        self._probability = probability
        self._cost_changes = cost_changes
        self._coefficient_changes = coefficient_changes
        self._rhs_changes = rhs_changes

    def get_probability(self):
        return self._probability


    def get_cost_changes(self):
        return self._cost_changes


    def get_coefficient_changes(self):
        return self._coefficient_changes


    def get_rhs_changes(self):
        return self._rhs_changes
