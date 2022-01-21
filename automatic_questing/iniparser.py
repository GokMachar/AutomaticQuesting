from shutil import copyfile
from logging import getLogger
from os.path import join, exists
from configparser import ConfigParser

from automatic_questing.aqlogger import BlacklistFilter
from automatic_questing.structures import AccountData


class INIParser(object):
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.filtered_strings = None

        self.logger = getLogger()

        self.config = self.read_file()
        self.account_names = self.enabled_accounts()
        self.accounts = []
        self.interval = 10
        self.rpc = ""
        self.parse_opts()

    def config_blacklist(self):
        filtered_strings = [section.get(k) for key, section in self.config.items()
                            for k in section if k in BlacklistFilter.blacklisted_strings]
        self.filtered_strings = list(filter(None, filtered_strings))
        # Added matching for domains that use /locations. ConnectionPool ignores the location in logs
        domains_only = [string.split('/')[0] for string in filtered_strings if '/' in string]
        self.filtered_strings.extend(domains_only)
        # Added matching for domains that use :port. ConnectionPool splits the domain/ip from the port
        without_port = [string.split(':')[0] for string in filtered_strings if ':' in string]
        self.filtered_strings.extend(without_port)

        for handler in self.logger.handlers:
            handler.addFilter(BlacklistFilter(set(self.filtered_strings)))

    def enabled_accounts(self):
        sections = self.config.sections()
        sections.remove("global")
        return sections

    def read_file(self):
        config = ConfigParser(interpolation=None)
        ini = "config.ini"
        file_path = join(self.data_folder, ini)

        if not exists(file_path):
            self.logger.error('File missing (%s) in %s', ini, self.data_folder)
            if ini == 'config.ini':
                try:
                    self.logger.debug('Creating config.ini from config.example.ini')
                    copyfile(join(self.data_folder, 'config.example.ini'), file_path)
                except IOError as e:
                    self.logger.error("AutomaticQuesting does not have permission to write to %s. Error: %s - Exiting.",
                                      e, self.data_folder)
                    exit(1)

        self.logger.debug('Reading from %s', ini)
        with open(file_path) as config_ini:
            config.read_file(config_ini)

        return config

    def parse_opts(self):
        self.config_blacklist()
        self.interval = self.config["global"].getint("interval")
        self.rpc = self.config["global"].get("rpc")

        for account in self.account_names:
            a = self.config[account]
            if a.getboolean("enabled"):
                act = AccountData(
                    address=a.get("address"),
                    pools=a.get("pools").split(","),
                    private_key=a.get("private_key"),
                    blocks=a.getint("blocks")
                )
                self.accounts.append(act)
