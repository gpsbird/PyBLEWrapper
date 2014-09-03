#!/usr/bin/env python
import logging
import pkgutil
import profile
from patterns import LoggerObject

logger = logging.getLogger(__name__)

class Service(LoggerObject):
    def __init__(self):
        self.name = "UNKNOWN"
        self.UUID = ""
        self.isPrimary = False
        self.characteristics = []
        self._characteristicUUIDs = []

    @property
    def characteristicUUIDs(self):
        if len(self._characteristicUUIDs) == 0:
            for characteristic in self.characteristics:
                self._characteristicUUIDs.append(characteristic.UUID)
        return self._characteristicUUIDs

    @characteristicUUIDs.setter
    def characteristicUUIDs(self, value):
        try:
            self._characteristicUUIDs = value[:]
        except:
            pass

    def addCharacteristic(self, characteristic):
        if characteristic not in self.characteristics:
            self.characteristics.append(characteristic)

    def removeCharacteristic(self, characteristic):
        if characteristic not in self.characteristics:
            self.characteristics.remove(characteristic)

    def __getitem__(self, key):
        if key.upper() in self.characteristicUUIDs:
            for characteristic in self.characteristics:
                if characteristic.UUID == key.upper():
                    return characteristic
        raise KeyError

    def __iter__(self):
        return iter(self.characteristics)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (other.UUID == self.UUID)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        identifier = ""
        if isinstance(self.UUID, type("")):
            identifier = self.UUID
        else:
            identifier = str(self.UUID).upper()
        string = "Service{%s <%s>}" % (self.name, identifier)
        if self.isPrimary:
            string = "*" + string
        return string

    def __str__(self):
        return self.__repr__()

class Profile(Service):
    pass

class Characteristic(LoggerObject):
    def __init__(self):
        self.name = "UNKNOWN"
        self.UUID = ""
        self.descriptors = []
        self.description = ""
        self.isNotifying = False
        self.isBroadcasted = False
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, data):
        self._value = data

    def addDescriptor(self, descriptor):
        if descriptor not in self.descriptors:
            self.descriptors.append(descriptor)

    def removeDescriptor(self, descriptor):
        if descriptor in self.descriptors:
            self.descriptors.remove(descriptor)
    
    def __repr__(self):
        identifier = ""
        if isinstance(self.UUID, type("")):
            identifier = self.UUID
        else:
            identifier = str(self.UUID).upper()
        return "Characteristic{%s <%s>}" % (self.name, identifier)

    def __str__(self):
        return self.__repr__()

class Descriptor(LoggerObject):
    def __init__(self):
        self.name = "UNKNOWN"
        self.UUID = ""
        self.value = None

    def __repr__(self):
        identifier = ""
        if isinstance(self.UUID, type("")):
            identifier = self.UUID
        else:
            identifier = str(self.UUID).upper()
        return "Descriptor{%s <%s>}" % (self.name, identifier)

def load_profiles():
    # load default profiles
    package = profile
    for importer, name, isPkg in pkgutil.walk_packages(
        path = package.__path__,
        prefix = package.__name__+".",
        onerror = lambda x: None):
        print(name)
    # load cutomized profiles

