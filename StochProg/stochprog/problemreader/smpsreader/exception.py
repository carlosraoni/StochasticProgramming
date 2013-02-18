
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
