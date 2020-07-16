import os
#根据ods的hql文件生成ods的etl 的sh文件  是select  * 模式的

path=r'C:\Users\TXWY\Desktop\数据湖\脚本\stg_export\ods'
fileSum=0
for root,dirs,files in os.walk(path):
    for file in files:
        if not file.endswith('.hql'):continue
        odsTableName = file.split('.')[0]
        print("file:"+file)
        print("odsTableName:"+odsTableName)

        # odsTable='ODS_S0001.ODS_S0001_SAPS4P_ZSAC_D_MD0001'
        # stgTable='STG.STG_S0001_SAPS4P_ZSAC_D_MD0001'

        odsTable=f'{odsTableName[:9]}.{odsTableName}'
        stgTable=odsTable.replace('ODS_','STG_').replace('ODS_','STG_',)
        print("odsTable:"+odsTable)
        print("stgTable:"+stgTable)

        text=f'''#!/bin/sh\n#ods(stg层数据格式转化及保留字段分区添加)\n#作者:weidongbin\n#创建时间:2020/05/28\n\n#引入时间脚本\nsource ./get_date.sh\necho $y_date
        
        
        hive -e "
        
        insert overwrite table {odsTable} PARTITION (PERIOD_WID='$y_date')
        select 
        *
        ,FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') as W_INSERT_DT
        from {stgTable} WHERE MANDT='800';
        
        "
        '''

        print(text)
        odsETL_Path=os.path.join(root, 'odsETL')

        odsETL_filePath=os.path.join(odsETL_Path, (odsTableName + '.sh'))
        print(odsETL_filePath)
        if not os.path.exists(odsETL_Path):os.makedirs(odsETL_Path)
        print("============================================")
        with open(odsETL_filePath, mode='w', encoding='utf-8') as f:
            f.write(text)

        fileSum+=1


print(fileSum)
