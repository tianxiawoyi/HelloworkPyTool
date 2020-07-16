##华实OA 将html中(D:\ecology80表单) 表格数据写入Excel中  #todo 美化:每个表 相隔用不同的颜色
from bs4 import BeautifulSoup
import xlwt
import os

xlsSavePath = "xls/OA.xls"

def listFiles():
    filecount=0
    file_list = [] #用来存放所有的文件路径
    for root,dirs,files in os.walk(r"D:\ecology80表单"):
        for file in files:
            # 下面的要手动处理
            if file=='vssver2.scc' or file=='index.html' or \
                    file=='workflow_hrmoperator.htm' or \
                    file=='matrixFieldInfo(人力资源组矩阵字段信息表).html' or \
                    file=='matrixinfo(人力资源组矩阵信息表).html':
                continue
            #获取文件所属目录
            print(root)
            print(file)
            #获取文件路径
            filePath=os.path.join(root,file)
            print(filePath)
            file_list.append(filePath)
            filecount=filecount+1
            print(str(filecount)+"----------------------------")
    print("file_list_len(html文件数) :" + str(len(file_list)))
    return file_list


if __name__ == "__main__":
    row = 0       # 记录行数
    tableSum=0   # 记录表个数
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet("sheet1")


    file_list = listFiles()
    # 文件遍历
    for childPath in file_list:
        print(childPath)
        tableSum = tableSum+1
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