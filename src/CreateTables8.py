import xlrd
import xlwt
import os
import time
import configparser
#openpyxl-可以读写XLSX、XLSM文件
#xlwt-用来写xls文件，是python-excal的三大模块
#xlrd-用来读取xls文件，是python-excel的三大模块  xlrd读取(xlsx)日期格式单元格的会有问题


# todo      /开头的字段     , 字段注释太长换行了,去掉换行符  , 标出包含关键字的表
# 字段类型判断转换(不够完善)在配置文件中定制
header=""" 
************************** 欢迎使用STG,ODS批量建表语句生成工具 ************************************
    
    version:v2.0
    author:weidongbin
    createtime:2020/05/29
    updatetime:2020/06/06
    email:wdb_workspace@126.com
    1.根据一定格式的数据字典生成stg,ods建表语句, 以及生成ods .sh脚本语句,股份SAP系统stg .sh脚本语句
    2.空字段,.开头的字段过滤不进行生成  
    3.sh脚本 创建时间获取当前时间, 作者
    4.是否接入判断; 系统代码,库名获取   
    5.stg生成的字段类型都是string;
      ods.hql文件的建表语句中生成的字段类型可以选择:(1/2/3/4)
      1).都是string 2).数据字典文件中字段类型(手动转化好) 3).用户自定义转化规则 4).工具内置转化 
    6.['TYPE','TIMESTAMP','OPERATION']等关键词字段加个下划线_   
    7.指定系统代码生成, 指定stg sqoop语句的target-dir  
    8.交互式参数改为配置文件参数模式  
    
*************** 欢迎使用STG,ODS批量建表语句生成工具,有任何问题提议建议可以Email ***********************
\n
"""
print(header)

import sys
def my_excepthook(exc_type, exc_value, tb):
    msg = ' Traceback (most recent call last):\n'
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        msg += '   File "%.500s", line %d, in %.500s\n' % (filename, lineno, name)
        tb = tb.tb_next
    msg += ' %s: %s\n' %(exc_type.__name__, exc_value)
    print("\n\n\n\n\n\n\n\n----------程序出现异常:")
    print(msg)
    exit_input=input('\n\n\n回车键退出!\n\n\n')
sys.excepthook = my_excepthook

def tf2xhx(strText):
    """驼峰命名转下划线 'ss Gds Js Dvc Gz' -->'ss _gds _js _dvc _gz'"""
    # 方式一
    import re
    return re.sub(r'[A-Z]',lambda x:f'_{x.group().lower()}',strText)
    # strText= 'ss Gds Js Dvc Gz'  -->'ss _gds _js _dvc _gz'
    # 方式二
    # print('前:'+strText)
    # s = set()
    # for i, ch in enumerate(strText):
    #     if ch.isupper():s.add(ch)
    # for i, ch in enumerate(s):
    #     strText = strText.replace(ch, f'_{ch.lower()}')
    # print('后:'+strText)
    # return strText
    #coln= addXHX(tbr[6].value)


def sourceColType2HiveColType(sourceColType):
    """
        源数据数据库字段类型转换hive字段类型
        #  %int%  --->bigint
        #  MONEY,FLOAT,DECIMAL,NUMERIC,DOUBLE  -->  DECIMAL(30,8)
        #   others    --->  STRING
    """
    sourceColType = sourceColType.upper()
    if 'INT' in sourceColType:HiveColType='BIGINT'
    elif ('MONEY' in sourceColType) \
        or ('FLOAT' in sourceColType) \
        or ('DECIMAL' in sourceColType) \
        or ('NUMERIC' in sourceColType) \
        or ('DOUBLE' in sourceColType):
        HiveColType='DECIMAL(30,8)'
    else:HiveColType='STRING'
    return HiveColType

def sourceColType2HiveWithConfig(sourceColType,config):
    """根据配置文件的原字段类型与hive转换规则转换,不在范围内的都转成string"""
    sourceColType = (sourceColType.strip().lower().split('('))[0]
    for items in config.items('col_type_tran_rule'):
        if sourceColType in items[1].strip().lower().split(','):
            return items[0]
    return 'string'


