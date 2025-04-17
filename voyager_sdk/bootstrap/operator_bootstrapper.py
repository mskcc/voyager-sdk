import os
import re
import json
from pathlib import Path
from string import Template
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
    def initialize(operator_name, base_dir, pipeline_link, pipeline_version, pipeline_endpoint, pipeline_format):
        operator_file_name = OperatorBootstrapper.camel_to_snake(operator_name)
        operator_directory = os.path.join(base_dir, operator_file_name)
        Path(operator_directory).mkdir(parents=True, exist_ok=True)
        operator_file = os.path.join(operator_directory, f"{operator_file_name}.py")
        with open(operator_file, 'w', encoding='utf-8') as f:
            operator_content = OPERATOR_TEMPLATE.substitute(operator_name=operator_name)
            f.write(operator_content)
        config_path = OperatorConfiguration.config_path(operator_directory)
        OperatorBootstrapper.initialize_config(config_path,
                                               operator_name,
                                               operator_file_name,
                                               pipeline_link,
                                               pipeline_version,
                                               pipeline_endpoint,
                                               pipeline_format)
        pipeline_schema = PipelineCache.get_pipeline(pipeline_format, pipeline_link, pipeline_version, pipeline_endpoint)
        input_schema_path = OperatorConfiguration.input_schema_path(operator_directory)
        OperatorBootstrapper.initialize_input_schema(input_schema_path, pipeline_schema["inputs"])

    @staticmethod
    def initialize_config(config_path, operator_name, operator_package, pipeline_link, pipeline_version, pipeline_entrypoint, pipeline_format):
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        config = {
            "pipeline": {
                "pipeline_link": pipeline_link,
                "pipeline_version": pipeline_version,
                "pipeline_entrypoint": pipeline_entrypoint,
                "pipeline_format": pipeline_format
            },
            "operator": {
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
    def camel_to_snake(name):
        # Insert underscores before capital letters, then lowercase the whole string
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
