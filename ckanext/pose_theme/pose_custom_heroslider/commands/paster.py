# -*- coding: utf-8 -*-

from __future__ import print_function
from ckan.lib.cli import CkanCommand
from ckanext.pose_theme.pose_custom_heroslider.db import init as db_setup


class HeroSliderAdmin(CkanCommand):
    '''Initialize DB to add hero slider table

    Usage:

        paster heroslideradmin initdb -c <path to config file>

    Must be run from the ckanext-heroslideradmin directory.
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(CkanCommand, self).__init__(name)


    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(self.__doc__)
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'initdb':
            self.initdb()
        else:
            print('Command "{0}" not recognized'.format(cmd))


    def initdb(self):
        db_setup()
        print('DB tables created')
