import os
import json
from dataclasses import dataclass, field, fields, asdict
from exceptions.operator_exceptions import OperatorNotFoundException


class _ConfigSection(object):
    """
    Base for config.json sections. Known keys become attributes; unknown keys
    are kept in `extra` so they survive a load/dump round trip.
    """

    @classmethod
    def from_dict(cls, data):
        data = dict(data or {})
        known = {f.name for f in fields(cls) if f.name != "extra"}
        kwargs = {k: data.pop(k) for k in list(data) if k in known}
        return cls(**kwargs, extra=data)

    def to_dict(self):
        data = asdict(self)
        extra = data.pop("extra")
        return {**extra, **data}


@dataclass
class PipelineConfig(_ConfigSection):
    pipeline_id: str = None
    pipeline_name: str = None
    pipeline_link: str = None
    pipeline_version: str = None
    pipeline_entrypoint: str = None
    pipeline_format: str = None
    extra: dict = field(default_factory=dict, repr=False)


@dataclass
class OperatorConfig(_ConfigSection):
    operator_id: str = None
    operator_name: str = ""
    operator_version: str = ""
    class_name: str = None
    package_name: str = None
    args: list = field(default_factory=list)
    environment: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict, repr=False)


class OperatorConfiguration(object):

    def __init__(self, config, inputs):
        self.config = config
        self.pipeline = PipelineConfig.from_dict(config.get("pipeline"))
        self.input_schema = inputs
        self.operator = OperatorConfig.from_dict(config.get("operator"))

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

    @classmethod
    def load(cls, config_path):
        configuration_path = OperatorConfiguration.config_path()
        inputs_path = OperatorConfiguration.input_schema_path()
        if not os.path.exists(inputs_path) or not os.path.exists(configuration_path):
            raise OperatorNotFoundException(f"Operator configuration now found directory {configuration_path}")
        with open(configuration_path, "r") as f:
            config = json.load(f)
        with open(inputs_path, "r") as f:
            inputs = json.load(f)
        return cls(config, inputs)

    def dump(self, configuration_path=None):
        self.config["pipeline"] = self.pipeline.to_dict()
        self.config["operator"] = self.operator.to_dict()
        if not configuration_path:
            configuration_path = OperatorConfiguration.config_path()
        with open(configuration_path, "w") as f:
            json.dump(self.config, f, indent=4)
