#!/usr/bin/env python
# coding=utf-8
import random
import xlwt


print(random.randint(1, 10))
# print("hello python")
# print("你好,python")

print("sssss\n" * 5)

# i = 0
# while i < 10:
#     print("i的值 %d" % i)
#     print("while循环语法示例")
#     i += 1

# s="你好,jkj对对对"
# b=s[0:]+"     "
# print(b*10)

# sss = ["aa" ,12,"sss"]
# aaa = [23,"ccc","56"]
# sa=sss+aaa
# print(sa)
# print(sss*3)

# 字典
# gg="ff"
# a=("dd",34,"sdsd",45)
# b={"ss":23,"bb":"ddd",gg:a,1:11111}
# print(a)
# print(a[2])
# print(b.values())
# print(b.keys())
# print(b[gg])
# print(b["ss"])
# print(b[1])

'''
三个单引号或双引号可以是多行的字符串,
或者注释
'''

sss = '''  三个单引号可以是多行的字符串,
或者注释'''

print(sss)

# python中有哪些类型的布尔值是False？
# 1.None
# 2. False
# 3.所有的值为零的数
# 4.""
# 5.[]
# 6.()
# 7.{}


a = "30"
b = 30

# print(a and b)
# print(a or b)
# print(not a)

if a is b:
    print("a is b")
    print("-" * 5)
elif a == b:
    print("a == b")
    print("-" * 5)
else:
    print("a!=b")
    print("-" * 5)

x = True
y = False
z = False
xx = 234

print("按时打发的撒发 %d%%" % xx)

if not x or y:
    print(1)
elif not x or not y and z:
    print("按时打发的撒发%d" % x)
elif not x or y or not y and x:
    print(3)
else:
    print(4)
