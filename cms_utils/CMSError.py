class CMSError(Exception):
    pass


class InvalidTimeseriesCMSError(CMSError):
    def __init__(self, message):
        self.message = message


class InvalidInterpolateStrategyCMSError(CMSError):
    def __init__(self, message):
        self.message = message
