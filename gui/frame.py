import wx
import wx.adv
import pandas as pd

from data.generator import JournalGenerator
from data.generator import ManagementGenerator
from utils import Info
from utils import Error


class MainFrame(wx.Frame):

    DATE_BUTTON = "Selecteaza data"
    MGMT_BUTTON = "Raport de gestiune"
    JOURNAL_BUTTON = "Jurnal de incasari si plati"
    BUTTONS = [DATE_BUTTON, MGMT_BUTTON, JOURNAL_BUTTON]

    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)

        self._wx_start_date = wx.DateTime.Now()
        self._wx_stop_date = wx.DateTime.Now()

        self.CreateMenuBar()
        self.CreatePanels()
        self.CreateButtons()
        self.CreateDatePickers()
        self.CreateTextBoxes()
        self.CreateGridBag()

        self.BindButtons()
        self.BindDatePickers()
        self.AddBorder()

    def CreateMenuBar(self):
        pass # TODO

    def CreatePanels(self):
        self.buttonPanel = wx.Panel(self)

    def CreateGridBag(self):
        self.grid = wx.GridBagSizer(3, 3)
        self.grid.Add(self.management_button, (1, 0), flag=wx.EXPAND)
        self.grid.Add(self.journal_button, (2, 0), flag=wx.EXPAND)
        self.grid.Add(self.startDateText, (0, 1), flag=wx.EXPAND)
        self.grid.Add(self.stopDateText, (0, 2), flag=wx.EXPAND)
        self.grid.Add(self.startPicker, (1, 1), flag=wx.EXPAND)
        self.grid.Add(self.stopPicker, (1, 2), flag=wx.EXPAND)

    def CreateButtons(self):
        self.management_button = wx.Button(self.buttonPanel, 0, MainFrame.MGMT_BUTTON)
        self.journal_button = wx.Button(self.buttonPanel, 1, MainFrame.JOURNAL_BUTTON)

        self.DisableReportButtons()
    
    def CreateDatePickers(self):
        self.startPicker = wx.adv.DatePickerCtrl(self.buttonPanel, wx.ID_ANY, wx.DefaultDateTime, style=wx.adv.DP_DROPDOWN)
        self.stopPicker = wx.adv.DatePickerCtrl(self.buttonPanel, wx.ID_ANY, wx.DefaultDateTime, style=wx.adv.DP_DROPDOWN)

    def BindButtons(self):
        self.management_button.Bind(wx.EVT_BUTTON, self.OnManagementButton)
        self.journal_button.Bind(wx.EVT_BUTTON, self.OnJournalButton)

    def BindDatePickers(self):
        self.startPicker.Bind(wx.adv.EVT_DATE_CHANGED, self.OnStartDateChanged)
        self.stopPicker.Bind(wx.adv.EVT_DATE_CHANGED, self.OnStopDateChanged)

    def AddBorder(self):
        self.border = wx.BoxSizer()
        self.border.Add(self.grid, 1, wx.ALL | wx.EXPAND, 5)
        self.buttonPanel.SetSizerAndFit(self.border)

    def CreateTextBoxes(self):
        self.startDateText = wx.StaticText(self.buttonPanel)
        self.startDateText.SetLabel("Data de start")

        self.stopDateText = wx.StaticText(self.buttonPanel)
        self.stopDateText.SetLabel("Data de stop")
        
    def OnManagementButton(self, event):
        ManagementGenerator.Instance().Generate(self._pd_start_date, self._pd_stop_date)
        Info("Generated management report.")
        infoDialog = wx.MessageDialog(self, "Raportul de gestiune a fost generat.", style=wx.OK)
        infoDialog.ShowModal()
        
    def OnJournalButton(self, event):
        start_date = pd.to_datetime(self._wx_start_date.Format("%Y%m%d"))
        stop_date = pd.to_datetime(self._wx_stop_date.Format("%Y%m%d"))
        JournalGenerator.Instance().Generate(self._pd_start_date, self._pd_stop_date)
        Info("Generated input/output journal.")
        infoDialog = wx.MessageDialog(self, "Jurnalul de incasari si plati a fost generat.", style=wx.OK)
        infoDialog.ShowModal()

    def OnStartDateChanged(self, event):
        date_val = event.GetDate()
        if date_val.IsLaterThan(wx.DateTime.Now()):
            color = wx.Colour(255, 0, 0)
            warningDateDialog = wx.MessageDialog(self, "Data de start selectata depaseste ziua curenta.", style=wx.OK)
            warningDateDialog.ShowModal()
            self.DisableReportButtons()
        elif date_val.IsLaterThan(self._wx_stop_date):
            color = wx.Colour(255, 0, 0)
            warningDateDialog = wx.MessageDialog(self, "Data de start selectata depaseste data de stop.", style=wx.OK)
            warningDateDialog.ShowModal()
            self.DisableReportButtons()
        else:
            self.EnableReportButtons()
        
        self._wx_start_date = date_val
        self._pd_start_date = pd.to_datetime(self._wx_start_date.Format("%Y%m%d"))
        Info("Start date: {}.".format(self._pd_start_date))

    def OnStopDateChanged(self, event):
        date_val = event.GetDate()
        if date_val.IsEarlierThan(self._wx_start_date):
            color = wx.Colour(255, 0, 0)
            warningDateDialog = wx.MessageDialog(self, "Data de stop selectata este mai mica decat data de start.", style=wx.OK)
            warningDateDialog.ShowModal()
            self.DisableReportButtons()
        elif date_val.IsLaterThan(wx.DateTime.Now()):
            date_val = wx.DateTime.Now()
        else:
            self.EnableReportButtons()
        self._wx_stop_date = date_val
        self._pd_stop_date = pd.to_datetime(self._wx_stop_date.Format("%Y%m%d"))
        Info("Stop date: {}.".format(self._pd_stop_date))

    def DisableReportButtons(self):
        self.management_button.Disable()
        self.journal_button.Disable()

    def EnableReportButtons(self):
        self.management_button.Enable()
        self.journal_button.Enable()


class Calendar(wx.Frame):

    def __init__(self, parent_frame, *args, **kargs):
        wx.Frame.__init__(self, *args, **kargs)

        self.parent = parent_frame
        self.cal = wx.adv.CalendarCtrl(self, 10, wx.DateTime.Now())
        self.cal.Bind(wx.adv.EVT_CALENDAR, self.OnDate)
        self.Show()

    def OnDate(self, event):
        self.parent.SetStartDate(self.cal.GetDate())
        self.Close()
