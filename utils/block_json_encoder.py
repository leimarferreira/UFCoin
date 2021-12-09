from json import JSONEncoder


class BlockJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
