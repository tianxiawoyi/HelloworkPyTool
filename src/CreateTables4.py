import xlrd
import xlwt
import os

### ## 根据一定格式的数据字典生成建表语句.. 生成的字段类型都是string ,   以及生成ods etl 语句
# todo     字段类型判断  针对股份SAP系统生成stg etl 是否接入(可以手动删除)  创建时间:2020/05/29改获取   包含关键词的字段(type,timesan,operate)  获取系统代码,

table_type='textfile'     #表默认格式
partition_flag='n' #是否是分区表
kxname='ODS_S0001.ODS_S0001_SAPS4P'

kxname_input=input('请输入系统名库名(回车默认 ODS_S0001.ODS_S0001_SAPS4P ):')
if kxname_input!='':kxname=kxname_input.upper()
print('系统名库名:'+kxname+'\n')

filePath=input('请输入文件地址(如 D:\建表sql\建表.xlsx) (尽量将文件路径复制过来避免输错):')
print('文件路径:'+filePath+'\n')

table_typeInput=input('请输入表存储类型(如textfile,orc - 回车默认textfile):')
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


# filePath = r'D:\建表sql\建表.xlsx'
partitionFlag = True if partition_flag.lower() =='y' else False  # 三目运算 h = "变量1" if a>b else "变量2"

filePathDirPath=os.path.abspath(os.path.dirname(filePath))  #获取文件的上级目录
creatSQL_DirPath=os.path.join(filePathDirPath,'createHQL')    #存放建表语句
creatSH_DirPath=os.path.join(filePathDirPath,'createSH')    #存放etl语句
if not os.path.exists(creatSQL_DirPath):os.makedirs(creatSQL_DirPath)
if not os.path.exists(creatSH_DirPath):os.makedirs(creatSH_DirPath)

data = xlrd.open_workbook(filePath)  #读取数据字典Excel文件
table = data.sheet_by_index(0) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数

tableRcs=[]
distTable = {}
for i in range(0,nrows,1):# 表名当字典的key,等于表名的那行数据加入value(数组).
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


row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet("sheet1")
# style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')  单元格样式

def stg_etl_text(tableName,col_text):
    """拼接股份stg表 etl语句"""
    text0='#!/bin/sh\n#作者:weidongbin\n#创建时间:2020/06/01\n'
    text1='''
    source ./init_config.sh
    sqoop import \\
    --connect "jdbc:sap://${sap_prod_host}:${sap_prod_port}?databaseName=${sap_prod_dbname}&instanceNumber=${sap_prod_instance}&reconnect=true&timeout=0" \\
    --driver com.sap.db.jdbc.Driver \\
    --username ${sap_prod_user} \\
    --password ${sap_prod_passwd} \\
    --delete-target-dir \\
    '''

    sap_prod_dbpath='${sap_prod_dbpath}'
    # tableName='bkpf'
    # col_text='Cast(MANDT As VARCHAR) AS MANDT , Cast(BUKRS As VARCHAR) AS BUKRS  '
    text2=f'''--target-dir /bd-os/zh_hfgf/hive/stg_s0001/stg_s0001_{sap_prod_dbpath}_{tableName} \\
    --query "select {col_text} from {sap_prod_dbpath}.{tableName} where 1=1 and \$CONDITIONS" \\
    '''

    text3='''--fields-terminated-by '\\001' \\
    --m 1 \\
    --lines-terminated-by '\\n' \\
    --null-string '\\\\N'  \\
    --null-non-string '\\\\N' \\
    --hive-drop-import-delims
    '''

    # print(text0+text1+text2+text3)
    return text0+text1+text2+text3


