import xlwt
import xlrd
import random
filename=xlwt.Workbook()
sheet=filename.add_sheet("my_sheet")
for row in range(0,10):
        sheet.write(row,range(0,10))
filename.save("test.xls")
print "Done"
