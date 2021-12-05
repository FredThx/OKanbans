# coding: utf-8
#
# Des utilitaires pour pyQT
#


class Qutil:
    '''Des outils pour pyQT
    '''
    @staticmethod
    def get_parent(widget, parent_class = None):
        '''return the first parent whois a parent_class instance'''
        while widget:
            widget = widget.parent()
            if parent_class is None or isinstance(widget, parent_class):
                return widget