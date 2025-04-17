

import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.parser = argparse.ArgumentParser(prog=self.name, description=self.description)
        self.setup_arguments()

    @abstractmethod
    def execute(self, args):
        """
        Execute the command logic.
        Subclasses must implement this method.
        """
        pass
