# coding=utf-8
# linxiao			2020-12-21      create
import xdrlib, sys
import xlrd
import xlwt


# 打开excel文件
def open_excel(file='test.xlsx'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))


# 根据名称获取Excel表格中的数据
def getDataBySheet(file='test.xlsx', colnameindex=0, by_name='Sheet1'):
    data = open_excel(file)
    table = data.sheet_by_name(by_name)
    nrows = table.nrows
    colnames = table.row_values(colnameindex)
    list = []
    for rownum in range(0, nrows):
        row = table.row_values(rownum)
        if row:
            app = []
            for i in range(len(colnames)):
                app.append(row[i])
            list.append(app)
    return list


# 根据索引获取Excel表格中的数据
def getDataByIndex(file='test.xlsx', colnameindex=0, by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows
    ncols = table.ncols
    colnames = table.row_values(colnameindex)
    list = []
    for rownum in range(0, nrows):

        row = table.row_values(rownum)
        if row:  # 如果行存在
            app = []
            for i in range(len(colnames)):
                app.append(row[i])
            if app[0] == app[1]:
                list.append(app)
    return list


# 将list中的内容写入一个新的file文件
def createFromList(list,file='new.xls'):
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('hello')
    i = 0
    for app in list:
        j = 0
        for x in app:
            sheet1.write(i, j, x)
            j = j + 1
        i = i + 1
    try:
        book.save(file)
    except Exception as e:
        print('请关闭已经打开的文档')
# 将list<dict>中的内容写入一个新的file文件

def createFromDict(dicts,file='new.xls'):
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('hello')
    i = 0
    j = 0
    for x in list(dicts[0].keys()):
        sheet1.write(i, j, x)
        j+=1
    i+=1
    for app in dicts:
        j = 0
        for x in app:
            sheet1.write(i, j, app[x])
            j = j + 1
        i = i + 1
    try:
        book.save(file)
    except Exception as e:
        print('请关闭已经打开的文档')

# -----------4 test------------

def main_test():
    tables = getDataByIndex('test.xlsx',1,0)
    assert tables
    createFromList(tables)


if __name__ == "__main__":
    main_test()