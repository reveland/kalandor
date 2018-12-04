from abc import ABCMeta, abstractmethod


class Adventure(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_page(self, page_id):
        """Get page with options and images by id."""
        pass

    @abstractmethod
    def record_action(self, user_id, action):
        """Record an user action."""
        pass

    @abstractmethod
    def get_actions(self, user_id):
        """Get an user prev actions."""
        pass
