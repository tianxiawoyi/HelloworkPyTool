import xlrd
import xlwt
import os
import time
import configparser
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

configPath=r'E:\Develop\ideaWorkPath\Python\project\Hellowork\src\config\insertValuesConfig.ini'
configPath_input=input(f'请输入配置文件所在路径:\n(回车默认:{configPath})\n')
if configPath_input!='':configPath=configPath_input.strip()
print('配置文件所在路径:'+configPath+'\n')

config = configparser.ConfigParser()   #  实例化configParser对象
config.read(configPath, encoding='utf_8')  # -read读取ini文件
paramGroup='param'
#关键词字段,生成时在后面添加一个下划线
filePath=config.get(paramGroup, 'filePath')
sheet_index=config.getint(paramGroup, 'sheet_index')-1
start_row_index=config.getint(paramGroup, 'start_row_index')-1
end_row_index=config.getint(paramGroup, 'end_row_index')
start_col_index=config.getint(paramGroup, 'start_col_index')-1
end_col_index=config.getint(paramGroup, 'end_col_index')

data = xlrd.open_workbook(filePath)  #读取数据字典Excel文件
table = data.sheet_by_index(sheet_index) #通过索引顺序获取
nrows = table.nrows  #获取该sheet中的有效行数

createText=''
for i in range(start_row_index,end_row_index,1):
    table_row=table.row(i)
    # print('-------------------')
    row_text=f'{i+1}\t,('
    for i in range(start_col_index,end_col_index,1):
       text=table_row[i].value
       # print(text)
       if i==end_col_index-1:row_text+= f"'{text}' \t)\n"
       else:row_text+= f"'{text}',\t"
    # print(row_text)
    createText+= row_text
print(createText)

filePathDirPath=os.path.abspath(os.path.dirname(filePath))  #获取文件的上级目录
generatePath=os.path.join(filePathDirPath,f'generatetext.txt')
with open(generatePath, mode='w',encoding='utf-8',newline='\n') as f:
    f.write(createText)
print(f'文件生成位置:{generatePath} \n')
exit_input=input('\n回车键退出!\n\n')