import os
import re
from pathlib import Path


OPERATOR_TEMPLATE = '''\
from voyager_sdk.


class {operator_name}:
    """Base operator class for the SDK"""

    def __init__(self, name):
        self.name = name
'''


class OperatorBootstrapper(object):

    @staticmethod
    def initialize(operator_name, base_dir):
        operator_file_name = OperatorBootstrapper.camel_to_snake(operator_name)
        operator_directory = os.path.join(base_dir, operator_file_name)
        Path(operator_directory).mkdir(parents=True, exist_ok=True)
        operator_file = os.path.join(operator_directory, f"{operator_file_name}.py")
        with open(operator_file, 'w', encoding='utf-8') as f:
            f.write(OPERATOR_TEMPLATE.format(operator_name))
        # initialize_config()

    @staticmethod
    def camel_to_snake(name):
        # Insert underscores before capital letters, then lowercase the whole string
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
