import logging
from config import Config
from voyager_sdk.file_repository import FileRepository
from voyager_sdk.protocols.pipeline_cache import PipelineCache


config = Config()


class Operator(object):
    logger = logging.getLogger(__name__)
    config = Config()

    def __init__(
        self,
        request_id=None,
        run_ids=[],
        pipeline=None,
        pairing=None,
        output_directory_prefix=None,
        file_group=None,
        job_group_id=None,
        job_group_notifier_id=None,
        **kwargs
    ):
        self.request_id = request_id
        self.run_ids = run_ids
        self.file_group = file_group
        if not self.file_group:
            self.file_group = config.default_file_group
        self.files = None
        self.pairing = pairing
        # {"pairs": [{"tumor": "tumorSampleName", "normal": "normalSampleName"}]}
        self.output_directory_prefix = output_directory_prefix
        self._jobs = []
        self._pipeline = PipelineCache.get_pipeline(pipeline['pipeline_format'],
                                                    pipeline['pipeline_link'],
                                                    pipeline['pipeline_version'],
                                                    pipeline['pipeline_entrypoint'])
        self._pipeline = pipeline
        self._job_group_id = job_group_id
        self._job_group_notifier_id = job_group_notifier_id

    def get_pipeline_id(self):
        pass

    def get_jobs(self):
        """
        :return: ([RunCreator])
        """
        return self._jobs

    def get_output_metadata(self):
        """
        Override this method to set proper metadata to output files
        :return: dict
        """
        return {}

    def failed_to_create_job(self, error):
        pass

    def ready_job(self, pipeline, tempo_inputs, job):
        pass

    def on_job_fail(self, run):
        pass

    def links_to_files(self):
        """
        Override this method to put the list of operator generated files into the ticket description
        :return: list[string]
        """
        return {}
