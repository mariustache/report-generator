import wx

from config.config import ConfigModule
from data.parser import DBFDatabase
from data.parser import FirebirdDatabase
from data.parser import ParserIesiri
from data.parser import ParserIntrari
from data.parser import ParserProduse
from data.generator import JournalGenerator
from data.generator import ManagementGenerator

from gui.frame import MainFrame

database_selector = 'firebird' # or dbf


if __name__ == "__main__":
    config = ConfigModule()

    if database_selector == 'firebird':
        parser_iesiri = ParserIesiri(FirebirdDatabase('IESIRI', config.GetFirebirdConfig()))
        parser_intrari = ParserIntrari(FirebirdDatabase('INTRARI', config.GetFirebirdConfig()))
        parser_produse = ParserProduse(FirebirdDatabase('INTR_DET', config.GetFirebirdConfig()))
    elif database_selector == 'dbf':
        parser_iesiri = ParserIesiri(DBFDatabase(config.GetIesiri()))
        parser_intrari = ParserIntrari(DBFDatabase(config.GetIntrari()))
        parser_produse = ParserProduse(DBFDatabase(config.GetProduse()))
    else:
        raise f"Invalid database selector {database_selector}"

    start_date = config.GetStartDate()
    sold_precedent = config.GetSoldPrecedent()
    plati_numerar = config.GetPlatiNumerar()
    plati_alte = config.GetPlatiAlte()
    incasari = config.GetIncasari()
    
    journal_generator = JournalGenerator(start_date, plati_numerar, plati_alte, incasari)
    management_generator = ManagementGenerator(start_date, sold_precedent)
    
    app = wx.App()
    frm = MainFrame(None, title="Generator Rapoarte")
    frm.Show()
    app.MainLoop()
