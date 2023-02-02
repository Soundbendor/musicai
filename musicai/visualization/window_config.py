import dotenv
from dotenv import dotenv_values
import os
import os.path

_DEBUG = False

class WindowConfig:
    def __init__(self, file_name: str = ".msvconfig"):
        if _DEBUG:
            print(f"WindowConfig __init__")

        self.file_name = file_name
        self.data = dotenv_values(self.file_name)
        self._parse_config_file()

    def _parse_config_file(self):
        if _DEBUG:
            print("WindowConfig::parse_config_file")
        for key, value in self.data.items():
            if _DEBUG:
                print(f"{key}: {value}")
            try:
                a_val = int(value)
            except ValueError:
                a_val = value
            setattr(self, key, a_val)

# def main():
#     print("Hello World")
#     config = WindowConfig()
#
#     print(f"config data: {config.data.items()}")
#
#     print(f"dir(config): {dir(config)}")
#
# if __name__ == '__main__':
#     main()