import configparser

#  实例化configParser对象
config = configparser.ConfigParser()
# -read读取ini文件
config.read(r'E:\Develop\ideaWorkPath\Python\project\Hellowork\src\config\config.ini', encoding='utf_8')
# -sections得到所有的section，并以列表的形式返回
print('sections:' , ' ' , config.sections())   # ['config', 'cmd', 'log']

# -options(section)得到该section的所有option
print('options:' ,' ' , config.options('config'))   #['platformname', 'apppackage', 'appactivity']

# -items（section）得到该section的所有键值对
print('items:' ,' ' ,config.items('cmd'))   #[('viewphone', 'adb devices'), ('startserver', 'adb start-server'), ('stopserver', 'adb kill-server'), ('install', 'adb install aaa.apk'), ('id', '1'), ('weight', '12.1'), ('ischoice', 'True')]


# -get(section,option)得到section中option的值，返回为string类型
print('get:' ,' ' , config.get('cmd', 'startserver'))   #adb start-server

# -getint(section,option)得到section中的option的值，返回为int类型
print('getint:' ,' ' ,config.getint('cmd', 'id'))
print('getfloat:' ,' ' , config.getfloat('cmd', 'weight'))
print('getboolean:' ,'  ', config.getboolean('cmd', 'isChoice'))
"""
首先得到配置文件的所有分组，然后根据分组逐一展示所有
"""
for sections in config.sections():
    for items in config.items(sections):
        print(items)



aaa=config.get('param', 'sys_code')
aac=config.get('param', 'odsTableColTran_switch').split(',')
aab=1
print("sys_code:"+aaa+"    type:"+ str(type(aaa)))
print("sys_code:"+str(aab)+"    type:"+ str(type(aab)))
print("sys_code:"+str(aac)+"    type:"+ str(type(aac)))


keywords=config.get('param', 'keywords').split(',')
keyword=config['param']['keywords']
print(keyword)
print(keywords)


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


def sourceColType2HiveColType2(sourceColType,config):
    sourceColType = (sourceColType.lower().split('('))[0]
    for items in config.items('col_type_tran_rule'):
        if sourceColType in items[1].lower().split(','):
            return items[0]
    return 'string'

print(sourceColType2HiveColType2("smallint"))
#
# import configparser
#
# #  实例化configParser对象
# config = configparser.ConfigParser()
# # -read读取ini文件
# config.read('C:\\Users\\songlihui\\PycharmProjects\\AutoTest_02\\config\\config.ini', encoding='GB18030')
# list = []
# list = config.sections()# 获取到配置文件中所有分组名称
# if 'type' not in list:# 如果分组type不存在则插入type分组
#     config.add_section('type')
#     config.set('type', 'stuno', '10211201')# 给type分组设置值
#
# config.remove_option('type', 'stuno')# 删除type分组的stuno
# config.remove_section('tpye')# 删除配置文件中type分组
# o = open('C:\\Users\\songlihui\\PycharmProjects\\AutoTest_02\\config\\config.ini', 'w')
# config.write(o)
# o.close()#不要忘记关闭
#