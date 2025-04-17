import os
import json
from pathlib import Path
from voyager_sdk.protocols.pipeline_resolver import PipelineResolver


class NextflowResolver(PipelineResolver):
    def __init__(self, github, entrypoint, version=None):
        super().__init__(github, entrypoint, version)

    def resolve(self):
        dir = self._dir_name()
        location = self._git_clone(dir)
        with open(os.path.join(location, "nextflow_schema.json"), "r") as f:
            nextflow_schema = json.load(f)
            inputs = self.schemas2template(nextflow_schema, location)
            pipeline = {"inputs": inputs}
        return pipeline

    def schemas2template(self, nextflow_schema, location):
        # TODO Not sure if this is an exhaustive search of possible definitions
        # TODO parse everything in definitions
        reference = nextflow_schema["definitions"]["reference_genome_options"]["properties"]
        input = nextflow_schema["definitions"]["input_output_options"]["properties"]
        properties = {**reference, **input}
        # Check for sample-sheet CLI inputs
        samplesheets = [key for key, val in properties.items() if val.get("format") == "sample-sheet"]
        inputs = [
            {"id": key, "schema": {"type": val.get("format")}}
            for key, val in properties.items()
            if val.get("format") != "sample-sheet"
        ]
        # Check Assets for sample sheet schemas
        for schema in samplesheets:
            with open(os.path.join(location, f"assets/schema_{schema}.json"), "r") as f:
                nextflow_schema = json.load(f)
                samplesheet_props = nextflow_schema["items"]["properties"]
                fields = [{"id": key, "type": val.get("format")} for key, val in samplesheet_props.items()]
                header = "\t".join([f["id"] for f in fields]) + "\n"
                body_start = f"{{{{#{schema}}}}}\n"
                body_end = f"\n{{{{/{schema}}}}}"
                body = "\t".join([f'{{{{{f["id"]}}}}}' for f in fields])
                template = header + body_start + body + body_end
                samplesheet_input = {"id": schema, "schema": {"items": {"fields": fields}}, "template": template}
                inputs.append(samplesheet_input)
        return inputs

    def load(self):
        location = self._git_clone()
        output_name = os.path.join(location, self._file_name())
        if Path(output_name).exists():
            with open(os.path.join(location, self.entrypoint), "r") as f:
                ret = json.load(f)
            return ret