from voyager_sdk.protocols import ProtocolType
from voyager_sdk.protocols.cwl.pipeline import CWLResolver
from voyager_sdk.protocols.nextflow.pipeline import NextflowResolver


class PipelineCache(object):
    @staticmethod
    def get_pipeline(protocol_type, github_link, github_version, pipeline_entrypoint):
        resolver_class = PipelineCache._get_pipeline_resolver(protocol_type)
        resolver = resolver_class(github_link, pipeline_entrypoint, github_version)
        resolved_dict = resolver.resolve()
        return resolved_dict

    @staticmethod
    def _get_pipeline_resolver(pipeline_type):
        if pipeline_type == ProtocolType.CWL:
            return CWLResolver
        elif pipeline_type == ProtocolType.NEXTFLOW:
            return NextflowResolver
