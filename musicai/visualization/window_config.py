from dotenv import dotenv_values


class WindowConfig(object):
    _instance = None

    def __new__(cls, file_name: str = ".msvconfig"):
        if cls._instance is None:
            cls._instance = super(WindowConfig, cls).__new__(cls)
            cls._instance._parse_config_file(dotenv_values(file_name))
        return cls._instance

    def _parse_config_file(self, config_data):
        for key, value in config_data.items():
            try:
                a_val = int(value)
            except ValueError:
                a_val = value
            setattr(self, key, a_val)
