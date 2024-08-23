from .base_model import Model

class Dummy(Model):
    def __init__(self, **kwargs):
        super(Dummy, self).__init__(**kwargs)
        self.model = self.build_model()

    def build_model(self):
        pass

    def predict(self, input):
        annotations = [
            {
                "id": "ENDOSPERM",
                "bbox": [0, 0, 100, 100],
                "mask": [[0, 0], [0, 100], [100, 100], [100, 0]]
            }
        ]
        return annotations