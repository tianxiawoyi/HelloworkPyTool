import xlrd
import xlwt
import os
import time

# todo      /开头的字段  ,说明可以用一个txt来   ,输入参数调整为配置文件 字段注释太长换行了,去掉换行符
# 有选择的对系统代码生成    重复表的问题     字段类型判断(不够完善),文件生成路径打印  exe报错能显示错误信息(使用全局异常钩子)
header=""" 
***************************** 欢迎使用建表语句生成工具 ***************************************
    
    version:v1.2
    author:weidongbin
    createtime:2020/05/29
    updatetime:2020/06/01
    email:wdb_workspace@126.com
    1.根据一定格式的数据字典生成stg,ods建表语句, 以及生成ods .sh脚本语句,股份SAP系统stg .sh脚本语句
    2.生成的字段类型都是string ,  空字段,.开头的字段排除
    3.sh脚本 创建时间获取当前时间, 作者
    4.是否接入判断; 系统代码,库名获取   update by 2020/06/01
    5.ods.hql文件的建表语句中生成的字段类型可以选择 1).都是string 2).数据字典文件中字段类型(手动转化好) 
        3).工具转化[%int%--->bigint;MONEY,FLOAT,DECIMAL,NUMERIC,DOUBLE-->DECIMAL(30,8)
        ;others-->STRING]; stg的还是 String类型   update by 2020/06/01
    6.['TYPE','TIMESTAMP','OPERATION']关键词字段加个下划线_   update by 2020/06/01
    7.指定系统代码生成, 指定stg sqoop语句的target-dir  update by 2020/06/03
    
************************ 欢迎使用建表语句生成工具,有任何问题提议建议可以Email ***********************
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
    """驼峰命名转下划线"""
    # strText= 'ssGdsJsDvcGz'
    print('前:'+strText)
    s = set()
    for i, ch in enumerate(strText):
        if ch.isupper():s.add(ch)
    for i, ch in enumerate(s):
        strText = strText.replace(ch, f'_{ch.lower()}')
    print('后:'+strText)
    return strText
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

def getETLText(tableName_short,name,cols_stg_etl_text,cols_ods_etl_text):
    etlText=''
    if 'ODS' in (kxname.upper()):
        stgName=name.replace('ODS_','STG_').replace('ods_','STG_',)
        y_date = '${y_date}'
        hqlText=f"hive -e \"\ninsert overwrite table {name} PARTITION (PERIOD_WID='{y_date}')\nselect\n{cols_ods_etl_text}\nfrom {stgName} \n;\n\n\""  #\nWHERE MANDT='800'
        etlText=f"#!/bin/sh\n#ods(stg层数据格式转化及保留字段分区添加)\n#作者:{sh_author}\n#创建时间:{creatTime}\n\n#引入时间脚本\nsource ./get_date.sh\necho {y_date}\n\n\n{hqlText}"
    else:
        etlText = stg_etl_text(tableName_short, cols_stg_etl_text)

    return etlText

def write_etl(tableName_short, etlText):
    tableFileName=f'{kxname}_{system_code}_{library_name}_{tableName_short}'  # tableFileName=kxname[10:]+"_"+tableName_short
    creatSH_FilePath=os.path.join(creatSH_DirPath,tableFileName+'.sh')
    with open(creatSH_FilePath, mode='w',encoding='utf-8',newline='\n') as f:
        f.write(etlText)
    print(etlText)
    return etlText

def write_createTable(tableName_short, cols_table_text):
    createTableText = f"DROP TABLE IF EXISTS {name};\nCREATE TABLE {name} (\n"  #建表开头语句
    createTableText +=cols_table_text  #拼接所有字段
    createTableText += f")COMMENT '{tableName_cn}' \n"  #拼接注释
    if partitionFlag: createTableText += f'PARTITIONED BY ({partition_col} {partition_col_type}) \n'  #拼接分区
    createTableText += f"ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\001'\nLINES TERMINATED BY '\\n'\nSTORED AS {table_type};"

    # 写建表 到.hql文件
    tableFileName=f'{kxname}_{system_code}_{library_name}_{tableName_short}'  # tableFileName=kxname[10:]+"_"+tableName_short
    creatSQL_FilePath=os.path.join(creatSQL_DirPath,tableFileName+'.hql')
    with open(creatSQL_FilePath, mode='w',encoding='utf-8',newline='\n') as f:
        f.write(createTableText)

    print("tableName_short:" + tableName_short)
    print("tableFileName:"+tableFileName)
    print(createTableText)
    return createTableText

def writeToExcel(tableName_short,createtableText,etlText, row):
    worksheet.write(row, 1, tableName_short.lower())
    worksheet.write(row, 2, tableName_short.upper())
    worksheet.write(row, 3, f'{kxname}_{system_code}_{library_name}_{tableName_short}')
    worksheet.write(row, 4, createtableText)    # 写建表 语句到Excel
    worksheet.write(row, 5, etlText)  # 写etl 语句到Excel


keywords=['TYPE','TIMESTAMP','OPERATION']
table_type='textfile'     #表默认格式
partition_flag='n' #是否是分区表
odsTableColTran_switch= '1' #ods表字段类型是否转换
kxname='ODS'   # kxname='ODS_S0001.ODS_S0001_SAPS4P'
sh_author=''  # weidongbin
creatTime=time.strftime("%Y/%m/%d", time.localtime())   # creatTime='2020/06/01'
partition_col='PERIOD_WID'
partition_col_type='STRING'
target_dir='/bd-os/zh_hfgf/hive/stg_s0001/stg_s0001'
sys_code=''

filePath=input('请输入文件地址(如 D:\建表sql\建表.xlsx) (尽量将文件路径复制过来避免输错):')
print('文件路径:'+filePath+'\n')

kxname_input=input('请输入生成的表层级(回车默认 ODS ):')
if kxname_input!='':kxname=kxname_input.upper()
print('生成的表层级:'+kxname+'\n')

sys_code_input=input('请输入系统代码(回车默认 全部):')
if sys_code_input!='':sys_code=sys_code_input.upper().strip()
print('系统代码:'+sys_code+'\n')


if kxname=='ODS':
    odsTableColTran_input=input('ods表字段类型生成方式:1.都是string 2.数据字典文件中字段类型(手动转化好) 3.工具转化\n[%int%--->bigint;MONEY,FLOAT,DECIMAL,NUMERIC,DOUBLE-->DECIMAL(30,8)\n(1/2/3 - 回车默认1:STRING类型):')
    if odsTableColTran_input!='':odsTableColTran_switch=odsTableColTran_input
    print('ods表字段类型生成方式:' + odsTableColTran_switch + '\n')
if kxname=='STG':
    target_dir_input=input('请输入stg target-dir 参数(回车默认:/bd-os/zh_hfgf/hive/stg_s0001/stg_s0001):')
    if target_dir_input!='':target_dir=target_dir_input.lower()
    print('target-dir 参数:'+target_dir+'\n')

table_typeInput=input('请输入表存储类型(如textfile,orc - 回车默认textfile):')
if table_typeInput!='':table_type=table_typeInput
print('表存储格式:'+table_type+'\n')


sh_authorInput=input('请输入生成的sh文件脚本语句中的作者(回车默认空''):')
if sh_authorInput!='':sh_author=sh_authorInput
print('生成的sh文件脚本语句中的作者:'+sh_author+'\n')


flag_input=input('请输入是否是分区表(y/n)(回车默认n):')
if flag_input!='':partition_flag=flag_input
print('是否是分区表:'+partition_flag+'\n')

if partition_flag.lower() =='y':
    col_input=input('请输入分区字段(回车默认PERIOD_WID):')
    if col_input!='':partition_col=col_input
    print('分区字段:'+partition_col)

    type_input=input('请输入分区字段类型(回车默认STRING):')
    if type_input!='':partition_col_type=type_input
    print('分区字段类型:'+partition_col_type)


# filePath = r'D:\建表sql\建表.xlsx'
partitionFlag = True if partition_flag.lower() =='y' else False  # 三目运算 h = "变量1" if a>b else "变量2"

creatDate=time.strftime("(%Y.%m.%d %H.%M.%S)", time.localtime())   # creatDate='06.01 19.25.30'
filePathDirPath=os.path.abspath(os.path.dirname(filePath))  #获取文件的上级目录
creatSQL_DirPath=os.path.join(filePathDirPath,f'generateTable{creatDate}\createHQL')    #存放建表语句
creatSH_DirPath=os.path.join(filePathDirPath,f'generateTable{creatDate}\createSH')    #存放etl语句
if not os.path.exists(creatSQL_DirPath):os.makedirs(creatSQL_DirPath)
if not os.path.exists(creatSH_DirPath):os.makedirs(creatSH_DirPath)

data = xlrd.open_workbook(filePath)  #读取数据字典Excel文件
table = data.sheet_by_index(0) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数

tableRcs=[]
distTable = {}  # 表名当字典的key,等于表名的那行数据加入value(数组).
for i in range(0,nrows,1):
    # 表名当字典的key,等于表名的那行数据加入value(数组).
    # print(i)
    # print(table.row(i))  #返回由该行中所有的单元格对象组成的列表
    table_row=table.row(i)
    tableName_short=table_row[3].value
    access_flag=table_row[2].value  #是否接入
    if not 'Y'==access_flag.upper():continue
    system_code=table_row[1].value.upper().strip()  #系统编码 S0001
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
worksheet = workbook.add_sheet("sheet1")
# style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')  单元格样式


for (k,v) in distTable.items():
    access_flag=v[0][2].value  #是否接入
    if not 'Y'==access_flag.upper():continue

    system_code=v[0][1].value.upper().strip()  #系统编码 S0001
    if ''!=sys_code and system_code!=sys_code: continue  #对特定系统代码生成:sys_code为空全部生成 (这个判断可以放到前面去)

    tableName_short=v[0][3].value.upper().strip()   # 表名 tableName_short=k
    tableName_cn=v[0][4].value.upper().strip()   # 表名中文
    library_name=v[0][5].value.upper().strip()   # 库名

    tableSum+=1
    # name = f'{kxname}_{tableName_short}'.upper()
    name = f'{kxname}_{system_code}.{kxname}_{system_code}_{library_name}_{tableName_short}'.upper()

    cols_table_text=''
    cols_stg_etl_text=''
    cols_ods_etl_text=''

    for i,tbr in enumerate(v):     # tbr表中每行
        coln=tbr[6].value  # 字段
        ctype=tbr[8].value  # 字段类型
        cCOMMENT=tbr[7].value  # 字段注释
        coln=coln.strip()
        if coln.startswith('.'): continue  #.开头的字段不要
        if ''==coln: continue  #空字段不要
        dh=','
        if i==0: dh=' '#第一行去掉,号
        if coln in keywords:coln+='_'  # 关键词字段加个下划线_
        #-----------stg etl 每个字段的拼接  ----------------
        cols_stg_etl_text += f'{dh}Cast({tbr[6].value.strip()} As VARCHAR) AS {coln} ' #第一个必须是原表的字段

        #-----------stg ods  createtable 每个字段的拼接----------------
        if len(coln)<30:coln+=' '*(30-len(coln))#字段长度不足30,补足空格,为了对齐好看
        colnType='STRING'
        if 'ODS' in (kxname.upper()) and '3'==odsTableColTran_switch.lower():colnType = sourceColType2HiveColType(ctype)  # ods表进行转换字段类型,stg用string
        elif 'ODS' in (kxname.upper()) and '2'==odsTableColTran_switch.lower():colnType = ctype
        else: colnType='STRING'
        cols_table_text += f"{dh}{coln} \t {colnType} \t\t\t COMMENT'{cCOMMENT}' \t\t\t \n"  #拼接表每行字段   --{ctype}

        #-----------ods etl 每个字段的拼接----------------
        cols_ods_etl_text += f"{dh}{coln}\n"

    if 'ODS' in (kxname.upper()): #是ODS表拼接W_INSERT_DT数据插入时间
        W_INSERT_DT='W_INSERT_DT'+' '*(30-len('W_INSERT_DT'))
        cols_table_text += f",{W_INSERT_DT} \t STRING \t\t\t COMMENT'数据插入时间'\n"
        cols_ods_etl_text += ",FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') as W_INSERT_DT\n"

    print('-------写建表语句---------------')
    createTableText = write_createTable(tableName_short, cols_table_text)

    print('----------写ETL语句------------')
    etlText=write_etl(tableName_short, getETLText(tableName_short,name,cols_stg_etl_text,cols_ods_etl_text))

    print('----------写进Excel------------')
    row += 1  #excel 写一个表中写一行加1
    writeToExcel(tableName_short,createTableText,etlText,row)

    print('=======================================================================')
print('tableSum:'+str(tableSum))

xlsSavePath = f"{creatSQL_DirPath}/{kxname}建表语句.xls"
workbook.save(xlsSavePath)

print(header)
print(f'\n文件生成位置:\n{creatSQL_DirPath}\n{creatSH_DirPath} ')
print('\n请检查生成的表数量及内容是否是您期望的!  工具存在bug是不意外的...')


exit_input=input('\n\n\n回车键退出!\n\n\n')

