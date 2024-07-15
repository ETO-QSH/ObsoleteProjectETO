
import os; import xlrd; from xlutils import copy; from List import *
while True:
    for Dir in Dict:
        try:
            Files = os.listdir(Dir)
            for i in Files:
                if os.path.splitext(i)[1] == '.xls':
                    filename = i
            workbook = xlrd.open_workbook((Dir+'\\{}').format(filename), formatting_info=False)
            sheet1 = workbook.sheet_by_name('总分及小题分')
            new_book = copy.copy(workbook)
            for t in List:
                x = sheet1.row_values(0).index('17T')
                y = sheet1.col_values(1).index(t[0])
                print(t[0], sheet1.cell_value(y, x))
                sheet = new_book.get_sheet(0)
                sheet.write(y, x, int(t[1]//5))
                new_book.save((Dir+'\\{}').format(filename))
            print('ok')
        except:
            pass
