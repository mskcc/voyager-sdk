import os
import json
import shutil
import tempfile
import unittest
from unittest import mock

# Keep Config() from touching the real ~/.voyagersdk
os.environ["HOME"] = tempfile.mkdtemp()
os.makedirs(os.path.join(os.environ["HOME"], ".voyagersdk"))

from voyager_sdk.protocols.nextflow.pipeline import NextflowResolver

SAMPLESHEET_SCHEMA = {
    "items": {
        "type": "object",
        "properties": {
            "sample": {"type": "string"},
            "fastq_1": {"type": "string", "format": "file-path"},
            "fastq_2": {"type": "string", "format": "file-path"},
        },
    }
}


def nextflow_schema(defs_key="$defs", mimetype="text/csv"):
    return {
        defs_key: {
            "input_output_options": {
                "properties": {
                    "input": {"type": "string", "format": "file-path", "schema": "assets/schema_input.json", "mimetype": mimetype},
                    "outdir": {"type": "string", "format": "directory-path"},
                }
            },
            "reference_genome_options": {"properties": {"genome": {"type": "string"}}},
            "no_properties": {"type": "object"},
        }
    }


class TestNextflowResolver(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.repo, "assets"))
        with open(os.path.join(self.repo, "assets", "schema_input.json"), "w") as f:
            json.dump(SAMPLESHEET_SCHEMA, f)
        patcher = mock.patch.object(NextflowResolver, "_git_clone", return_value=self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.repo)

    def _write_schema(self, schema):
        with open(os.path.join(self.repo, "nextflow_schema.json"), "w") as f:
            json.dump(schema, f)

    def _resolve(self, nfcore_template=True):
        return NextflowResolver("https://github.com/nf-core/demo", "main.nf", "1.0.0", nfcore_template).resolve()

    def test_nfcore_inputs_and_outputs(self):
        self._write_schema(nextflow_schema())
        pipeline = self._resolve()
        inputs = {i["id"]: i for i in pipeline["inputs"]}
        self.assertEqual(set(inputs), {"input", "outdir", "genome"})
        self.assertEqual(inputs["outdir"]["schema"], {"type": "directory-path"})
        self.assertEqual(inputs["genome"]["schema"], {"type": None})
        samplesheet = inputs["input"]
        self.assertEqual(samplesheet["extension"], ".csv")
        self.assertEqual(
            samplesheet["schema"]["items"]["fields"],
            [
                {"id": "sample", "type": None},
                {"id": "fastq_1", "type": "file-path"},
                {"id": "fastq_2", "type": "file-path"},
            ],
        )
        self.assertEqual(
            samplesheet["template"],
            "sample,fastq_1,fastq_2\n{{#input}}\n{{sample}},{{fastq_1}},{{fastq_2}}\n{{/input}}",
        )
        self.assertEqual(pipeline["outputs"], [{"id": "outputs", "schema": {"type": {"items": "File", "type": "array"}}}])

    def test_legacy_definitions_key(self):
        self._write_schema(nextflow_schema(defs_key="definitions"))
        ids = {i["id"] for i in self._resolve()["inputs"]}
        self.assertEqual(ids, {"input", "outdir", "genome"})

    def test_tsv_and_unknown_mimetype(self):
        for mimetype in ("text/tsv", "application/unknown"):
            self._write_schema(nextflow_schema(mimetype=mimetype))
            samplesheet = next(i for i in self._resolve()["inputs"] if i["id"] == "input")
            self.assertEqual(samplesheet["extension"], ".tsv")
            self.assertTrue(samplesheet["template"].startswith("sample\tfastq_1\tfastq_2\n"))

    def test_missing_samplesheet_schema_is_skipped(self):
        os.remove(os.path.join(self.repo, "assets", "schema_input.json"))
        self._write_schema(nextflow_schema())
        ids = {i["id"] for i in self._resolve()["inputs"]}
        self.assertEqual(ids, {"outdir", "genome"})

    def test_non_nfcore_uses_inputs_template(self):
        template = {"inputs": [{"id": "foo", "schema": {"type": "string"}}], "outputs": []}
        with open(os.path.join(self.repo, "inputs.template.json"), "w") as f:
            json.dump(template, f)
        self.assertEqual(self._resolve(nfcore_template=False), template)


if __name__ == "__main__":
    unittest.main()
