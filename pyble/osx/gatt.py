from objc import *

from pyble.gatt import Service, Characteristic, Descriptor
from util import CBUUID2String

import uuid
import logging
from pprint import pprint, pformat
import struct

logger = logging.getLogger(__name__)

class OSXBLEService(Service):
    def __init__(self, peripheral, instance):
        try:
            super().__init__()
        except:
            super(OSXBLEService, self).__init__()
        self.instance = instance
        uuidBytes = instance._.UUID._.data
        if len(uuidBytes) == 2:
            self.name = str(instance._.UUID)
            if self.name.startswith("Unknown"):
                self.name = "UNKNOWN"
            self.UUID = CBUUID2String(uuidBytes)
        elif len(uuidBytes) == 16:
            self.UUID = uuid.UUID(bytes=uuidBytes)
        else:
            # invalid UUID size
            pass
        self.isPrimary = (instance._.isPrimary == YES)
        # which peripheral own this service
        self.peripheral = peripheral

    @property
    def characteristicUUIDs(self):
        if len(self._characteristicUUIDs) == 0:
            self.peripheral.discoverCharacteristicsForService(self.instance)
            for characteristic in self.characteristics:
                self._characteristicUUIDs.append(characteristic.UUID)
        return self._characteristicUUIDs
 
    @characteristicUUIDs.setter
    def characteristicUUIDs(self, value):
        try:
            self._characteristicUUIDs = value[:]
        except:
            pass

    def __iter__(self):
        if len(self.characteristics) == 0:
            self.peripheral.discoverCharacteristicsForService(self.instance)
        return iter(self.characteristics)

    def show(self):
        print self
        for c in self.characteristics:
            print "  " + str(c)
            print "    Description: %s" % (str(c.description))
            print "    Value      : ", pformat(c.value)

    def findCharacteristicByInstance(self, instance):
        for c in self.characteristics:
            if str(c.UUID) == CBUUID2String(instance._.UUID._.data):
                return c
        return None

    def getCharacteristicByInstance(self, instance):
        for c in self.characteristics:
            if str(c.UUID) == CBUUID2String(instance._.UUID._.data):
                return c
        return None

class OSXBLECharacteristic(Characteristic):
    def __init__(self, service, instance):
        try:
            super().__init__()
        except:
            super(OSXBLECharacteristic, self).__init__()
        self.service = service
        uuidBytes = instance._.UUID._.data
        if len(uuidBytes) == 2:
            self.name = str(instance._.UUID)
            if self.name.startswith("Unknown"):
                self.name = "UNKNOWN"
            self.UUID = CBUUID2String(uuidBytes)
        elif len(uuidBytes) == 16:
            self.UUID = uuid.UUID(bytes=uuidBytes)
        else:
            # invalid UUID size
            pass

        self._description = ""
        self.properties = {
            "broadcast": False,                 # 0x0001
            "read": False,                      # 0x0002
            "writeWithoutResponse": False,      # 0x0004
            "write": False,                     # 0x0008
            "notify": False,                    # 0x0010
            "indicate": False,                  # 0x0020
            "authenticatedSignedWrites": False, # 0x0040
            "extendedProperties": False,        # 0x0080
            "notifyEncryptionRequired": False,  # 0x0100
            "indicateEncryptionRequired": False # 0x0200
        }

        # update basic info
        self.instance = instance

    # callbacks
    def _update_userdescription(self, description):
        self._description = description

    def _update_value(self, value):
        self.value = value

    def addDescriptor(self, descriptor):
        if descriptor not in self.descriptors:
            self.descriptors.append(descriptor)
            if descriptor.UUID == "2901": # user description descriptor
                descriptor.setDescriptorUserDescriptionCallback(self._update_userdescription)

    def findDescriptorByInstance(self, instance):
        for d in self.descriptors:
            if str(d.UUID) == CBUUID2String(instance._.UUID._.data):
                return d
        return None

    def showProperties(self):
        print "%s:%s:%s properties" % (self.service.peripheral, self.service, self)
        pprint(self.properties)

    def showDescriptors(self):
        print "%s:%s:%s descriptors" % (self.service.peripheral, self.service, self)
        for d in self.descriptors:
            print "\t%s: " % d, d.value

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        self._instance = value
        # update properties
        if value._.properties:
            self.updateProperties(int(value._.properties))

    @property
    def value(self):
        if self._value == None and self.properties["read"]:
            self.service.peripheral.readValueForCharacteristic(self.instance)
        return self._value

    @value.setter
    def value(self, data):
        self._value = data
        # notify callback

    @property
    def description(self):
        if len(self._description) == 0:
            if len(self.descriptors) == 0:
                self.service.peripheral.discoverDescriptorsForCharacteristic(self.instance)
        d = None
        for descriptor in self.descriptors:
            if descriptor.UUID == "2901":
                d = descriptor
                break
        if d:
            self._description = d.value
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def updateProperties(self, properties):
        for key in self.properties:
            self.properties[key] = False
        if properties & 0x0001:
            self.properties["broadcast"] = True
        if properties & 0x0002:
            self.properties["read"] = True
        if properties & 0x0004:
            self.properties["writeWithoutResponse"] = True
        if properties & 0x0008:
            self.properties["write"] = True
        if properties & 0x0010:
            self.properties["notify"] = True
        if properties & 0x0020:
            self.properties["indicate"] = True
        if properties & 0x0040:
            self.properties["authenticatedSignedWrites"] = True
        if properties & 0x0080:
            self.properties["extendedProperties"] = True
        if properties & 0x0100:
            self.properties["notifyEncryptionRequired"] = True
        if properties & 0x0200:
            self.properties["indicateEncryptionRequired"] = True

