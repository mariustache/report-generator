
from dbfread import DBF
from firebird.driver import connect, driver_config
from pandas import DataFrame

import os

from utils import Error
from utils import Debug
from utils import Info


class Database:

    def __init__(self, name):
        self.name = name

    # Returns the database as a pandas data frame object
    def get_db(self, columns):
        assert "Should be implemented in derived classes"


class DBFDatabase(Database):

    def __init__(self, name):
        super().__init__(name)

    def get_db(self, columns):
        dbf = DBF(self.name)
        columns = list(columns)
        return DataFrame(iter(dbf))[columns]


class FirebirdDatabase(Database):

    def __init__(self, name, config):
        super().__init__(name)
        self.config = config

    def get_db(self, columns):
        driver_config.read(self.config)
        keys = ",".join(columns)

        with connect('saga', user=f'{os.environ["ISC_USER"]}', password=f'{os.environ["ISC_PASSWORD"]}') as con:
            cursor = con.cursor()
            cursor.execute(f'select {keys} from {self.name}')

            _dataFrame = DataFrame(iter(cursor.fetchall()))
            _dataFrame.columns = columns
            return _dataFrame


class DatabaseParser:
    
    FIELDS = list()
    INSTANCE = None

    def __init__(self, database):
        self._dataFrame = database.get_db(self.FIELDS.keys())

        # Ensure correct data type in data frame.
        for column_name, data_type in self.FIELDS.items():
            # Replace None/NaN with default value
            fill_value = ""
            if data_type == "int64" or data_type == "float64":
                fill_value = 0
            self._dataFrame[column_name] = self._dataFrame[column_name].fillna(fill_value)
            self._dataFrame[column_name] = self._dataFrame[column_name].astype(data_type)
        # Strip whitespace
        self._dataFrame = self._dataFrame.apply(lambda x: x.str.strip() if isinstance(x, str) else x)

    def GetData(self):
        return self._dataFrame

    def GetDataWithPosition(self, position):
        return self._dataFrame.loc[[position]]

    def GetDataWithValue(self, record_key, record_value):
        mask = self._dataFrame[record_key] == record_value
        return self._dataFrame.loc[mask]

    def GetDataWithDate(self, date):
        mask = self._dataFrame["DATA"] == date
        return self._dataFrame.loc[mask]

    def GetDataFromDate(self, start_date):
        mask = self._dataFrame["DATA"] >= start_date
        return self._dataFrame.loc[mask]

    def PrintData(self):
        print(self._dataFrame)

    def PrintEntry(self, position):
        print(self._dataFrame.loc[[position]])
    
    @classmethod
    def GetParser(cls):
        if cls.INSTANCE is None:
            Error(f"Trying to access instance of {cls.__name__} class, but it does not exist.")
        return cls.INSTANCE


class ParserIesiri(DatabaseParser):

    FIELDS = {
        "NR_IESIRE": "string",
        "ID_IESIRE": "string",
        "DENUMIRE": "string",
        "DATA": "datetime64[ns]",
        "TOTAL": "float64",
        "NR_BONURI": "int64"
    }

    def __init__(self, database):
        DatabaseParser.__init__(self, database)
        ParserIesiri.INSTANCE = self


class ParserIntrari(DatabaseParser):

    FIELDS = {
        "ID_INTRARE": "string",
        "NR_NIR": "string",
        "NR_INTRARE": "string",
        "DENUMIRE": "string",
        "DATA": "datetime64[ns]",
        "TOTAL": "float64",
        "TIP": "string"
    }

    def __init__(self, database):
        DatabaseParser.__init__(self, database)
        ParserIntrari.INSTANCE = self


class ParserProduse(DatabaseParser):

    FIELDS = {
        "ID_U": "string",
        "ID_INTRARE": "string",
        "DENUMIRE": "string",
        "DEN_GEST": "string",
        "DEN_TIP": "string",
        "TVA_ART": "string",
        "CANTITATE": "float64",
        "PRET_VANZ": "float64"
    }

    def __init__(self, database):
        DatabaseParser.__init__(self, database)
        ParserProduse.INSTANCE = self
    
    def GetDataWithIdIntrare(self, id_intrare):
        mask = self._dataFrame["ID_INTRARE"] == id_intrare
        return self._dataFrame.loc[mask]
