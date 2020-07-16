#nameList = ["zhangsan", '李四', "王五", 12]

# print(type(nameList[3]))
#
# print(len(nameList))
#
# nameList.pop()

# print(nameList.index(12))
tableType='textfile'     #表默认格式
partition_flag='n' #是否是分区表
filePath=input('请输入文件地址 (尽量将文件路径复制过来避免输错):')
print('文件路径:'+filePath+'\n')

tableTypeInput=input('请输入表存储类型(textfile或orc - 回车默认textfile):')
if tableTypeInput!='':tableType=tableTypeInput
print('表存储类型:'+tableType+'\n')

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


print('\n\n文件路径:'+filePath)
print('表存储类型:'+tableType)
print('是否是分区表:'+partition_flag)
if partition_flag.lower() =='y':
    print('分区字段:'+partition_col)
    print('分区字段类型:'+partition_col_type)







