import casual.make.platform.selector as selector
class Configuration(object):

    def __init__(self, data):
        self.data = data

    def initialize(self, data):
        self.data = data

    def get(self, key):
        if key in self.data:
            return self.data[key]
        raise SystemError(f"{key} does not exist in configuration")

configuration = Configuration( selector.build_configuration())
