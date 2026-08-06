from  abc import ABC, abstractmethod

class People(ABC):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def dni(self):
        return self.dni

    @dni.setter
    def dni(self, value):
        if type(value)==int and value > 1000000 and value < 99999999:
            self.dni = value

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        if type(value)==str and len(value) > 2 and value!= "":
            self.name = value

    @property
    def age(self):
        return self.age

    @age.setter
    def age(self, value):
        if type(value)==int and value > 0:
            self.age = value