from typing import Set
from json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Set):
            return list(o)
        return o.__dict__
