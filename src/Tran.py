## 将html中(D:\ecology80表单) 表格数据写入Excel中  #todo 美化:每个表 相隔用不同的颜色
from bs4 import BeautifulSoup
import xlwt
import os

html = """
<html><head>
<title>hrmmessagergroup(聊天人员分组表)</title>
<meta http-equiv="Content-Type" content="text/html; charset=gbk">
<style>
body, td {
font-family: 微软雅黑;
font-size: 12px;
line-height: 150%;
}
table {
width: 100%;
background-color: #ccc;
margin: 5px 0;
word-break: break-all;
}
td {
	background-color: #fff;
	padding: 3px;
padding-left: 10px;
}
thead td {
	text-align: left;
font-weight: bold;
background-color: #eee;
}
a:link, a:visited, a:active {
color: #015FB6;
text-decoration: none;
}
a:hover {
color: #E33E06;
}
.tablename {
margin-top: 30px;
}
.outdiv {
width: 1000px;
margin: 40px auto;
text-align: left;
}

</style>
</head>
<body>
<center>
<div class="outdiv">
<div class="tablename">
<b>表名：hrmmessagergroup</b>
</div>
<div>中文名称：聊天人员分组表</div>
<div>表类型： </div>
<a href="index.html" style="float: right;">返回目录</a><div>说明：</div>
<table cellspacing="1" cellpadding="0">
 <colgroup>
  <col width="50px">
  <col width="190px">
  <col width="190px">
  <col width="80px">
  <col width="80px">
  <col width="70px">
  <col width="40px">
  <col width="60px">
  <col width="40px">
  <col width="200px">
 </colgroup>
 <thead>
  <tr>
   <td>序号</td>
   <td>中文名称</td>
   <td>英文名称</td>
   <td>数据类型</td>
   <td>长度</td>
   <td>允许空值</td>
   <td>主键</td>
   <td>默认值</td>
   <td>自增</td>
   <td>说明</td>
  </tr>
 </thead> 
 <tbody>
  <tr>
   <td style="text-align: center;">1</td>
   <td>组名</td>
   <td>groupname</td>
   <td align="center">int</td>
   <td align="center"></td>
   <td align="center"> N </td>
   <td align="center"></td>
   <td align="center"></td>
   <td></td>
   <td>　</td>
  </tr>
  <tr>
   <td style="text-align: center;">2</td>
   <td> 组描述</td>
   <td>groupdesc</td>
   <td align="center">varchar</td>
   <td align="center">1000</td>
   <td align="center"> N </td>
   <td align="center"></td>
   <td align="center"></td>
   <td></td>
   <td>　</td>
  </tr> 
 </tbody>
</table>
</div>
</center>



</body></html>"""

row = 0       # 记录行数
tableSum=0   # 记录表个数
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet("sheet1")


#dirPath = 'D:\ecology80表单\E-message'
# dirPath = 'D:\ecology80表单\表单建模'
# dirPath = 'D:\ecology80表单\公文'
# dirPath = 'D:\ecology80表单\会议'
# dirPath = 'D:\ecology80表单\集成中心'
# dirPath = 'D:\ecology80表单\客户'
# dirPath = 'D:\ecology80表单\流程引擎'  # workflow_hrmoperator.htm 这个文件没弄  Y
# dirPath = 'D:\ecology80表单\门户'
# dirPath = 'D:\ecology80表单\内容引擎'
# dirPath = 'D:\ecology80表单\人力资源'   # matrixFieldInfo(人力资源组矩阵字段信息表).html , matrixinfo(人力资源组矩阵信息表).html 这文件没弄
# dirPath = 'D:\ecology80表单\日程'
# dirPath = 'D:\ecology80表单\微博'
# dirPath = 'D:\ecology80表单\微搜'
# dirPath = 'D:\ecology80表单\相册'
# dirPath = 'D:\ecology80表单\项目'
# dirPath = 'D:\ecology80表单\协作'
# dirPath = 'D:\ecology80表单\移动引擎'
# dirPath = 'D:\ecology80表单\邮件'
# dirPath = 'D:\ecology80表单\预算'
# dirPath = 'D:\ecology80表单\证照'
# dirPath = 'D:\ecology80表单\资产'
# dirPath = 'D:\ecology80表单\组织权限'
# dirPath = 'D:\ecology80表单\集成中心\HR同步'
# dirPath = 'D:\ecology80表单\集成中心\IM集成设置'
# dirPath = 'D:\ecology80表单\集成中心\LDAP集成'
# dirPath = 'D:\ecology80表单\集成中心\WebService注册'
# dirPath = 'D:\ecology80表单\集成中心\集成登录'
# dirPath = 'D:\ecology80表单\集成中心\流程触发集成'
# dirPath = 'D:\ecology80表单\集成中心\流程流转集成'
# dirPath = 'D:\ecology80表单\集成中心\数据展现集成'
# dirPath = 'D:\ecology80表单\集成中心\外部数据元素'
dirPath = 'D:\ecology80表单\集成中心 - 副本'

