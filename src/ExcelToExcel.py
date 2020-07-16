import xlrd
from xlrd import xldate_as_tuple
import datetime
import xlwt

#openpyxl-可以读写XLSX、XLSM文件
#xlwt-用来写xls文件，是python-excal的三大模块
#xlrd-用来读取xls文件，是python-excel的三大模块  xlrd读取(xlsx)日期格式单元格的会有问题

filename = r'D:\股份OA.xlsx'
# filename = r'C:\Users\TXWY\Desktop\数据湖\9数据管理\房产开发\股份OA\10-ZY-OA-OA（股份）\10-ZY-OA-OA（股份）\5-V71数据字典.xlsx'
data = xlrd.open_workbook(filename)  #文件名以及路径，如果路径或者文件名有中文给前面加一个r拜师原生字符。


#以下三个函数都会返回一个xlrd.sheet.Sheet()对象
# table = data.sheets()[0]          #通过索引顺序获取
# table = data.sheet_by_name()#通过名称获取
# table = data.sheet_by_index(0) #通过索引顺序获取
# names = data.sheet_names()    #返回book中所有工作表的名字
# data.sheet_loaded(sheet_name or indx)   # 检查某个sheet是否导入完毕

# 行操作
# nrows = table.nrows  #获取该sheet中的有效行数
# table.row(rowx)  #返回由该行中所有的单元格对象组成的列表
# table.row_slice(rowx)  #返回由该列中所有的单元格对象组成的列表
# table.row_types(rowx, start_colx=0, end_colx=None)    #返回由该行中所有单元格的数据类型组成的列表
# table.row_values(rowx, start_colx=0, end_colx=None)   #返回由该行中所有单元格的数据组成的列表
# table.row_len(rowx) #返回该列的有效单元格长度

#列(colnum)的操作
# ncols = table.ncols   #获取列表的有效列数
# table.col(colx, start_rowx=0, end_rowx=None)  #返回由该列中所有的单元格对象组成的列表
# table.col_slice(colx, start_rowx=0, end_rowx=None)  #返回由该列中所有的单元格对象组成的列表
# table.col_types(colx, start_rowx=0, end_rowx=None)    #返回由该列中所有单元格的数据类型组成的列表
# table.col_values(colx, start_rowx=0, end_rowx=None)   #返回由该列中所有单元格的数据组成的列表

# 单元格的操作
# table.cell(rowx,colx)   #返回单元格对象
# table.cell_type(rowx,colx)    #返回单元格中的数据类型
# table.cell_value(rowx,colx)   #返回单元格中的数据
# table.cell_xf_index(rowx, colx)   # 暂时还没有搞懂

def isEmptyRows(row):
    """判断Excel中行是否空行"""
    isEmpty=True
    for cell in row:
        if cell.value!='':
            # print('--------------------并非空行:'+cell.value)
            isEmpty=False
            break
    if isEmpty: print('--------------------有空行:')
    return isEmpty


tableRcs=[]
tableNum = 0
distTable = {}
table = data.sheet_by_index(0) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数

for i in range(0,nrows,1):
    # print(i)
    # print(table.row(i))  #返回由该行中所有的单元格对象组成的列表
    if table.cell_value(i,0)=='表分割':
        tableNum+=1
        tableRcs=[]
        continue
    if isEmptyRows(table.row(i)):continue  # table.row(i)是空行的话不要
    tableRcs.append(table.row(i))
    distTable[tableNum]=tableRcs

print(distTable)
print(len(distTable))

row2 = 0
row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet("sheet1")
worksheet2 = workbook.add_sheet("sheet2")
style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')

for index,tb in enumerate(distTable.values()):  # tb个表(一个数组(每行数据))
    if tb[0][0].value!='名称' or tb[1][0].value!='注释' or  tb[2][0].value!='名称':
        print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--++-+-+-+-+-手动导表:')
        row2 = row2+2  #每表之间格个2空行
        # 不符合规则的表的单元格,写入另一个sheet中
        for i2,tbr2 in enumerate(tb):     # tbr表中行
            row2 = row2+1
            for j2,cell2 in enumerate(tbr2):
                print(cell2.value)
                worksheet2.write(row2, j2 + 5, label=(str(cell2.value)).strip())  # strip()去掉两边空格 ,第6列开始
        continue
    tableSum+=1
    tableName=tb[0][1].value
    tableName_cn=tb[1][1].value
    print('tableName:'+tableName)
    print('tableName_cn:'+tableName_cn)
    if index%2!=0:
        for i,tbr in enumerate(tb):     # tbr表中行
            if i<3: continue
            row = row+1
            worksheet.write(row, 3, label=tableName.strip())
            worksheet.write(row, 4, label=tableName_cn.strip())
            for j,cell in enumerate(tbr):
                print(cell.value)
                worksheet.write(row, j + 5, label=(str(cell.value)).strip())  # strip()去掉两边空格 ,第6列开始
    else:
        for i,tbr in enumerate(tb):     # tbr表中行
            if i<3: continue
            row = row+1
            worksheet.write(row, 3, label=tableName.strip(),style = style)
            worksheet.write(row, 4, label=tableName_cn.strip(),style = style)
            for j,cell in enumerate(tbr):
                print(cell.value)
                worksheet.write(row, j + 5, label=(str(cell.value)).strip(),style = style)  # strip()去掉两边空格 ,第6列开始
                #todo 如果第五列后(+3列)有数据就写到第四列中,有点难搞,不管
    print('===================')

print('tableSum:'+str(tableSum))
xlsSavePath = "xls/股份OA/OA7.xls"
workbook.save(xlsSavePath)

