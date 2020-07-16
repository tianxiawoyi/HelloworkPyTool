

def stg_etl_text(tableName,col_text):
    text1='''
    #!/bin/sh
    #作者:weidongbin
    #创建时间:2020/06/01
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
    text2=f'''
    --target-dir /bd-os/zh_hfgf/hive/stg_s0001/stg_s0001_{sap_prod_dbpath}_{tableName} \\
    --query "select {col_text} from {sap_prod_dbpath}.{tableName} where 1=1 and \$CONDITIONS" \\
    '''

    text3='''
    --fields-terminated-by '\\001' \\
    --m 1 \\
    --lines-terminated-by '\\n' \\
    --null-string '\\\\N'  \\
    --null-non-string '\\\\N' \\
    --hive-drop-import-delims
    '''

    print(text1+text2+text3)
    return text1+text2+text3


#stg_etl_text('bkpf','Cast(MANDT As VARCHAR) AS MANDT , Cast(BUKRS As VARCHAR) AS BUKRS')


# import time
# print(time.strftime("%Y/%m/%d", time.localtime()))  #2020/05/31

# 测试将驼峰命名转下划线命名
# def tf2xhx(strText):
#     # strText= 'ssGdsJsDvcGz'
#     print('前:'+strText)
#     s = set()
#     for i, ch in enumerate(strText):
#         if ch.isupper():s.add(ch)
#     for i, ch in enumerate(s):
#         strText = strText.replace(ch, f'_{ch.lower()}')
#     print('后:'+strText)
#     return strText
#     #coln= addXHX(tbr[6].value)


# 测试正则,用正则sub将驼峰命名转下划线命名
#import  re
#def tf2xhx2(strText):
#    ret = re.sub(r'[A-Z]',lambda x:f'_{x.group().lower()}',strText)
#    re.match()
#    print(ret)
#    return ret
#tf2xhx2('ss Gds Js Dvc Gz')
#tf2xhx2('ss gds js dvc gz')


# import win32ui
# dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
# dlg.SetOFNInitialDir('E:/Python')  # 设置打开文件对话框中的初始显示目录
# dlg.DoModal()
#
# filename = dlg.GetPathName()  # 获取选择的文件名称
# self.lineEdit_InputId_AI.setText(filename)  #将获取的文件名称写入名为“lineEdit_InputId_AI”可编辑文本框中

import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

root = tk.Tk().withdraw()
fileName = tkfiledialog.askopenfilename(title='请选择vcf或csv文件',filetypes=[("vcf文件", "*.*"), ('csv文件', '*.csv')])
#多文件
fileNames = tkfiledialog.askopenfilenames(title='请选择vcf或csv文件',filetypes=[("vcf文件", "*.*"), ('csv文件', '*.csv')])
print(fileName)
print(fileNames)
tkmessagebox.showinfo(message="正常消息")
