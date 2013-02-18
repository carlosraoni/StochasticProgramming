from sets import Set

#CORE_FILE_PATH = '../../instances/assets.cor'
#TIME_FILE_PATH = '../../instances/assets.tim'
#STOCH_FILE_PATH = '../../instances/assets.sto.small'

CORE_FILE_PATH = '../../instances/env.cor'
TIME_FILE_PATH = '../../instances/env.tim'
STOCH_FILE_PATH = '../../instances/env.sto.1200'

_STOCH_FILE_SECTION_NAMES = Set(['STOCH',
                                 'SIMPLE',
                                 'ROBUST',
                                 'PLINQUAD',
                                 'CHANCE',
                                 'ICC',
                                 'SCENARIOS',
                                 'NODES',
                                 'INDEP',
                                 'BLOCKS',
                                 'DISTRIB',
                                 'ENDATA'])

class Error(Exception):
    
    def __init__(self, msg):
        self._message = msg
        
    def __str__(self):
        return "[ERROR] %s\n" % str(self._message)
        

class FormatError(Error):
    
    def __init__(self, msg, reason = None):
        self._message = msg
        self._reason = reason
        
    def __str__(self):
        ret = "[FORMAT_ERROR] %s\n" % str(self._message)
        if(self._reason != None):
            ret += "[REASON] %s\n" % str(self._reason)
        return ret


class WrongFileError(Error):
    
    def __init__(self, msg, reason = None):
        self._message = msg
        self._reason = reason
        
    def __str__(self):
        ret = "[WRONG_FILE_ERROR] %s\n" % str(self._message)
        if(self._reason != None):
            ret += "[REASON] %s\n" % str(self._reason)
        return ret


class NotSupportedError(Error):
    
    def __init__(self, msg, reason = None):
        self._message = msg
        self._reason = reason
        
    def __str__(self):
        ret = "[NOT_SUPPORTED_ERROR] %s\n" % str(self._message)
        if(self._reason != None):
            ret += "[REASON] %s\n" % str(self._reason)
        return ret
        

class Column(object):
    
    def __init__(self, id, name):
        self._id = id
        self._name = name
        
    def get_id(self):
        return self._id
    
    def get_name(self):
        return self._name
  
        
class RowType(object):
    LT, LE, E, GE, GT, N = range(6)


def _type_name_to_row_type(type_name):
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


