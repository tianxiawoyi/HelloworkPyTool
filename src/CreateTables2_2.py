import xlrd
import xlwt
import os

## 根据一定格式的数据字典生成建表语句.. 生成的字段类型是表格中的
# todo     字段类型判断   是否接入(可以手动删除)   生成etl语句   包含关键词的字段(type,timesan,operate)

table_type='textfile'     #表默认格式
partition_flag='n' #是否是分区表
kxname='ODS_S0001.ODS_S0001_SAPS4P'

kxname_input=input('请输入系统名库名(回车默认 ODS_S0001.ODS_S0001_SAPS4P ):')
if kxname_input!='':kxname=kxname_input.upper()
print('统名库名:'+kxname+'\n')

filePath=input('请输入文件地址(如 D:\数据字典.xlsx) (尽量将文件路径复制过来避免输错):')
print('文件路径:'+filePath+'\n')

table_typeInput=input('请输入表存储类型(textfile或orc - 回车默认textfile):')
if table_typeInput!='':table_type=table_typeInput
print('表存储格式:'+table_type+'\n')

flag_input=input('请输入是否是分区表(y/n)(回车默认n):')
if flag_input!='':partition_flag=flag_input
print('是否是分区表:'+partition_flag+'\n')


partition_col='PERIOD_WID'
partition_col_type='STRING'
if partition_flag.lower() =='y':
    col_input=input('请输入分区字段(回车默认PERIOD_WID):')
    if col_input!='':partition_col=col_input
    print('分区字段:'+partition_col)

    type_input=input('请输入分区字段类型(回车默认STRING):')
    if type_input!='':partition_col_type=type_input
    print('分区字段类型:'+partition_col_type)



# table_type='textfile'  #表   textfile  orc
partitionFlag = True if partition_flag.lower() =='y' else False  # 三目运算 h = "变量1" if a>b else "变量2"
# partition_col=''
# partition_type=''

# filePath = r'D:\建表sql\建表.xlsx'

filePathDirPath=os.path.abspath(os.path.dirname(filePath))
creatSQL_DirPath=os.path.join(filePathDirPath,'createHQL')    #存放建表语句
if not os.path.exists(creatSQL_DirPath):os.makedirs(creatSQL_DirPath)

data = xlrd.open_workbook(filePath)  #文件名以及路径，如果路径或者文件名有中文给前面加一个r拜师原生字符。



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


# row2 = 0
row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet("sheet1")
# worksheet2 = workbook.add_sheet("sheet2")
# style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')



for (k,v) in distTable.items():
    tableSum+=1
    tableName=k
    tableName_cn=v[0][4].value


    name = f'{kxname}_{tableName}'.upper()
    text = f"DROP TABLE IF EXISTS {name};\nCREATE TABLE {name} (\n"  #建表开头语句
    #print('tableName:'+tableName)
    #print('tableName_cn:'+tableName_cn)
    for i,tbr in enumerate(v):     # tbr表中每行
        coln=tbr[6].value
        ctype=tbr[8].value
        cCOMMENT=tbr[7].value
        dh=','
        if i==0: dh=' '#第一行去掉,号
        if len(coln)<30:coln+=' '*(30-len(coln))#字段长度不足30,补足空格,为了对齐好看
        # rtext=f"{dh}{coln} \t STRING \t\t\t COMMENT'{cCOMMENT}' \t\t\t  --{ctype}\n"  #拼接表每行字段
        rtext=f"{dh}{coln} \t {ctype} \t\t\t COMMENT'{cCOMMENT}' \n"  #拼接表每行字段
        text+=rtext
    if 'ODS_' in (kxname.upper()): #是ODS表拼接W_INSERT_DT数据插入时间
        W_INSERT_DT='W_INSERT_DT'+' '*(30-len('W_INSERT_DT'))
        text += f",{W_INSERT_DT} \t STRING \t\t\t COMMENT'数据插入时间'\n"
    text += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    if partitionFlag: text += f'PARTITIONED BY ({partition_col} {partition_col_type}) \n'  #拼接 orc 加上分区
    # if table_type=='orc':text += 'PARTITIONED BY (PERIOD_WID STRING) \n'  #拼接 orc 加上分区 todo:待优化手动输入是否分区
    text += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS {table_type};"
    row += 1
    worksheet.write(row, 1, tableName)
    worksheet.write(row, 2, text)
    print(text)
    print('----------------------')
    print("tableName:"+tableName)
    tableFileName=kxname[10:]+"_"+tableName
    print("tableFileName:"+tableFileName)


    creatSQL_FilePath=os.path.join(creatSQL_DirPath,tableFileName+'.hql')
    with open(creatSQL_FilePath, mode='w',encoding='utf-8') as f:
        f.write(text)

    print('=======================================================================')
print('tableSum:'+str(tableSum))


xlsSavePath = f"{creatSQL_DirPath}/建表语句.xls"
workbook.save(xlsSavePath)


exit_input=input('\n\n\n回车键退出!')
