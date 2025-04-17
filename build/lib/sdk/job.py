class Job(object):

    def __init__(self, job_id, protocol, app, inputs, outputs, config):
        self.id = job_id
        self.protocol = protocol
        self.app = app
        self._inputs_schemas = []
        self.inputs = inputs
        self.outputs = outputs
        self._outputs_schemas = []
        self.config = config