class SMPSReader(object):
    
    def __init__(self, core_file_path, time_file_path, stoch_file_path):
        self._core_file_path = core_file_path
        self._time_file_path = time_file_path
        self._stoch_file_path = stoch_file_path
        self._name = ''
        self._rhs_name = 'RHS'
        self._rows = []
        self._columns = []
        self._column_by_name = {}
        self._row_by_name = {}
        self._obj = None
        self._periods = []
        self._blocks = []
        self._blocks_by_name = {}
        self._indeps = []
        self._indeps_by_col_row = {}        
    

    def _read_name_section(self, core_file):
        line = core_file.readline()
        fields = line.split()
        if len(fields) < 2:
            raise FormatError('Name section missing', 'Less than 2 fields in first line of file')
        if fields[0] != 'NAME':
            raise FormatError('Name section missing', 'Wrong name of the section')
        name = fields[1]
        print 'NAME =', name
        self._name = name
        
        return line


    def _read_rows_section(self, core_file):
        fields = core_file.readline().split()
        if len(fields) < 1:
            raise FormatError('Rows section missing', 'Empty line')
        if fields[0] != 'ROWS':
            raise FormatError('Rows section missing', "Expecting ROWS section received %s" % fields[0])
        
        line = core_file.readline()
        fields = line.split()
        id = 0
        while len(fields) >= 2:
            type_name = fields[0]
            name = fields[1]
            type = _type_name_to_row_type(type_name)
            if type is None:
                raise FormatError('Wrong type name', "Invalid Type: %s" % type_name)
            row = Row(id, name, type)
            if type == RowType.N and self._obj is None:
                print 'Objective Function =', name
                self._obj = row
            self._rows.append(row)
            self._row_by_name[name] = row
            print 'Row[',id, ']:', type_name, name
            id = id + 1
            line = core_file.readline()
            fields = line.split()
        
        if self._obj is None:
            raise FormatError('Missing Objective Function', 'The file must have at least one ROW of type N, representing the objective function')
        
        return line
    
    def _read_columns_section(self, core_file, last_read_line):
        fields = last_read_line.split()
        if len(fields) < 1:
            raise FormatError('COLUMNS section missing', 'Empty line')
        section_name = fields[0]
        if section_name != 'COLUMNS':
            raise FormatError('COLUMNS section missing', "Expecting COLUMNS section received '%s'" % section_name)
        
        line = core_file.readline()
        fields = line.split()
        id = 0
        while len(fields) >= 3:
            column_name = fields[0]
            column = self._column_by_name.get(column_name, None)
            if column is None:
                column = Column(id, column_name)
                self._columns.append(column)
                self._column_by_name[column_name] = column
                print 'Column[', id, ']:', column_name
                id = id + 1
            
            for i in range(1, len(fields), 2):
                row_name = fields[i]
                coef = float(fields[i+1])
                print 'Coefficient of column', column_name, 'in row', row_name, '=', coef
                row = self._row_by_name.get(row_name, None)
                if row is None:
                    raise FormatError('Row not found', "Row %s was not found" % row_name)
                row.add_coef_to_column(column, coef)
            
            line = core_file.readline()
            fields = line.split()
        
        return line
    
    
    def _read_rhs_section(self, core_file, last_read_line):
        fields = last_read_line.split()
        rhs_name = 'RHS'
        if len(fields) > 1:
            rhs_name = fields[1]
        print 'RHS Name = ', rhs_name
        self._rhs_name = rhs_name
        
        line = core_file.readline()
        fields = line.split()
        while len(fields) >= 3:
            rhs_name = fields[0]
            for i in range(1, len(fields), 2):
                row_name = fields[i]
                coef = float(fields[i+1])
                print 'Coefficient of rhs', rhs_name, 'in row', row_name, '=', coef
                row = self._row_by_name.get(row_name, None)
                if row is None:
                    raise FormatError('Row not found', "Row %s was not found" % row_name)
                row.set_rhs(rhs_name, coef)
            
            line = core_file.readline()
            fields = line.split()
        
        return line
    
    
    def _read_core_file(self):
        with open(self._core_file_path) as core_file:
            self._read_name_section(core_file)
            last_read_line = self._read_rows_section(core_file)
            last_read_line = self._read_columns_section(core_file, last_read_line)
            if last_read_line.startswith('RHS'):
                last_read_line = self._read_rhs_section(core_file, last_read_line)
            if not last_read_line.startswith('ENDATA'):
                print 'Ignoring next sections. SMPSReader does not support the additional optional sections'
    
    
    def _read_time_section(self, time_file):
        line = time_file.readline()
        fields = line.split()
        if len(fields) < 2:
            raise FormatError('Time section missing', 'Less than 2 fields in first line of file')
        if fields[0] != 'TIME':
            raise FormatError('Time section missing', 'Wrong name of the section')
        instance_name = fields[1]
        print 'TIME =', instance_name
        if instance_name != self._name:
            raise WrongFileError('Time file for different problem instance', "Core file describes problem %s, while time file describes problem %s" % (self._name, instance_name))
        
        return line
    
    
    def _read_periods_section(self, time_file):
        fields = time_file.readline().split()
        if len(fields) < 1:
            raise FormatError('Periods section missing', 'Empty line')
        if fields[0] != 'PERIODS':
            raise FormatError('Periods section missing', "Expecting PERIODS section received %s" % fields[0])
        if len(fields) > 1 and fields[1] != 'IMPLICIT':
            raise NotSupportedError('Time section type not supported', "SMPSReader only support IMPLICIT time section, received %s" % fields[1])
        
        line = time_file.readline()
        fields = line.split()
        
        period_names = []
        row_indexes = []
        column_indexes = []
        while len(fields) >= 3:
            column_name = fields[0]
            row_name = fields[1]
            period_name = fields[2]
            
            column = self._column_by_name.get(column_name, None)
            if column is None:
                raise FormatError('Column not found', "Column %s was not found" % column_name)
            row = self._row_by_name.get(row_name, None)
            if row is None:
                raise FormatError('Row not found', "Row %s was not found" % row_name)
            
            period_names.append(period_name)
            column_indexes.append(column.get_id())
            row_indexes.append(row.get_id())
            print 'Reading period col/row begins [', period_name, column_name, row_name, ']'
            
            line = time_file.readline()
            fields = line.split()
        
        n_periods = len(period_names)
        for i in range(n_periods - 1):
            column_range = (column_indexes[i], column_indexes[i+1])
            row_range = (row_indexes[i], row_indexes[i+1])
            period = Period(period_names[i], column_range, row_range)
            self._periods.append(period)
        column_range = (column_indexes[n_periods - 1], len(self._columns))
        row_range = (row_indexes[n_periods - 1], len(self._rows))
        period = Period(period_names[n_periods - 1], column_range, row_range)
        self._periods.append(period)
        
        for p in self._periods:
            column_range = p.get_column_range()
            row_range = p.get_row_range()
            print 'Period', p.get_name(), '= col ', column_range, ', row', row_range 
        
        return line
    
    def _read_time_file(self):
        with open(self._time_file_path) as time_file:
            self._read_time_section(time_file)
            last_read_line = self._read_periods_section(time_file)
            if not last_read_line.startswith('ENDATA'):
                print 'Ignoring next sections of time file. SMPSReader does not support the additional optional sections'
                
                            
    def _read_stoch_section(self, stoch_file):
        line = stoch_file.readline()
        fields = line.split()
        if len(fields) < 2:
            raise FormatError('Stoch section missing', 'Less than 2 fields in first line of file')
        if fields[0] != 'STOCH':
            raise FormatError('Stoch section missing', 'Wrong name of the section')
        instance_name = fields[1]
        print 'STOCH =', instance_name
        if instance_name != self._name:
            raise WrongFileError('Stoch file for different problem instance', "Core file describes problem %s, while stoch file describes problem %s" % (self._name, instance_name))
        
        line = stoch_file.readline()
        return line
    
    
    def _read_indep_section(self, stoch_file, last_read_line):
        fields = last_read_line.split()
        if len(fields) > 1 and fields[1] != 'DISCRETE':
            raise NotSupportedError('INDEP section type not supported', "SMPSReader only support DISCRETE INDEP section, received %s" % fields[1])
        
        line = stoch_file.readline()
        fields = line.split()
        while fields[0] not in _STOCH_FILE_SECTION_NAMES:
            col_name = fields[0]
            row_name = fields[1]
            
            column = self._column_by_name.get(col_name, None)
            if column is None and col_name != self._rhs_name:
                raise FormatError('Column not found', "Column '%s' was not found" % col_name)
            row = self._row_by_name.get(row_name, None)
            if row is None:
                raise FormatError('Row not found', "Row %s was not found" % row_name)
            
            value = float(fields[2])
            if len(fields) == 5:
                period = fields[3]
                prob = float(fields[4])
            else:
                prob = float(fields[3])
            
            indep = self._indeps_by_col_row.get((col_name, row_name), None)
            if indep is None:
                indep = Indep(col_name, row_name, period)
                self._indeps.append(indep)
                self._indeps_by_col_row[(col_name, row_name)] = indep
            indep.add_realization(prob, value)
            
            line = stoch_file.readline()      
            fields = line.split()
        
        return line
    
    
    def _read_block(self, stoch_file, line):
        fields = line.split()
        if len(fields) < 4:
            raise FormatError('Missing information in block header', 'BLOCK header BL must have at least 4 fields')
        name = fields[1]
        period = fields[2]
        prob = float(fields[3])
        elements = []
        realization = []
        
        line = stoch_file.readline()
        fields = line.split()
        while fields[0] not in _STOCH_FILE_SECTION_NAMES and fields[0] != 'BL':
            column_name = fields[0]
            column = self._column_by_name.get(column_name, None)
            if column is None and column_name != self._rhs_name:
                raise FormatError('Column not found', "Column '%s' was not found" % column_name)
            for i in range(1, len(fields), 2):
                row_name = fields[i]
                coef = float(fields[i+1])
                row = self._row_by_name.get(row_name, None)
                if row is None:
                    raise FormatError('Row not found', "Row %s was not found" % row_name)
                elements.append((column_name, row_name))
                realization.append(coef)
            line = stoch_file.readline()
            fields = line.split()
            
        return (name, period, elements, prob, realization, line) 
    
    def _read_blocks_section(self, stoch_file, last_read_line):
        fields = last_read_line.split()
        if len(fields) > 1 and fields[1] != 'DISCRETE':
            raise NotSupportedError('BLOCKS section type not supported', "SMPSReader only support DISCRETE BLOCKS section, received %s" % fields[1])
        
        line = stoch_file.readline()
        fields = line.split()
        while fields[0] == 'BL':
            (name, period, elements, prob, realization, line) = self._read_block(stoch_file, line)
            block = self._blocks_by_name.get(name, None)
            if block is None:
                block = Block(name, period)
                block.set_coef_elements(elements)
                self._blocks.append(block)
                self._blocks_by_name[name] = block
            block.add_realization(elements, prob, realization)
                
            fields = line.split()
        
        return line
    
    def _read_stoch_file(self):
        with open(self._stoch_file_path) as stoch_file:
            last_read_line = self._read_stoch_section(stoch_file)
            if last_read_line.startswith('INDEP'):
                last_read_line = self._read_indep_section(stoch_file, last_read_line)
                for i in self._indeps:
                    print i
            if last_read_line.startswith('BLOCKS'):
                last_read_line = self._read_blocks_section(stoch_file, last_read_line)
                for b in self._blocks:
                    print b
            if not last_read_line.startswith('ENDATA'):
                print 'Ignoring next sections of time file. SMPSReader does not support the additional optional sections'
    
    
    def read(self):
        self._read_core_file()
        self._read_time_file()
        self._read_stoch_file()


if __name__ == '__main__':
    try:
        smps_reader = SMPSReader(CORE_FILE_PATH, TIME_FILE_PATH, STOCH_FILE_PATH)
        smps_reader.read()
    #except FormatError as  e:
    #    print e
    except NotSupportedError as e:
        print e
    except WrongFileError as e:
        print e
    
    
    