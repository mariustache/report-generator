import wx
import pathlib
import pandas as pd
import os
from datetime import datetime

from data.parser import DatabaseParser
from data.parser import ParserIntrari
from data.parser import ParserIesiri
from data.parser import ParserProduse

from utils import NextDay



class ReportGenerator:

    INSTANCE = None
    OUTPUT_PATH = f'{pathlib.Path().resolve()}\output'

    def __init__(self):
        ReportGenerator.INSTANCE = self
        self._out_df_list = list()

    def GetDataFrameList(self):
        return self._out_df_list
    
    def GetInputDfFromDate(self, _date):
        return ParserIntrari.GetParser().GetDataWithDate(_date)

    def GetOutputDfFromDate(self, _date):
        return ParserIesiri.GetParser().GetDataWithDate(_date)

    def SaveFile(self, df_list):
        pd.set_option('display.expand_frame_repr', False)
        pathlib.Path(ReportGenerator.OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
        writer = pd.ExcelWriter(f'{ReportGenerator.OUTPUT_PATH}\{self.OUTPUT_FILE}')
        
        _start = 0
        for _df in df_list:
            print(_df)
            _df.to_excel(writer, startrow=_start)
            _start += len(_df) + 2

        writer.close()

    @classmethod
    def Instance(cls):
        return cls.INSTANCE


class JournalGenerator(ReportGenerator):

    COLUMNS = ["Data", "Documentul (felul, nr.)", "Felul operatiunii (explicatii)", "Incasari (numerar)", "Plati (numerar)", "Plati (alte)"]
    OUTPUT_FILE = f"jurnal_incasari_si_plati_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
    NAME = "Jurnal de incasari si plati"

    def __init__(self, start_date, plati_numerar=0, plati_alte=0, incasari=0):
        ReportGenerator.__init__(self)
        JournalGenerator.INSTANCE = self

        self.start_date = pd.to_datetime(start_date)
        self.plati_numerar = float(plati_numerar)
        self.plati_alte = float(plati_alte)
        self.incasari = float(incasari)
    
    def Generate(self, start_date, stop_date):
        # Get last values for inputs based on the difference between starte_date passed as input
        # and latest start date found in config file.
        plati_numerar = self.plati_numerar
        plati_alte = self.plati_alte
        incasari = self.incasari
        if self.start_date < start_date:
            plati_numerar, plati_alte, incasari = self.UpdateInputsForDate(self.start_date, start_date, plati_numerar, plati_alte, incasari)
        current_date = start_date
        intrari_df = self.GetInputDfFromDate(current_date)
        iesiri_df = self.GetOutputDfFromDate(current_date)

        while current_date <= stop_date:
            _out_list = list()
            # Add current data to header.
            _out_list.append([current_date.strftime("%d-%m-%Y"), 0, "TOTAL PRECEDENT", incasari, plati_numerar, plati_alte])
            # Update data values. Start and stop date are the same: current date.
            plati_numerar, plati_alte, incasari = self.UpdateInputsForDate(current_date, current_date, plati_numerar, plati_alte, incasari)

            rows = intrari_df.loc[intrari_df["TIP"] == "C"].apply(self.CreateAlteRow, axis='columns')
            [_out_list.append(row) for row in rows if not rows.empty]

            rows = intrari_df.loc[intrari_df["TIP"] != "C"].apply(self.CreateNumerarRow, axis='columns')
            [_out_list.append(row) for row in rows if not rows.empty]

            rows = iesiri_df.apply(self.CreateIncasariRow, axis='columns')
            [_out_list.append(row) for row in rows if not rows.empty]

            # Add updated data to footer.    
            _out_list.append([current_date.strftime("%d-%m-%Y"), 0, "TOTAL FINAL", incasari, plati_numerar, plati_alte])
            current_date = NextDay(current_date)
            intrari_df = self.GetInputDfFromDate(current_date)
            iesiri_df = self.GetOutputDfFromDate(current_date)

            if _out_list:
                self._out_df_list.append(pd.DataFrame(_out_list, columns=self.COLUMNS))
        
        self.SaveFile(self._out_df_list)
    
    def UpdateInputsForDate(self, start_date, stop_date, plati_numerar, plati_alte, incasari):
        
        intrari_df = self.GetInputDfFromDate(start_date)
        iesiri_df = self.GetOutputDfFromDate(start_date)
        
        while start_date <= stop_date:
            if not intrari_df.empty and not iesiri_df.empty:
                plati_numerar += intrari_df["TOTAL"].sum()
                cheltuieli = intrari_df.loc[intrari_df["TIP"] == "C"]
                if not cheltuieli.empty:
                    plati_alte += cheltuieli["TOTAL"].sum()
                incasari += iesiri_df["TOTAL"].sum()

            start_date = NextDay(start_date)
            intrari_df = self.GetInputDfFromDate(start_date)
            iesiri_df = self.GetOutputDfFromDate(start_date)
        return plati_numerar, plati_alte, incasari

    def CreateAlteRow(self, row):
        return [row["DATA"].strftime("%d-%m-%Y"), row["NR_INTRARE"], f"Cheltuieli {row['DENUMIRE']}", 0, 0, row["TOTAL"]]

    def CreateNumerarRow(self, row):
        return [row["DATA"].strftime("%d-%m-%Y"), row["NR_INTRARE"], f"Cumparare marfa {row['DENUMIRE']}", 0, row["TOTAL"], 0]
    
    def CreateIncasariRow(self, row):
        return [row["DATA"].strftime("%d-%m-%Y"), row["NR_IESIRE"], f"Vanzare marfa {row['DENUMIRE']}", row["TOTAL"], 0, 0]


class ManagementGenerator(ReportGenerator):
    
    COLUMNS = ["Numar document", "Explicatii", "Valoare lei (Marfuri)"]
    OUTPUT_FILE = f"raport_de_gestiune_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
    NAME = "Raport de gestiune"

    def __init__(self, start_date, sold_precedent):
        ReportGenerator.__init__(self)
        ManagementGenerator.INSTANCE = self
        self.start_date = pd.to_datetime(start_date)
        self.sold_precedent = float(sold_precedent)
    
    def Generate(self, start_date, stop_date):
        """
        Intrari, Iesiri and Produse are needed.
        Two tables.
        First table. 
            Columns: Numar document (NIR asociat), Explicatii, Valoare lei (marfuri);
            At the beginning of the table, print Sold precedent.
            At the end of the table, print Total intrari + sold (sum of all Intrari values and Sold precedent).

        Second table columns: 
            Columns: same
            At the end of the table, print Total vanzari + iesiri (end sum of first table minus the sum of all Iesiri values)
        """
        sold = self.sold_precedent
        if self.start_date < start_date:
            sold = self.UpdateSold(self.start_date, start_date, self.sold_precedent)
        current_date = start_date
        intrari_df = self.GetInputDfFromDate(current_date)
        iesiri_df = self.GetOutputDfFromDate(current_date)

        while current_date <= stop_date:
            _out_list = list()
            # Add header.
            _out_list.append([f"Data: {current_date.strftime('%d-%m-%Y')}", "Sold precedent", sold])
            # Update sold value. Start and stop date are the same: current date.
            sold = self.UpdateSold(current_date, current_date, sold, use_iesiri=False)
            
            rows = intrari_df.apply(self.CreateIntrariRow, axis='columns')
            [_out_list.append(row) for row in rows if not rows.empty]

            # Add mid header.
            _out_list.append(["", "Total intrari + sold", sold])
            
            sold = self.UpdateSold(current_date, current_date, sold, use_intrari=False)
            rows = iesiri_df.apply(self.CreateIesiriRow, axis='columns')
            [_out_list.append(row) for row in rows if not rows.empty]

            # Add footer.
            _out_list.append(["", "Total vanzari + iesiri", sold])
            _out_list.append(["", "Sold final", sold])
                
            current_date = NextDay(current_date)
            intrari_df = self.GetInputDfFromDate(current_date)
            iesiri_df = self.GetOutputDfFromDate(current_date)
        
            if _out_list:
                self._out_df_list.append(pd.DataFrame(_out_list, columns=self.COLUMNS))
        
        self.SaveFile(self._out_df_list)
    
    def GetProductSumFromId(self, id_intrare):
        produse_df = ParserProduse.GetParser().GetDataWithIdIntrare(id_intrare)
        if produse_df.empty:
            return 0
        return produse_df.apply(lambda row: row["CANTITATE"] * row["PRET_VANZ"], axis='columns').sum()

    def UpdateSold(self, start_date, stop_date, sold, use_intrari=True, use_iesiri=True):
        intrari_df = self.GetInputDfFromDate(start_date)
        iesiri_df = self.GetOutputDfFromDate(start_date)
        
        while start_date <= stop_date:
            if not intrari_df.empty and not iesiri_df.empty:
                if use_intrari:
                    sold += intrari_df["ID_INTRARE"].apply(self.GetProductSumFromId).sum()
                if use_iesiri:
                    sold -= iesiri_df["TOTAL"].sum()

            start_date = NextDay(start_date)
            intrari_df = self.GetInputDfFromDate(start_date)
            iesiri_df = self.GetOutputDfFromDate(start_date)
            
        return sold
    
    def CreateIntrariRow(self, row):
        return [row["NR_NIR"], f"Cumparare marfa {row['DENUMIRE']}", self.GetProductSumFromId(row["ID_INTRARE"])]

    def CreateIesiriRow(self, row):
        return [row["NR_IESIRE"], f"Vanzare marfa {row['DENUMIRE']}", row["TOTAL"]]