def writeETLText(tableName_jc,tableName,cols):
    if 'ODS_' in tableName.upper():
        odsTable = tableName
        cols_text=''
        for col in cols:cols_text += (col+'\n')
        cols_text += ",FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') as W_INSERT_DT\n"

        stgTable=odsTable.replace('ODS_','STG_').replace('ods_','STG_',)
        y_date = '${y_date}'
        hqlText=f"hive -e \"\ninsert overwrite table {odsTable} PARTITION (PERIOD_WID='{y_date}')\nselect\n{cols_text}\nfrom {stgTable} \nWHERE MANDT='800'\n;\n\n\""
        text=f"#!/bin/sh\n#ods(stg层数据格式转化及保留字段分区添加)\n#作者:\n#创建时间:2020/05/29\n\n#引入时间脚本\nsource ./get_date.sh\necho {y_date}\n\n\n{hqlText}"
        print(text)
        return text
    else:
        cols_text=''
        for col in cols:
            coln=col.strip()
            if col.startswith(','):coln=col[1:].strip()
            cols_text += f',Cast({coln} As VARCHAR) AS {coln} '
            if cols_text.startswith(','):cols_text=cols_text[1:]
        text = stg_etl_text(tableName_jc,cols_text)

        print(text)
        return text




for (k,v) in distTable.items():
    tableSum+=1
    tableName=k
    tableName_cn=v[0][4].value


    name = f'{kxname}_{tableName}'.upper()
    text = f"DROP TABLE IF EXISTS {name};\nCREATE TABLE {name} (\n"  #建表开头语句
    #print('tableName:'+tableName)
    #print('tableName_cn:'+tableName_cn)
    cols=[]
    for i,tbr in enumerate(v):     # tbr表中每行
        coln=tbr[6].value
        ctype=tbr[8].value
        cCOMMENT=tbr[7].value
        if coln.strip().startswith('.'): continue
        dh=','
        if i==0: dh=' '#第一行去掉,号
        if len(coln)<30:coln+=' '*(30-len(coln))#字段长度不足30,补足空格,为了对齐好看
        # rtext=f"{dh}{coln} \t {ctype} \t\t\t COMMENT'{cCOMMENT}'   \n"  #拼接表每行字段
        rtext=f"{dh}{coln} \t STRING \t\t\t COMMENT'{cCOMMENT}' \t\t\t \n"  #拼接表每行字段   --{ctype}
        text+=rtext
        # 添加字段进数组,为了写etl
        cols.append(f"{dh}{coln}")

    if 'ODS_' in (kxname.upper()): #是ODS表拼接W_INSERT_DT数据插入时间
        W_INSERT_DT='W_INSERT_DT'+' '*(30-len('W_INSERT_DT'))
        text += f",{W_INSERT_DT} \t STRING \t\t\t COMMENT'数据插入时间'\n"

    text += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    if partitionFlag: text += f'PARTITIONED BY ({partition_col} {partition_col_type}) \n'  #拼接 orc 加上分区
    # if table_type=='orc':text += 'PARTITIONED BY (PERIOD_WID STRING) \n'  #拼接 orc 加上分区
    text += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS {table_type};"
    row += 1
    worksheet.write(row, 1, tableName)
    worksheet.write(row, 2, text)  # 写建表 语句到Excel

    print('-------写建表语句---------------')
    print(text)
    print("tableName:"+tableName)
    tableFileName=kxname[10:]+"_"+tableName
    print("tableFileName:"+tableFileName)
    creatSQL_FilePath=os.path.join(creatSQL_DirPath,tableFileName+'.hql')
    with open(creatSQL_FilePath, mode='w',encoding='utf-8') as f:
        f.write(text)

    print('----------写ETL语句------------')
    ## 写ETL
    etlText = writeETLText(tableName,name,cols)
    worksheet.write(row, 3, etlText)  # 写etl 语句到Excel
    creatSH_FilePath=os.path.join(creatSH_DirPath,tableFileName+'.sh')
    with open(creatSH_FilePath, mode='w',encoding='utf-8') as f:
        f.write(etlText)
    print('=======================================================================')
print('tableSum:'+str(tableSum))


xlsSavePath = f"{creatSQL_DirPath}/建表语句.xls"
workbook.save(xlsSavePath)


exit_input=input('\n\n\n回车键退出!')
