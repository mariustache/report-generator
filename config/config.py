import os
import configparser

from utils import Info
from utils import Error

CONFIG_PATH = "config/config.cfg"


class ConfigModule:

    SECTIONS = ["Common", "Management", "Journal"]

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._read()

    def _read(self):
        if not os.path.isfile(CONFIG_PATH):
            Error(f"{CONFIG_PATH} file not present.")
            return

        Info(f"Reading {CONFIG_PATH} data.")
        self._config.read(CONFIG_PATH)

        for section in ConfigModule.SECTIONS:
            if section not in self._config:
                Error(f"Section {section} does not exist.")
    
    def GetDataFromKey(self, section, ini_key):
        if section not in self._config:
            Error(f"Section {section} does not exist.")
        if ini_key not in self._config[section]:
            Error(f"Key {ini_key} does not exist in section {section}.")
        value = self._config[section].get(ini_key)
        Info(f"Reading {section}/{ini_key} from .ini file: {value}")
        return value

    def GetFirebirdConfig(self):
        return "config/firebird.cfg"

    def GetIntrari(self):
        return self.GetDataFromKey("Common", "Intrari")
    
    def GetIesiri(self):
        return self.GetDataFromKey("Common", "Iesiri")
    
    def GetProduse(self):
        return self.GetDataFromKey("Common", "Produse")

    def GetStartDate(self):
        return self.GetDataFromKey("Common", "StartDate")
    
    def GetSoldPrecedent(self):
        return self.GetDataFromKey("Management", "SoldPrecedent")

    def GetPlatiNumerar(self):
        return self.GetDataFromKey("Journal", "PlatiNumerar")

    def GetPlatiAlte(self):
        return self.GetDataFromKey("Journal", "PlatiAlte")

    def GetIncasari(self):
        return self.GetDataFromKey("Journal", "Incasari")