def stg_etl_text(tableName_short, col_text):
    """拼接股份stg表 etl语句"""
    text0='#!/bin/sh\n#作者:{sh_author}\n#创建时间:{creatTime}\n'.format(sh_author=sh_author, creatTime=creatTime)
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
    text2=f'''--target-dir {target_dir}_{sap_prod_dbpath}_{tableName_short.lower()} \\
    --query "select {col_text} from {sap_prod_dbpath}.{tableName_short} where 1=1 and \$CONDITIONS" \\
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

def getETLText(tableName_short,odsName,stgName,cols_stg_etl_text,cols_ods_etl_text):
    y_date = '${y_date}'
    hqlText=f"hive -e \"\ninsert overwrite table {odsName} PARTITION (PERIOD_WID='{y_date}')\nselect\n{cols_ods_etl_text}\nfrom {stgName} \n;\n\n\""  #\nWHERE MANDT='800'
    odsEtlText=f"#!/bin/sh\n#ods(stg层数据格式转化及保留字段分区添加)\n#作者:{sh_author}\n#创建时间:{creatTime}\n\n#引入时间脚本\nsource ./get_date.sh\necho {y_date}\n\n\n{hqlText}"

    stgEtlText = stg_etl_text(tableName_short, cols_stg_etl_text)

    return (stgEtlText,odsEtlText)

def getCreatTableText(tableName_cn,odsName,stgName, cols_ods_table_text,cols_stg_table_text):
    stg_createTableText = f"DROP TABLE IF EXISTS {stgName};\nCREATE TABLE {stgName} (\n"  #建表开头语句
    stg_createTableText +=cols_stg_table_text  #拼接所有字段
    stg_createTableText += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    # if partitionFlag: createTableText += f'PARTITIONED BY ({partition_col} {partition_col_type}) \n'  #拼接分区
    stg_createTableText += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS textfile;"

    ods_createTableText = f"DROP TABLE IF EXISTS {odsName};\nCREATE TABLE {odsName} (\n"  #建表开头语句
    ods_createTableText +=cols_ods_table_text  #拼接所有字段
    ods_createTableText += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    ods_createTableText += f'PARTITIONED BY (PERIOD_WID STRING) \n'  #拼接分区
    ods_createTableText += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS orc;"

    return (stg_createTableText,ods_createTableText)


def write_etl(etlText, name,creatSH_DirPath):
    """写etlText到.sh文件"""
    # tableFileName=f'{kxname}_{system_code}_{library_name}_{tableName_short}'
    tableFileName=name.split('.')[1]
    creatSH_FilePath=os.path.join(creatSH_DirPath,tableFileName+'.sh')
    with open(creatSH_FilePath, mode='w',encoding='utf-8',newline='\n') as f:
        f.write(etlText)
    print("--sh----tableFileName:"+tableFileName)
    print(etlText)
    return etlText

def write_createTable(createTableText,name,creatSQL_DirPath ):
    """写建表 到.hql文件"""
    tableFileName=name.split('.')[1]
    creatSQL_FilePath=os.path.join(creatSQL_DirPath,tableFileName+'.hql')
    with open(creatSQL_FilePath, mode='w',encoding='utf-8',newline='\n') as f:
        f.write(createTableText)

    print("--hql----tableFileName:"+tableFileName)
    print(createTableText)
    return createTableText

def writeToExcel(tableName_short,createtableText,etlText,stgName,odsName,row):
    stgTableFileName=stgName.split('.')[1]
    stgSheet.write(row, 1, tableName_short.lower())
    stgSheet.write(row, 2, tableName_short.upper())
    stgSheet.write(row, 3, stgTableFileName)
    stgSheet.write(row, 4, createtableText[0])    # 写建表 语句到Excel
    stgSheet.write(row, 5, etlText[0])  # 写etl 语句到Excel

    odsTableFileName=odsName.split('.')[1]
    odsSheet.write(row, 1, tableName_short.lower())
    odsSheet.write(row, 2, tableName_short.upper())
    odsSheet.write(row, 3, odsTableFileName)
    odsSheet.write(row, 4, createtableText[1])    # 写建表 语句到Excel
    odsSheet.write(row, 5, etlText[1])  # 写etl 语句到Excel

def writeKeyWordTableToExcel(hasKeyWordTable):
    """将记录包含keywords的表写到Excel keyWordsSheet """
    row=0
    for v in hasKeyWordTable:
        row+=1
        vv=v.split('-')
        keyWordsSheet.write(row, 1, v)
        keyWordsSheet.write(row, 2, vv[0])
        keyWordsSheet.write(row, 3, vv[1])

configPath=r'E:\Develop\ideaWorkPath\Python\project\Hellowork\src\config\config.ini'
configPath_input=input('请输入配置文件所在路径:\n(回车默认:E:\Develop\ideaWorkPath\Python\project\Hellowork\src\config\config.ini)\n')
if configPath_input!='':configPath=configPath_input.strip()
print('配置文件所在路径:'+configPath+'\n')

creatTime=time.strftime("%Y/%m/%d", time.localtime())   # creatTime='2020/06/01'
keywords=['TYPE','TIMESTAMP','OPERATION']

config = configparser.ConfigParser()   #  实例化configParser对象
config.read(configPath, encoding='utf_8')  # -read读取ini文件
paramGroup='param'
#关键词字段,生成时在后面添加一个下划线
keywords=config.get('param', 'keywords').upper().split(',')
filePath=config.get(paramGroup, 'filePath')
#生成的表层级 ODS/STG
#kxname=config.get(paramGroup, 'kxname')
#要生成的系统代码例如S0001(空为全部
sys_code=config.get(paramGroup, 'sys_code')
#ods表字段类型生成方式
#ods表字段类型是否转换1/2/3  1.都是string 2.数据字典文件中字段类型(手动转化好) 3.工具转化[%int%--->bigint;MONEY,FLOAT,DECIMAL,NUMERIC,DOUBLE-->DECIMAL(30,8);others-->STRING]; stg的还是 String类型
odsTableColTran_switch=config.get(paramGroup, 'odsTableColTran_switch')
#stg sqoop target-dir 参数例: /bd-os/zh_hfgf/hive/stg_s0001/stg_s0001
target_dir=config.get(paramGroup, 'target_dir')
#表存储格式textfile,orc...
#table_type=config.get(paramGroup, 'table_type')
#生成的sh文件脚本语句中的作者例如xiaoming
sh_author=config.get(paramGroup, 'sh_author')
#是否是分区表y/n
#partition_flag=config.get(paramGroup, 'partition_flag')
#分区字段PERIOD_WID
#partition_col=config.get(paramGroup, 'partition_col')
#分区字段类型例如STRING...
#partition_col_type=config.get(paramGroup, 'partition_col_type')
#数据字典内容所在表格的sheet位置,从0开始算
sheet_index=config.getint(paramGroup, 'sheet_index')
#系统代码 所在表格的列,从0开始算
sys_code_index=config.getint(paramGroup, 'sys_code_index')
#是否接入 所在表格的列,从0开始算
isAccess_index=config.getint(paramGroup, 'isAccess_index')
#表英文名 所在表格的列,从0开始算
tablename_short_index=config.getint(paramGroup, 'tablename_short_index')
#表中文名 所在表格的列,从0开始算
tablename_short_cn_index=config.getint(paramGroup, 'tablename_short_cn_index')
#库名 所在表格的列,从0开始算
library_name_index=config.getint(paramGroup, 'library_name_index')
#字段名 所在表格的列,从0开始算
col_index=config.getint(paramGroup, 'col_index')
#字段描述 所在表格的列,从0开始算
col_comment_index=config.getint(paramGroup, 'col_comment_index')
#数据类型 所在表格的列,从0开始算
col_type_index=config.getint(paramGroup, 'col_type_index')
#文件生成保存的目录例如 D:\建表生成
# save_path=config.get(paramGroup, 'save_path')

# table_type='textfile'     #表默认格式
# partition_flag='n' #是否是分区表
# odsTableColTran_switch= '1' #ods表字段类型是否转换
# kxname='ODS'   # kxname='ODS_S0001.ODS_S0001_SAPS4P'
# sh_author=''  # weidongbin
#
# partition_col='PERIOD_WID'
# partition_col_type='STRING'
# target_dir='/bd-os/zh_hfgf/hive/stg_s0001/stg_s0001'
# sys_code=''
#
# filePath=input('请输入文件地址(如 D:\建表sql\建表.xlsx) (尽量将文件路径复制过来避免输错):')
# print('文件路径:'+filePath+'\n')
#
# kxname_input=input('请输入生成的表层级(回车默认 ODS ):')
# if kxname_input!='':kxname=kxname_input.upper()
# print('生成的表层级:'+kxname+'\n')
#
# sys_code_input=input('请输入系统代码(回车默认 全部):')
# if sys_code_input!='':sys_code=sys_code_input.upper().strip()
# print('系统代码:'+sys_code+'\n')
#
#
# if kxname=='ODS':
#     odsTableColTran_input=input('ods表字段类型生成方式:1.都是string 2.数据字典文件中字段类型(手动转化好) 3.工具转化\n[%int%--->bigint;MONEY,FLOAT,DECIMAL,NUMERIC,DOUBLE-->DECIMAL(30,8)\n(1/2/3 - 回车默认1:STRING类型):')
#     if odsTableColTran_input!='':odsTableColTran_switch=odsTableColTran_input
#     print('ods表字段类型生成方式:' + odsTableColTran_switch + '\n')
# if kxname=='STG':
#     target_dir_input=input('请输入stg target-dir 参数(回车默认:/bd-os/zh_hfgf/hive/stg_s0001/stg_s0001):')
#     if target_dir_input!='':target_dir=target_dir_input.lower()
#     print('target-dir 参数:'+target_dir+'\n')
#
# table_typeInput=input('请输入表存储类型(如textfile,orc - 回车默认textfile):')
# if table_typeInput!='':table_type=table_typeInput
# print('表存储格式:'+table_type+'\n')
#
#
# sh_authorInput=input('请输入生成的sh文件脚本语句中的作者(回车默认空''):')
# if sh_authorInput!='':sh_author=sh_authorInput
# print('生成的sh文件脚本语句中的作者:'+sh_author+'\n')
#
#
# flag_input=input('请输入是否是分区表(y/n)(回车默认n):')
# if flag_input!='':partition_flag=flag_input
# print('是否是分区表:'+partition_flag+'\n')
#
# if partition_flag.lower() =='y':
#     col_input=input('请输入分区字段(回车默认PERIOD_WID):')
#     if col_input!='':partition_col=col_input
#     print('分区字段:'+partition_col)
#
#     type_input=input('请输入分区字段类型(回车默认STRING):')
#     if type_input!='':partition_col_type=type_input
#     print('分区字段类型:'+partition_col_type)


# filePath = r'D:\建表sql\建表.xlsx'
#partitionFlag = True if partition_flag.lower() =='y' else False  # 三目运算 h = "变量1" if a>b else "变量2"

creatDate=time.strftime("(%Y.%m.%d %H.%M.%S)", time.localtime())   # creatDate='06.01 19.25.30'
filePathDirPath=os.path.abspath(os.path.dirname(filePath))  #获取文件的上级目录
generateTablePath=os.path.join(filePathDirPath,f'generateTable{creatDate}')

stgCreatSQL_DirPath=os.path.join(generateTablePath,f'stg_createHQL')    #存放stg建表语句
odsCreatSQL_DirPath=os.path.join(generateTablePath,f'ods_createHQL')    #存放ods建表语句
stgCreatSH_DirPath=os.path.join(generateTablePath,f'stg_createSH')    #存放stg etl语句
odsCreatSH_DirPath=os.path.join(generateTablePath,f'ods_createSH')    #存放ods etl语句
if not os.path.exists(stgCreatSQL_DirPath):os.makedirs(stgCreatSQL_DirPath)
if not os.path.exists(odsCreatSQL_DirPath):os.makedirs(odsCreatSQL_DirPath)
if not os.path.exists(stgCreatSH_DirPath):os.makedirs(stgCreatSH_DirPath)
if not os.path.exists(odsCreatSH_DirPath):os.makedirs(odsCreatSH_DirPath)

data = xlrd.open_workbook(filePath)  #读取数据字典Excel文件
table = data.sheet_by_index(sheet_index) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数

tableRcs=[]
distTable = {}  # 表名当字典的key,等于表名的那行数据加入value(数组).
for i in range(0,nrows,1):
    # 表名当字典的key,等于表名的那行数据加入value(数组).
    # print(i)
    # print(table.row(i))  #返回由该行中所有的单元格对象组成的列表
    table_row=table.row(i)
    tableName_short=table_row[tablename_short_index].value
    access_flag=table_row[isAccess_index].value  #是否接入
    if not 'Y'==access_flag.upper():continue
    system_code=table_row[sys_code_index].value.upper().strip()  #系统编码 S0001
    if ''!=sys_code and system_code!=sys_code: continue  #对特定系统代码生成:sys_code为空全部生成 (这个判断可以放到前面去)
    # tableName_cn=table_row[4].value
    table_key=tableName_short+'-'+system_code    #表名+系统编码组成字典的key
    if table_key not in distTable.keys():
        tableRcs=[]
        distTable[table_key]=[]
    distTable[table_key].append(table.row(i))

print(distTable)
print(len(distTable))


row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
stgSheet = workbook.add_sheet("stg表")
odsSheet = workbook.add_sheet("ods表")
keyWordsSheet = workbook.add_sheet("keyWords表")
# style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')  单元格样式

hasKeyWordTable=[] # 记录哪些表有keywords

for (k,v) in distTable.items():
    access_flag=v[0][isAccess_index].value  #是否接入
    if not 'Y'==access_flag.upper():continue

    system_code=v[0][sys_code_index].value.upper().strip()  #系统编码 S0001
    if ''!=sys_code and system_code!=sys_code: continue  #对特定系统代码生成:sys_code为空全部生成 (这个判断可以放到前面去)

    tableName_short=v[0][tablename_short_index].value.upper().strip()   # 表名 tableName_short=k
    tableName_cn=v[0][tablename_short_cn_index].value.upper().strip()   # 表名中文
    library_name=v[0][library_name_index].value.upper().strip()   # 库名

    tableSum+=1

    odsName = f'ODS_{system_code}.ODS_{system_code}_{library_name}_{tableName_short}'.upper()
    stgName = f'STG_{system_code}.STG_{system_code}_{library_name}_{tableName_short}'.upper()

    cols_stg_table_text=''
    cols_ods_table_text=''
    cols_stg_etl_text=''
    cols_ods_etl_text=''
    colnInitLen=30
    colnTypeInitLen=18
    for i,tbr in enumerate(v):     # tbr表中每行
        coln=tbr[col_index].value.upper()  # 字段
        ctype=tbr[col_type_index].value  # 字段类型
        cCOMMENT=tbr[col_comment_index].value  # 字段注释
        coln=coln.strip()
        if coln.startswith('.'): continue  #.开头的字段不要
        if ''==coln: continue  #空字段不要
        dh=','
        if i==0: dh=' '#第一行去掉,号
        if coln in keywords:
            coln+='_'  # 关键词字段加个下划线_
            hasKeyWordTable.append(f'{tableName_short}-{coln}')  #记录哪些表有keywords
        #-----------stg etl 每个字段的拼接  ----------------
        cols_stg_etl_text += f'{dh}Cast({tbr[col_index].value.upper().strip()} As VARCHAR) AS {coln} ' #第一个必须是原表的字段

        #-----------stg ods  createtable 每个字段的拼接----------------
        if len(coln)<colnInitLen:coln+=' '*(colnInitLen-len(coln))#字段长度不足30,补足空格,为了对齐好看
        cols_stg_table_text += f"{dh}{coln} \t STRING \t\t\t COMMENT'{cCOMMENT}' \t\t\t \n"  #拼接表每行字段   --{ctype}

        colnType='STRING'
        if '4'==odsTableColTran_switch.lower():colnType = sourceColType2HiveColType(ctype)
        elif '3'==odsTableColTran_switch.lower():colnType = sourceColType2HiveWithConfig(ctype,config)  # ods表进行转换字段类型,stg用string
        elif '2'==odsTableColTran_switch.lower():colnType = ctype
        else: colnType='STRING'
        if len(colnType)<colnTypeInitLen:colnType+=' '*(colnTypeInitLen-len(colnType))#字段类型长度不足23,补足空格,为了对齐好看
        cols_ods_table_text += f"{dh}{coln} \t {colnType} \t COMMENT'{cCOMMENT}' \t\t\t \n"  #拼接表每行字段   --{ctype}

        #-----------ods etl 每个字段的拼接----------------
        cols_ods_etl_text += f"{dh}{coln}\n"

    # W_INSERT_DT='W_INSERT_DT'+' '*(30-len('W_INSERT_DT'))
    cols_ods_table_text += f",{'W_INSERT_DT'+' '*(colnInitLen-len('W_INSERT_DT'))} \t STRING{' '*(colnTypeInitLen-len('STRING'))} \t COMMENT'数据插入时间'\n"
    cols_ods_etl_text += ",FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') as W_INSERT_DT\n"


    print('-------写建表语句---------------')
    creatTableText= getCreatTableText(tableName_cn,odsName,stgName, cols_ods_table_text,cols_stg_table_text)
    write_createTable(creatTableText[0],stgName,stgCreatSQL_DirPath)
    write_createTable(creatTableText[1],odsName,odsCreatSQL_DirPath)

    print('----------写ETL语句------------')
    etlText=getETLText(tableName_short,odsName,stgName,cols_stg_etl_text,cols_ods_etl_text)
    write_etl(etlText[0], stgName,stgCreatSH_DirPath)
    write_etl(etlText[1], odsName,odsCreatSH_DirPath)

    print('----------写进Excel------------')
    row += 1  #excel 写一个表中写一行加1
    writeToExcel(tableName_short,creatTableText,etlText,stgName,odsName,row)

    print('=======================================================================')
print('tableSum:'+str(tableSum))

writeKeyWordTableToExcel(hasKeyWordTable)
workbook.save(f"{generateTablePath}/建表语句.xls")

print(header)
print(f'文件生成位置:{generateTablePath} \n')
print('请检查生成的表数量及内容是否是您期望的.....查看下【库名】是否漏了.....')
print('请检查生成的表数量及内容是否是您期望的.....查看下【库名】是否漏了.....')
print('请检查生成的表数量及内容是否是您期望的.....查看下【库名】是否漏了.....')

exit_input=input('\n\n回车键退出!\n\n')


#exit_input=input('\n\n回车键退出!\n\n')
