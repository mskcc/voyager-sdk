import os
import json
from voyager_sdk.protocols.pipeline_resolver import PipelineResolver

NFCORE_OUTPUTS = [{"id": "outputs", "schema": {"type": {"items": "File", "type": "array"}}}]


class NextflowResolver(PipelineResolver):
    def __init__(self, github, entrypoint, version=None, nfcore_template=False):
        super().__init__(github, entrypoint, version)
        self.nfcore_template = nfcore_template

    def resolve(self):
        location = self._git_clone()
        if self.nfcore_template:
            with open(os.path.join(location, "nextflow_schema.json"), "r") as f:
                nextflow_schema = json.load(f)
            inputs = self.schemas2template(nextflow_schema, location)
            return {"inputs": inputs, "outputs": NFCORE_OUTPUTS}
        with open(os.path.join(location, "inputs.template.json"), "r") as f:
            return json.load(f)

    def schemas2template(self, nextflow_schema, location):
        inputs = []
        defs = nextflow_schema.get("$defs") or nextflow_schema.get("definitions") or {}
        for definition in defs.values():
            for key, prop in definition.get("properties", {}).items():
                schema = prop.get("schema")
                mimetype = prop.get("mimetype")
                if schema and mimetype:
                    samplesheet_input = self._samplesheet_input(key, schema, mimetype, location)
                    if samplesheet_input:
                        inputs.append(samplesheet_input)
                else:
                    inputs.append({"id": key, "schema": {"type": prop.get("format")}})
        return inputs

    def _samplesheet_input(self, key, schema, mimetype, location):
        schema_path = os.path.join(location, schema)
        if not os.path.exists(schema_path):
            self.logger.warning(f"Samplesheet schema '{schema_path}' not found, skipping input '{key}'.")
            return None
        delimiter, extension = self._delimiter_for_mimetype(mimetype)
        with open(schema_path, "r") as f:
            samplesheet_props = json.load(f)["items"]["properties"]
        fields = [{"id": k, "type": v.get("format")} for k, v in samplesheet_props.items()]
        header = delimiter.join([f["id"] for f in fields]) + "\n"
        body_start = f"{{{{#{key}}}}}\n"
        body_end = f"\n{{{{/{key}}}}}"
        body = delimiter.join([f'{{{{{f["id"]}}}}}' for f in fields])
        return {
            "id": key,
            "schema": {"items": {"fields": fields}},
            "template": header + body_start + body + body_end,
            "extension": extension,
        }

    def _delimiter_for_mimetype(self, mimetype):
        if mimetype == "text/csv":
            return ",", ".csv"
        if mimetype != "text/tsv":
            self.logger.warning(f"Unsupported mimetype '{mimetype}', defaulting to tab delimiter.")
        return "\t", ".tsv"
