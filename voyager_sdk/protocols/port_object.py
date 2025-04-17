from enum import IntEnum


class PortType(IntEnum):
    INPUT = 0
    OUTPUT = 1


class PortObject(object):
    def __init__(
        self, run_id, name, port_type, schema, secondary_files, db_value, value, files, port_id=None, notify=False
    ):
        self.run_id = run_id
        self.name = name
        self.port_type = port_type
        self.schema = schema
        self.secondary_files = secondary_files
        self.db_value = db_value
        self.value = value
        self.files = files
        self.port_id = port_id
        self.port_object = None
        self.notify = notify

    @classmethod
    def from_definition(cls, run_id, value, port_type, port_values, notify=False):
        pass

    def ready(self):
        pass

    def complete(self, value, group, job_group_notifier, output_metadata={}):
        pass

    @classmethod
    def from_db(cls, port_id):
        pass

    def to_db(self):
        pass

    def __repr__(self):
        return "(PORT) %s: Name: %s Type: %s" % (self.port_object.id, self.name, PortType(self.port_type).name)
