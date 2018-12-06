from abc import ABCMeta, abstractmethod


class Provider(object):
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

    @abstractmethod
    def get_current_book_name(self, user_id):
        """The the user currently played book."""
        pass

    @abstractmethod
    def get_books(self):
        """Get all the book there is."""
        pass

    @abstractmethod
    def select_book(self, user_id, book_name):
        """Select the a new currently played book for player"""
