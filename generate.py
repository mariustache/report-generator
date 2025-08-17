import wx

from config.config import ConfigModule
from data.parser import DBFDatabase
from data.parser import DBFParserIesiri
from data.parser import DBFParserIntrari
from data.parser import DBFParserProduse
from data.generator import JournalGenerator
from data.generator import ManagementGenerator

from gui.frame import MainFrame

from utils import Info


if __name__ == "__main__":
    config = ConfigModule()

    parser_iesiri = DBFParserIesiri(DBFDatabase(config.GetIesiri()))
    parser_intrari = DBFParserIntrari(DBFDatabase(config.GetIntrari()))
    parser_produse = DBFParserProduse(DBFDatabase(config.GetProduse()))

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