class OSXBLEDescriptor(Descriptor):
    def __init__(self, characteristic, instance):
        try:
            super().__init__()
        except:
            super(OSXBLEDescriptor, self).__init__()
        self.instance = instance
        uuidBytes = instance._.UUID._.data
        if len(uuidBytes) == 2:
            self.name = str(instance._.UUID)
            if self.name.startswith("Unknown"):
                self.name = "UNKNOWN"
            self.UUID = CBUUID2String(uuidBytes)
        elif len(uuidBytes) == 16:
            self.UUID = uuid.UUID(bytes=uuidBytes)
        else:
            # invalid UUID size
            pass
        self.characteristic = characteristic
        self._value = None

        # callback
        self.update_userdescription = None

    # register callbacks
    def setDescriptorUserDescriptionCallback(self, func):
        self.update_userdescription = func

    @property
    def value(self):
        if self._value == None:
            self.characteristic.service.peripheral.readValueForDescriptor(self.instance)
        return self._value

    @value.setter
    def value(self, data):
        # base on UUID to convert data
        if self.UUID == "2900":     # Characteristic Extended Properties
            self._value = struct.unpack(">h", data)[0]
        elif self.UUID == "2901":   # Characteristic User Description
            self._value = str(data)
            if self.update_userdescription:
                self.update_userdescription(self._value)
        elif self.UUID == "2902":   # Client Characteristic Configuration
            self._value = struct.unpack(">H", data)[0]
        elif self.UUID == "2903":   # Client Characteristic Configuration
            self._value = data
        elif self.UUID == "2904":   # Characteristic Presentation Format
            self._value = data
        elif self.UUID == "2905":   # Characteristic Aggregate Format
            self._value = data
        elif self.UUID == "2906":   # Valid Range
            self._value = data
        elif self.UUID == "2907":   # External Report Reference
            self._value = data
        elif self.UUID == "2908":   # Report Regerence
            self._value = data
        else:
            # invalid descriptor
            pass

    def __repr__(self):
        identifier = ""
        if isinstance(self.UUID, type("")):
            identifier = self.UUID
        else:
            identifier = str(self.UUID).upper()
        return "Descriptor{%s <%s>}" % (self.name, identifier)

    def __str__(self):
        return self.__repr__()


