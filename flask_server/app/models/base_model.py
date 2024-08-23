from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def build_model(self):
        pass

    @abstractmethod
    def predict(self, x):
        pass