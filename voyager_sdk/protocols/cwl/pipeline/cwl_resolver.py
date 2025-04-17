import os
import json
import subprocess
from pathlib import Path
from voyager_sdk.protocols.pipeline_resolver import PipelineResolver


class CWLResolver(PipelineResolver):
    def __init__(self, github, entrypoint, version=None):
        super().__init__(github, entrypoint, version)

    def resolve(self):
        location = self._git_clone()
        output_name = os.path.join(location, self._file_name())
        with open(output_name, "w") as out:
            subprocess.check_call(["cwlpack", os.path.join(location, self.entrypoint), "--json"], stdout=out)
        with open(output_name) as f:
            pipeline = json.load(f)
        return pipeline

    def _file_name(self):
        github_name = self.github.split(".com/")[-1].replace("/", "_")
        github_name = github_name.split(".com/")[-1].replace(":", "_")
        file_name = f"{github_name}_{self.version}.cwl"
        return file_name

    def load(self):
        location = self._git_clone()
        output_name = os.path.join(location, self._file_name())
        if Path(output_name).exists():
            with open(os.path.join(location, self.entrypoint), "r") as f:
                ret = json.load(f)
            return ret
