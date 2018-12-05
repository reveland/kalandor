from abc import ABCMeta, abstractmethod


class Handler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, user_id, message):
        """Handle an user message."""
        pass
