import xlrd
import xlwt
import os
import time
import configparser

filePath=r'D:\建表sql\人力数据校验.xlsx'
data = xlrd.open_workbook(filePath)  #读取数据字典Excel文件
table = data.sheet_by_index(4) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数
# 获取工作表的有效列数
colNum = table.ncols


# table_row=table.row(i)
# table_col0=table.col(1)#--4月
# table_col1=table.col(3)

# table_col0=table.col(7)# 5月
# table_col1=table.col(9)

table_col0=table.col(11) # 12月
table_col1=table.col(13)

value_list0=[]
value_list1=[]

for v0 in table_col0:
    value_list0.append(str(v0.value).split('.')[0])

for v1 in table_col1:
    value_list1.append(str(v1.value).split('.')[0])

for a in value_list0:
    if a not in value_list1:
        print(a)




print(value_list0)
print(value_list1)

print("ods中没有这些员工")
for b in value_list1:
    if b not in value_list0:
        print(b)
