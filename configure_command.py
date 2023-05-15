from config_manager import ConfigManager


class ConfigureCommand(object):
    def __init__(self, api_key):
        self.configManager = ConfigManager()
        self.setApiKey(api_key)

    def setApiKey(self, api_key):
        self.configManager.set_api_token(api_key)