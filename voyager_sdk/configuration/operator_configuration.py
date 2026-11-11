import os
import json
from exceptions.operator_exceptions import OperatorNotFoundException


class OperatorConfiguration(object):

    def __init__(self, config, inputs, outputs=None):
        self.config = config
        self.pipeline = config.get("pipeline")
        self.input_schema = inputs
        self.output_schema = outputs or []
        self.operator = config.get("operator")
        print(self.operator)

    @staticmethod
    def config_path(directory=os.getcwd()):
        config_dir = os.path.join(directory, ".voyager")
        config_file = os.path.join(config_dir, "config.json")
        return config_file

    @staticmethod
    def input_schema_path(directory=os.getcwd()):
        input_schema_dir = os.path.join(directory, ".voyager")
        input_schema_file = os.path.join(input_schema_dir, "inputs.json")
        return input_schema_file

    @staticmethod
    def output_schema_path(directory=os.getcwd()):
        return os.path.join(directory, ".voyager", "outputs.json")

    @classmethod
    def load(cls):
        configuration_path = OperatorConfiguration.config_path()
        inputs_path = OperatorConfiguration.input_schema_path()
        if not os.path.exists(inputs_path) or not os.path.exists(configuration_path):
            raise OperatorNotFoundException(f"Operator configuration now found directory {configuration_path}")
        with open(configuration_path, "r") as f:
            config = json.load(f)
        with open(inputs_path, "r") as f:
            inputs = json.load(f)
        outputs = []
        outputs_path = OperatorConfiguration.output_schema_path()
        if os.path.exists(outputs_path):
            with open(outputs_path, "r") as f:
                outputs = json.load(f)
        return cls(config, inputs, outputs)

    def dump(self):
        configuration_path = OperatorConfiguration.config_path()
        with open(configuration_path, "w") as f:
            json.dump(self.config, f)
