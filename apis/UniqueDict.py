class UniqueDict(dict):
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        if key in self._data:
            raise KeyError(f'Duplicate key: {key}')
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return repr(self._data)

    @classmethod
    def fromDict(cls, input_dict):
        instance = cls()
        for key, value in input_dict.items():
            instance[key] = value
        return instance