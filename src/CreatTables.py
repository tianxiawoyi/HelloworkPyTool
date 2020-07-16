import xlrd
import xlwt

table_type='textfile'  #表   textfile  orc
partition_flag=False
partition_col=''
partition_type=''

filename = r'D:\建表.xlsx'
data = xlrd.open_workbook(filename)  #文件名以及路径，如果路径或者文件名有中文给前面加一个r拜师原生字符。
kxname='STG_S0001.STG_S0001_SAPS4P'


table = data.sheet_by_index(0) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数



tableRcs=[]
distTable = {}
for i in range(0,nrows,1):
    # print(i)
    # print(table.row(i))  #返回由该行中所有的单元格对象组成的列表
    table_row=table.row(i)
    tableName=table_row[3].value
    # tableName_cn=table_row[4].value
    # table_key=tableName+'-'+tableName_cn    #中-英名字组成字典的key
    if tableName not in distTable.keys():
        tableRcs=[]
        distTable[tableName]=[]
    distTable[tableName].append(table.row(i))

print(distTable)
print(len(distTable))


row2 = 0
row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet("sheet1")
worksheet2 = workbook.add_sheet("sheet2")
style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')



for (k,v) in distTable.items():
    tableSum+=1
    tableName=k
    tableName_cn=v[0][4].value


    name=f'{kxname}_{tableName}'
    text=f"DROP TABLE IF EXISTS {name};\nCREATE TABLE {name} (\n"  #建表开头语句
    #print('tableName:'+tableName)
    #print('tableName_cn:'+tableName_cn)
    for i,tbr in enumerate(v):     # tbr表中每行
        coln=tbr[6].value
        ctype=tbr[8].value
        cCOMMENT=tbr[7].value
        dh=','
        if i==0: dh=' '#第一行去掉,号
        if len(coln)<30:coln+=' '*(30-len(coln))#字段长度不足30,补足空格,为了对齐好看
        rtext=f"{dh}{coln} \t string \t\t\t COMMENT'{cCOMMENT}' \t\t\t  --{ctype}\n"  #拼接表每行字段
        text+=rtext
    text += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    if table_type=='orc':text += 'PARTITIONED BY (PERIOD_WID STRING) \n'  #拼接 orc 加上分区 todo:待优化手动输入是否分区
    text += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS {table_type};"
    row += 1
    worksheet.write(row, 1, tableName)
    worksheet.write(row, 2, text)
    print(text)
    print(tableName)
    print('===================')
print('tableSum:'+str(tableSum))


# xlsSavePath = "xls/建表语句/建表语句3.xls"
# workbook.save(xlsSavePath)



