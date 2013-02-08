CORE_FILE_PATH = '../../instances/assets.cor'
TIME_FILE_PATH = '../../instances/assets.tim'
STOCH_FILE_PATH = '../../instances/assets.sto.small'


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
    

class Column(object):
    
    def __init__(self, id, name):
        self._id = id
        self._name = name
  
        
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
        
    def add_coef_to_column(self, column, coef):
        self._coefficients[column] = coef
        

class SMPSReader(object):
    
    def __init__(self, core_file_path, time_file_path, stoch_file_path):
        self._core_file_path = core_file_path
        self._time_file_path = time_file_path
        self._stoch_file_path = stoch_file_path
        self._name = ''
        self._rows = []
        self._columns = []
        self._column_by_name = {}
        self._row_by_name = {}
        self._obj = None
        
    

    def _read_name_section(self, core_file):
        line = core_file.readline()
        line_arr = line.split()
        if len(line_arr) < 2:
            raise FormatError('Name section missing', 'Less than 2 fields in first line of file')
        if line_arr[0] != 'NAME':
            raise FormatError('Name section missing', 'Wrong name of the section')
        name = line_arr[1]
        print 'NAME =', name
        self._name = name
        
        return line


    def _read_rows_section(self, core_file):
        line_arr = core_file.readline().split()
        if len(line_arr) < 1:
            raise FormatError('Rows section missing', 'Empty line')
        if line_arr[0] != 'ROWS':
            raise FormatError('Rows section missing', "Expecting ROWS section received %s" % line_arr[0])
        
        line = core_file.readline()
        line_arr = line.split()
        id = 0
        while len(line_arr) >= 2:
            type_name = line_arr[0]
            name = line_arr[1]
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
            line_arr = line.split()
        
        if self._obj is None:
            raise FormatError('Missing Objective Function', 'The file must have at least one ROW of type N, representing the objective function')
        
        return line
    
    def _read_columns_section(self, core_file, last_read_line):
        line_arr = last_read_line.split()
        if len(line_arr) < 1:
            raise FormatError('COLUMNS section missing', 'Empty line')
        section_name = line_arr[0]
        if section_name != 'COLUMNS':
            raise FormatError('COLUMNS section missing', "Expecting COLUMNS section received '%s'" % section_name)
        
        line = core_file.readline()
        line_arr = line.split()
        id = 0
        while len(line_arr) >= 3:
            column_name = line_arr[0]
            column = self._column_by_name.get(column_name, None)
            if column is None:
                column = Column(id, column_name)
                self._columns.append(column)
                self._column_by_name[column_name] = column
                print 'Column[', id, ']:', column_name
                id = id + 1
            
            for i in range(1, len(line_arr), 2):
                row_name = line_arr[i]
                coef = float(line_arr[i+1])
                print 'Coefficient of column', column_name, 'in row', row_name, '=', coef
                row = self._row_by_name.get(row_name, None)
                if row is None:
                    raise FormatError('Row not found', "Row %s was not found" % row_name)
                row.add_coef_to_column(column, coef)
            
            line = core_file.readline()
            line_arr = line.split()
        
        return line
    
    
    def _read_rhs_section(self, core_file, next_section):
        pass
    
    
    def _read_core_file(self):
        with open(self._core_file_path) as core_file:
            self._read_name_section(core_file)
            last_read_line = self._read_rows_section(core_file)
            last_read_line = self._read_columns_section(core_file, last_read_line)
            last_read_line = self._read_rhs_section(core_file, last_read_line)
    
    def _read_time_file(self):
        pass
    
    
    def _read_stoch_file(self):
        pass
    
    
    def read(self):
        self._read_core_file()
        self._read_time_file()
        self._read_stoch_file()


if __name__ == '__main__':
    try:
        smps_reader = SMPSReader(CORE_FILE_PATH, TIME_FILE_PATH, STOCH_FILE_PATH)
        smps_reader.read()
    except FormatError as  e:
        print e
    
    
    