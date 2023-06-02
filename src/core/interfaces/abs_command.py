import abc

from config import Config


class AbsCommand(metaclass=abc.ABCMeta):
    """AbsCommand abstract obj"""
    __config = dict()

    NAMESPACE = "command"

    @abc.abstractmethod
    def run(self):
        """Execute routine"""
        pass

    def build_context(self, config: Config):
        self.config = config
        pass

    @property
    def config(self):
        """config property"""
        return self.__config

    @config.setter
    def config(self, value):
        """config setter"""
        self.__config = value
