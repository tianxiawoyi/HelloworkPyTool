import os

#filePath2=r'C:\Users\TXWY\Desktop\数据湖\脚本\scriptExport_1590498892912\STG_S0001_SAPS4P_ACDOCA.hql'
path=r'C:\Users\TXWY\Desktop\数据湖\脚本\stg_export'
#read()是最简单的一种方法，一次性读取文件的所有内容放在一个大字符串中，即存在内存中
# file_object = open('test.txt') #不要把open放在try中，以防止打开失败，那么就不用关闭了
# file_object = open(filePath,encoding='utf-8') #不要把open放在try中，以防止打开失败，那么就不用关闭了
# try:
#     file_context = file_object.read() #file_context是一个string，读取完后，就失去了对test.txt的文件引用
#     #  file_context = open(file).read().splitlines()
#     # file_context是一个list，每行文本内容是list中的一个元素
# finally:
#     file_object.close()

for root,dirs,files in os.walk(path):
    for file in files:
        if file.endswith('.xml'):continue
        filePath=os.path.join(root,file)
        print(filePath)

        file_context=''
        with open(filePath,encoding='utf-8') as file_object:
            file_context = file_object.read()

        file_context = file_context.replace('STG_','ODS_').replace('stg_','ODS_')
        file_context = file_context.replace('textfile','orc').replace('TEXTFILE','orc')

        ROW_FORMAT_index=file_context.index('ROW FORMAT')
        table_COMMENT_index=None
        if ')COMMENT' in file_context:table_COMMENT_index=file_context.index(')COMMENT')
        else:table_COMMENT_index=file_context.index(')\nCOMMENT')
        file_context=file_context[:table_COMMENT_index]+",W_INSERT_DT						STRING				COMMENT '数据插入时间'\n\n" +\
            file_context[table_COMMENT_index:ROW_FORMAT_index]+'PARTITIONED BY (PERIOD_WID STRING)\n\n'+file_context[ROW_FORMAT_index:]
        # file_context=file_context[:ROW_FORMAT_index]+'PARTITIONED BY (PERIOD_WID STRING)\n'+file_context[ROW_FORMAT_index:]
        print(file_context)
        print(ROW_FORMAT_index)

        ods_dirPath=os.path.join(root,'ods')
        ods_filePath=os.path.join(ods_dirPath,file.replace('STG_','ODS_').replace('stg_','ODS_'))
        print(ods_filePath)
        if not os.path.exists(ods_dirPath):os.makedirs(ods_dirPath)
        print("============================================")
        with open(ods_filePath, mode='w',encoding='utf-8') as f:
            f.write(file_context)


