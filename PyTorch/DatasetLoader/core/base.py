class DatasetLoader:
    def __init__(self, domain: str, name: str, **kwargs):
        self.domain = domain
        self.name = name
        self.kwargs = kwargs

    def load(self):
        raise NotImplementedError("Subclasses must implement this method")
