from abc import ABC, abstractmethod


class Getter(ABC):
    @abstractmethod
    def make_request():
        ...
