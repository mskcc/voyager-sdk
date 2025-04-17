import os
import git
import uuid
import shutil
import logging


class PipelineResolver(object):
    logger = logging.getLogger(__name__)

    def __init__(self, github, entrypoint, version=None):
        self.github = github
        self.entrypoint = entrypoint
        self.version = version

    def _git_clone(self, location):
        dirname = os.path.join(location, self._extract_dirname_from_github_link())
        cached = GithubCache.get(self.github, self.version)
        if cached:
            self.logger.info("App found in cache %s" % cached)
            os.symlink(cached, dirname)
        else:
            git.Git(location).clone(self.github, "--branch", self.version, "--recurse-submodules")
        return dirname

    def _dir_name(self):
        dirname = "/tmp/" + str(uuid.uuid4())
        os.mkdir(dirname)
        return dirname

    def _extract_dirname_from_github_link(self):
        dirname = self.github.rsplit("/", 2)[1] if self.github.endswith("/") else self.github.rsplit("/", 1)[1]
        if dirname.endswith(".git"):
            dirname = dirname[:-4]
        return dirname

    def _cleanup(self, location):
        if os.path.islink(location):
            os.unlink(location)
        else:
            shutil.rmtree(location)

    def load(self):
        pass

    def resolve(self):
        pass
