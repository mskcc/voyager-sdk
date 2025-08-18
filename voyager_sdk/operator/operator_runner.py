import json
import uuid
from config import Config
from git import Repo
from voyager_sdk.configuration import OperatorConfiguration
from voyager_sdk.client.voyager_client import VoyagerClient
from voyager_sdk.operator.operator_factory import OperatorFactory
from exceptions.operator_exceptions import MissingArgumentsException

config = Config()


class OperatorRunner(object):

    def __init__(self, path):
        self.path = path
        self.operator_config = OperatorConfiguration.load()

    def run(self, request_id=None, pairs=None):
        operator_path = f"{self.operator_config.operator['package_name']}.{self.operator_config.operator['class_name']}"
        file_path = self.path + "/" + self.operator_config.operator['package_name'] + "/" + f"{self.operator_config.operator['package_name']}.py"
        OperatorClass = OperatorFactory.import_operator(operator_path, file_path)
        if request_id:
            operator_instance = OperatorClass(request_id=request_id, pipeline=self.operator_config.pipeline)
        elif pairs:
            with open(pairs, "r") as f:
                pairs_dict = json.load(f)
            operator_instance = OperatorClass(pairs=pairs_dict, pipeline=self.operator_config.pipeline)
        else:
            raise MissingArgumentsException("--request-id or --pairs needs to be defined")
        jobs = operator_instance.get_jobs()
        return jobs

    def run_production(self, operator_class, request_id=None, pairs=None):
        OperatorClass = OperatorFactory.import_installed_operator(operator_class)
        if request_id:
            operator_instance = OperatorClass(request_id=request_id, pipeline=self.operator_config.pipeline)
        elif pairs:
            with open(pairs, "r") as f:
                pairs_dict = json.load(f)
            operator_instance = OperatorClass(pairs=pairs_dict, pipeline=self.operator_config.pipeline)
        jobs = operator_instance.get_jobs()
        return jobs

    def register(self):
        repo = Repo(self.path)
        origin = repo.remotes.origin.url
        if origin.startswith("git@"):
            origin = "https://" + origin[4:].replace(":", "/")
        commit = repo.head.commit.hexsha
        repo_tag = None
        for tag in repo.tags:
            if tag.commit.hexsha == commit:
                repo_tag = tag.name
                break
        if not repo_tag:
            # Can't register operator without github tag
            raise
        class_name = self.operator_config.operator["class_name"]
        package_name = self.operator_config.operator["package_name"]
        github_link = origin
        version = repo_tag
        pipeline_id = self.operator_config.pipeline["pipeline_id"]
        try:
            response = VoyagerClient.register_operator(class_name, version, class_name, package_name, github_link, pipeline_id)
        except Exception as e:
            raise
        self.operator_config.pipeline["operator_id"] = response["id"]
        self.operator_config.dump()
        return self.operator_config.operator


    def register_pipeline(self, output_directory, output_file_group):
        pipeline = self.operator_config.pipeline
        if not output_file_group:
            output_file_group = VoyagerClient.get_file_group_id(config.output_file_group)["id"]
        if not output_directory:
            output_directory = config.output_directory
        try:
            response = VoyagerClient.register_pipeline(pipeline["pipeline_format"],
                                                       pipeline["pipeline_name"],
                                                       pipeline["pipeline_link"],
                                                       pipeline["pipeline_version"],
                                                       pipeline["pipeline_entrypoint"],
                                                       output_directory,
                                                       output_file_group
                                                       )
        except Exception as e:
            raise
        self.operator_config.pipeline["pipeline_id"] = response["id"]
        self.operator_config.dump()
        return self.operator_config.pipeline

    def submit_runs(self, inputs):
        pipeline = self.operator_config.pipeline["pipeline_id"]
        output_directory = config.output_directory + f"/{str(uuid.uuid4())}"
        for input_json in inputs:
            response = VoyagerClient.run_pipeline(input_json["name"], pipeline, input_json["inputs"], input_json.get("tags", {}), output_directory)
            print(response.json())

