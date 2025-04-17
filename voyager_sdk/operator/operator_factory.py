import sys
import importlib.util


class OperatorFactory(object):

    @staticmethod
    def get_by_model(class_name, **kwargs):
        # TODO: Deprecated
        mod_name, func_name = class_name.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        operator_class = getattr(mod, func_name)
        return operator_class(**kwargs)

    @staticmethod
    def import_operator(class_name, full_path):
        mod_name, func_name = class_name.rsplit(".", 1)
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        return getattr(module, func_name)