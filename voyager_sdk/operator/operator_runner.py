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
        print(operator_path)
        file_path = self.path + "/" + f"{self.operator_config.operator['package_name']}.py"
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

    def register(self):
        repo = Repo(self.path)
        origin = repo.remotes.origin.url
        if origin.startswith("git@"):
            origin = "https://" + origin[4:].replace(":", "/")
        branch = self.get_current_branch()
        pipeline_id = self.operator_config.pipeline["pipeline_id"]
        operator = self.operator_config.operator
        body = {"operator_url": origin, "branch": branch}

    def register_pipeline(self):
        pipeline = self.operator_config.pipeline
        try:
            response = VoyagerClient.register_pipeline(pipeline["pipeline_format"],
                                                       pipeline["pipeline_name"],
                                                       pipeline["pipeline_link"],
                                                       pipeline["pipeline_version"],
                                                       pipeline["pipeline_entrypoint"],
                                                       config.output_directory,
                                                       config.output_file_group
                                                       )

        except Exception as e:
            raise
        self.operator_config.pipeline["pipeline_id"] = response["id"]
        self.operator_config.dump()

    def submit_runs(self, inputs):
        pipeline = self.operator_config.pipeline["pipeline_id"]
        output_directory = config.output_directory + f"/{str(uuid.uuid4())}"
        for input_json in inputs:
            response = VoyagerClient.run_pipeline(input_json["name"], pipeline, input_json["inputs"], input_json["tags"], output_directory)