# xlsSavePath = "xls/组织权限.xls"
xlsSavePath = "xls/集成中心/集成中心all.xls"

# 遍历指定目录，显示目录下的所有文件名
#def eachFile(dirpath):
#    pathDirs = os.listdir(dirpath)
#    pathDirs2 = [i for i in pathDirs if i!='vssver2.scc' and i!='index.html' ]
#
#    for childName in pathDirs:
#        if childName=='vssver2.scc' or childName=='index.html':
#            continue
#        childPath = os.path.join('%s%s' % (dirpath, childName))
#        print(childPath)  # .decode('gbk')是解决中文显示乱码问题
#    print(pathDirs)
#    print(pathDirs2)
#    return pathDirs2


# 遍历指定目录，显示目录下的所有文件名
def eachFile(dirpath):
    pathDirstem = os.listdir(dirpath)
    pathDirs = [i for i in pathDirstem if i!='vssver2.scc' and i!='index.html' ]
    print(pathDirs)
    return pathDirs

pathDirs = eachFile(dirPath)
# 文件遍历
for childName in pathDirs:
    # 下面的要手动处理
    if childName=='vssver2.scc' or childName=='index.html' or \
            childName=='workflow_hrmoperator.htm' or \
            childName=='matrixFieldInfo(人力资源组矩阵字段信息表).html' or \
            childName=='matrixinfo(人力资源组矩阵信息表).html':
        continue
    childPath = os.path.join('%s\%s' % (dirPath, childName))  #文件路径
    print(childPath)
    tableSum = tableSum+1   # 是文件的话 记录表个数+1
    # f = open(r"F:\xxx.html")
    #f = open("C:\\Users\\TXWY\\Desktop\\E-message\\hrmmessagergroup(聊天人员分组表).html", 'r', encoding='gbk')
    f = open(childPath, 'r', encoding='gbk')
    ff = f.read()
    soup = BeautifulSoup(ff, 'lxml')  # BeautifulSoup使用lxml解析器
    # print(soup.find('tablename'))
    # print(soup.find(class_='tablename'))
    tableName = soup.select('.tablename')[0].get_text().replace('表名：', '').replace('\n', '')  #获取表名
    tableName_cn = soup.select('.tablename')[0].find_next_sibling().get_text().replace('中文名称：', '')  # 获取中文表名
    print(tableName)
    print(tableName_cn)

    trs = soup.find('tbody').find_all('tr')   #获取表格行数据
    for i, tr in enumerate(trs):
        row = row+1
        tds = tr.find_all('td')
        print('-------------')
        worksheet.write(row, 3, label=tableName.strip())
        worksheet.write(row, 4, label=tableName_cn.strip())
        for j, td in enumerate(tds):
            #print(td.get_text())
            worksheet.write(row, j + 5, label=td.get_text().strip())  # strip()去掉两边空格 ,第6列开始

print(tableSum)
workbook.save(xlsSavePath)


#trs = soup.find('tbody').find_all('tr')
#for i, tr in enumerate(trs):
#    row = row+1
#    tds = tr.find_all('td')
#    print('-------------')
#    worksheet.write(i + 1, 3, label=tableName.strip())
#    worksheet.write(i + 1, 4, label=tableName_cn.strip())
#    for j, td in enumerate(tds):
#        #print(td.get_text())
#        worksheet.write(i + 1, j + 5, label=td.get_text().strip())  # strip()去掉两边空格 ,第6列开始

# workbook.save(xlsSavePath)


# bb = soup.find_all(attrs={'class', 'testcase'})
# for i, b in enumerate(bb):
#     print b['id']
#     worksheet.write(i+1, 0, label = b['id'])
#     sss = b.td.get_text().split()
#     if len(sss) >= 2:
#         print sss[0], sss[1]
#     else:
#         print sss[0], u"无描述"
#     worksheet.write(i + 1, 1, label=sss[0])
#     if len(sss) >= 2:
#         worksheet.write(i + 1, 2, label=sss[1])
#     else:
#         worksheet.write(i + 1, 2, label=u'无描述')
#
# workbook.save(xlsSavePath)
