import os
#根据ods的hql文件生成ods的etl 的sh文件  是select  具体字段 模式的


# todo  baohan `的字段加上\   如 ,\`YEAR\`
def readCols(hql_file_path):
    """ 从hql文件中毒出字段:根据字段都包含COMMENT子串,再排除掉表的COMMENT """
    cols_text=''
    cols_line=[]
    with open(filePath,encoding='utf-8') as f:
        for line in f.readlines():
            # print(line)
            if 'COMMENT' in line or 'comment' in line:
                #cols_line.append(line.strip())
                #1.split()函数默认可以按空格分割，并且把结果中的空字符串删除掉，aa   bbbbb         ccc  -->['aa','bbbbb','ccc']
                #2.可以用filter函数对split（“ ”）进行过滤str = "aa   bbbbb         ccc";str_list = filter(None,str.split(" "))
                line_split = line.strip().split()
                if len(line_split)>=3:
                    if 'W_INSERT_DT' in line_split[0] or  'w_insert_dt' in line_split[0]:
                        W_INSERT_DT=",FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') as W_INSERT_DT"
                        cols_line.append(""+W_INSERT_DT)
                    elif ')COMMENT' in line_split[0] or ')comment' in line_split[0]   or ')' in line_split[0]:
                        pass
                    elif '`' in line_split[0]:
                        col_tmp=line_split[0].replace('`','\`')
                        cols_line.append(col_tmp)
                    else:
                        cols_line.append(line_split[0])
    for col in cols_line:
        cols_text += (col+'\n')
    # print(cols_text)
    return cols_text


# path=r'C:\Users\TXWY\Desktop\数据湖\脚本\stg_export\ods'
path=r'C:\Users\TXWY\Desktop\数据湖\脚本\ods_s0007导出'
# path=r'C:\Users\TXWY\Desktop\数据湖\脚本\odsS0017_export'
fileSum=0
for root,dirs,files in os.walk(path):
    for file in files:
        if not file.endswith('.hql'):continue

        filePath=os.path.join(root,file)
        print(filePath)
        cols_text = readCols(filePath)

        odsTableName = file.split('.')[0]
        print("file:"+file)
        print("odsTableName:"+odsTableName)

        # odsTable='ODS_S0001.ODS_S0001_SAPS4P_ZSAC_D_MD0001'
        # stgTable='STG.STG_S0001_SAPS4P_ZSAC_D_MD0001'

        odsTable=f'{odsTableName[:9]}.{odsTableName}'
        stgTable=odsTable.replace('ODS_','STG_').replace('ODS_','STG_',)
        print("odsTable:"+odsTable)
        print("stgTable:"+stgTable)

        y_date='${y_date}'
        hqlText=f"hive -e \"\ninsert overwrite table {odsTable} PARTITION (PERIOD_WID='{y_date}')\nselect\n{cols_text}\nfrom {stgTable} ;\n\n\""  # WHERE MANDT='800'
        text=f"#!/bin/sh\n#ods(stg层数据格式转化及保留字段分区添加)\n#作者:weidongbin\n#创建时间:2020/06/15\n\n#引入时间脚本\nsource ./get_date.sh\necho $y_date\n\n\n{hqlText}"

        print(text)
        odsETL_Path=os.path.join(root, 'odsETL20200615')

        odsETL_filePath=os.path.join(odsETL_Path, (odsTableName + '.sh'))
        print(odsETL_filePath)
        if not os.path.exists(odsETL_Path):os.makedirs(odsETL_Path)
        print("============================================")
        with open(odsETL_filePath, mode='w', encoding='utf-8') as f:
            f.write(text)

        fileSum+=1


print(fileSum)
