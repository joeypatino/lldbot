import configparser
import os


class ConfigManager:
    def __init__(self, config_file=".lldbotrc"):
        self.config_file = os.path.expanduser(f"~/.lldbot/{config_file}")
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            self.config.add_section('default')
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        else:
            self.config.read(self.config_file)

    def get_api_token(self):
        try:
            return self.config.get('default', 'api_token')
        except configparser.NoOptionError:
            return None

    def set_api_token(self, token):
        self.config.set('default', 'api_token', token)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
