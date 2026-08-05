from  abc import ABC, abstractmethod

class People(ABC):
    def __init__(self, name, age):
        self.name = name
        self.age = age