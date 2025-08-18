import os
import re
import json
import shutil
from pathlib import Path
from string import Template
from importlib.resources import files, as_file
from voyager_sdk.configuration import OperatorConfiguration
from voyager_sdk.protocols.pipeline_cache import PipelineCache


OPERATOR_TEMPLATE = Template('''\
from voyager_sdk.operator.operator import Operator
from voyager_sdk.file_repository import FileRepository
from voyager_sdk.protocols.processors.file_processor import FileProcessor


class $operator_name:
    """Base operator class for the SDK"""

    def __init__(
            self,
            request_id=None,
            runs=[],
            pipeline=None,
            pairing=None,
            output_directory_prefix=None,
            file_group=None,
            job_group_id=None,
            job_group_notifier_id=None,
            **kwargs):
        """
        request_id: metadata key:igoRequestId
        runs: runs[]
        pipeline: {
            "pipeline_format": "",
            "pipeline_link": "",
            "pipeline_version: "",
            "pipeline_entrypoint": ""
        },
        file_group: file_group_id
        """
        super().__init__(request_id, runs, pipeline, pairing, output_directory_prefix, file_group, job_group_id,
                         job_group_notifier_id)
        
    def get_jobs(self):
        """
        :return:  A list of dicts where each dict contains
            :app: dict in pipeline format
            :inputs: dict of inputs for the pipeline run
            :name: run name (Example: TumorSampleName Run 1)
        """
        pass
''')

CONFIG_TEMPLATE = {
    "pipeline": {
        "pipeline_id": "",
        "pipeline_github_link": "",
        "pipeline_github_version": "",
        "pipeline_entrypoint": ""
    },
    "operator": {
        "class_name": "",
        "package_name": ""
    }
}


class OperatorBootstrapper(object):

    @staticmethod
    def initialize(operator_name, base_dir, pipeline_name, pipeline_link, pipeline_version, pipeline_endpoint, pipeline_format):
        operator_file_name = OperatorBootstrapper.camel_to_snake(operator_name)
        main_directory = operator_file_name.replace("_", "-")
        operator_package = operator_file_name
        operator_directory = os.path.join(base_dir, main_directory)
        Path(operator_directory).mkdir(parents=True, exist_ok=True)
        config_path = OperatorConfiguration.config_path(operator_directory)
        OperatorBootstrapper.initialize_config(config_path,
                                               operator_name,
                                               operator_file_name,
                                               pipeline_name,
                                               pipeline_link,
                                               pipeline_version,
                                               pipeline_endpoint,
                                               pipeline_format)
        package_directory = os.path.join(operator_directory, operator_package)
        Path(package_directory).mkdir(parents=True, exist_ok=True)
        operator_file = os.path.join(package_directory, f"{operator_file_name}.py")
        with open(operator_file, 'w', encoding='utf-8') as f:
            operator_content = OPERATOR_TEMPLATE.substitute(operator_name=operator_name)
            f.write(operator_content)
        OperatorBootstrapper.copy_package_file("templates/README.md", os.path.join(operator_directory, "README.md"))
        OperatorBootstrapper.copy_package_file("templates/requirements.txt", os.path.join(operator_directory, "requirements.txt"))
        OperatorBootstrapper.copy_package_file("templates/setup.py.template",
                                               os.path.join(operator_directory, "setup.py"))
        OperatorBootstrapper.copy_package_file("templates/__init__.py.template",
                                               os.path.join(package_directory, "__init__.py"))
        OperatorBootstrapper.update_setup_py(operator_name, main_directory, operator_directory)

        pipeline_schema = PipelineCache.get_pipeline(pipeline_format, pipeline_link, pipeline_version, pipeline_endpoint)
        input_schema_path = OperatorConfiguration.input_schema_path(operator_directory)
        OperatorBootstrapper.initialize_input_schema(input_schema_path, pipeline_schema["inputs"])

    @staticmethod
    def copy_package_file(file_path, target_path):
        """Copy a file from the package to a target location"""
        source = files("voyager_sdk").joinpath(file_path)
        with as_file(source) as src_file:
            shutil.copy(src_file, target_path)

    @staticmethod
    def update_setup_py(operator_name, package_name, operator_directory):
        path = Path(os.path.join(operator_directory, "setup.py"))

        if not path.exists():
            raise FileNotFoundError(f"setup.py not found at {path.absolute()}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        updated_content = content.replace("{OPERATOR_NAME}", operator_name)
        updated_content = updated_content.replace("{PACKAGE_NAME}", package_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

    @staticmethod
    def initialize_config(config_path, operator_name, operator_package, pipeline_name, pipeline_link, pipeline_version, pipeline_entrypoint, pipeline_format):
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        config = {
            "pipeline": {
                "pipeline_id": None,
                "pipeline_name": pipeline_name,
                "pipeline_link": pipeline_link,
                "pipeline_version": pipeline_version,
                "pipeline_entrypoint": pipeline_entrypoint,
                "pipeline_format": pipeline_format
            },
            "operator": {
                "operator_id": None,
                "class_name": operator_name,
                "package_name": operator_package
            }
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def initialize_input_schema(input_schema_path, input_schema):
        with open(input_schema_path, "w") as f:
            json.dump(input_schema, f, indent=4)

    @staticmethod
    def cache_pipeline(pipeline_path, pipeline):
        with open(pipeline_path, "w") as f:
            json.dump(pipeline, f, indent=4)

    @staticmethod
    def camel_to_snake(name):
        # Insert underscores before capital letters, then lowercase the whole string
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
