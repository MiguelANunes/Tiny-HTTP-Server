from enum import Enum
class AcceptedMethods(Enum):
    GET  = "GET"
    HEAD = "HEAD"

    def __str__(self):
        return self.value

    def as_list(self):
	    return [str(self.value)]
