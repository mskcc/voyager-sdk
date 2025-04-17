import os
import json


class OperatorConfiguration(object):

    def __init__(self, pipeline):
        self.pipeline = pipeline

    @staticmethod
    def initialize_operator(operator_name, github_link, github_version):
        pass
        # _create_configuration_directory()
        # _clone_pipeline()
        # _dump_config_file()

    @staticmethod
    def config_path(self):
        cwd = os.getcwd()
        config_dir = os.path.join(cwd, ".voyager")
        config_file = os.path.join(config_dir, ".config.json")
        return config_file

    @classmethod
    def load(cls):
        configuration_path = OperatorConfiguration.config_path()
        with open(configuration_path, "r") as f:
            data = json.load(f)
        data["pipeline"]
