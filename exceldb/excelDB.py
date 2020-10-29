from openpyxl import Workbook
from datetime import datetime

#엑셀

class excel:
    def __init__(self):
        self.wb = Workbook()
        self.sheet = self.wb.active
        self.database_name = str(datetime.today().month)+'_'+str(datetime.today().day)+\
               '_'+str(datetime.today().hour)+'_'+str(datetime.today().minute)+'_'+'dataBase.xlsx'

    def post_excel(self, list):
        self.sheet.append(list)
        self.wb.save()

