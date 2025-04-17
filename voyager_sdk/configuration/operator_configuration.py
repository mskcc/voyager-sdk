import os
import json


class OperatorConfiguration(object):

    def __init__(self, config, inputs):
        self.config = config
        self.pipeline = config.get("pipeline")
        self.input_schema = inputs
        self.operator = config.get("operator")
        print(self.operator)

    @staticmethod
    def config_path(directory):
        config_dir = os.path.join(directory, ".voyager")
        config_file = os.path.join(config_dir, "config.json")
        return config_file

    @staticmethod
    def input_schema_path(directory):
        input_schema_dir = os.path.join(directory, ".voyager")
        input_schema_file = os.path.join(input_schema_dir, "inputs.json")
        return input_schema_file

    @classmethod
    def load(cls, directory):
        configuration_path = OperatorConfiguration.config_path(directory)
        with open(configuration_path, "r") as f:
            config = json.load(f)
        inputs_path = OperatorConfiguration.input_schema_path(directory)
        with open(inputs_path, "r") as f:
            inputs = json.load(f)
        return cls(config, inputs)

    def dump(self, directory):
        configuration_path = OperatorConfiguration.config_path(directory)
        with open(configuration_path, "w") as f:
            json.dump(self.config, f)

