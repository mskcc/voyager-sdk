import logging
from config import Config
from voyager_sdk.file_repository import FileRepository


config = Config()


class Operator(object):
    logger = logging.getLogger(__name__)
    config = Config()

    def __init__(
        self,
        model,
        job_group_id=None,
        job_group_notifier_id=None,
        request_id=None,
        run_ids=[],
        pipeline=None,
        pairing=None,
        output_directory_prefix=None,
        file_group=None,
        **kwargs
    ):

        self.model = model
        self.request_id = request_id
        self.run_ids = run_ids
        self.file_group = file_group
        if not self.file_group:
            self.file_group = config.default_file_group
        self.files = FileRepository.filter(file_group=self.file_group).all()
        self.pairing = pairing
        # {"pairs": [{"tumor": "tumorSampleName", "normal": "normalSampleName"}]}
        self.output_directory_prefix = output_directory_prefix
        self._jobs = []
        self._pipeline = pipeline
        self._job_group_id = job_group_id
        self._job_group_notifier_id = job_group_notifier_id
        # self.logger = OperatorLogger()

    def get_pipeline_id(self):
        if self._pipeline:
            return self._pipeline
        return str(self.model.pipeline_set.filter(default=True).first().pk)

    def get_jobs(self):
        """
        :return: ([RunCreator])
        """
        files = FileRepository.filter()
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
