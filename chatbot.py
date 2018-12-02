from abc import ABCMeta, abstractmethod


class ChatBot(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_message(self, request):
        """Get received message and the user's id."""
        pass

    @abstractmethod
    def send_message(self, user_id, text=None):
        """Send a message to the user."""
        pass
