from time import ctime, sleep
#=======================================
#装饰不定长参数函数和有返回值函数
from typing import Dict


def timefun(func):
    def wrapped_func(*args, **kwargs):  #装饰定长参数函数
        print("%s called at %s"%(func.__name__, ctime()))
        return func(*args, **kwargs)     #加return 通用有返回值函数和无返回值函数
    return wrapped_func

@timefun
def foo(a, b, c):
    print(a+b+c)

@timefun
def foo1(a, b):
    print(a+b)

@timefun
def foo2():
    print('无参')

@timefun
def getInfo():
    return '----hahah---'

foo(3,5,7)
# sleep(2)
foo1(2,4)
# sleep(2)
foo2()

print(getInfo())

#======================================================
# 装饰器带参数,在原有装饰器的基础上，设置外部变量
def timefun_arg(pre="hello"):
    def timefun(func):
        def wrapped_func():
            print("%s called at %s %s" % (func.__name__, ctime(), pre))
            return func()
        return wrapped_func
    return timefun

# 下面的装饰过程
# 1. 调用timefun_arg("itcast")
# 2. 将步骤1得到的返回值，即time_fun返回， 然后time_fun(foo)
# 3. 将time_fun(foo)的结果返回，即wrapped_func
# 4. 让foo = wrapped_fun，即foo现在指向wrapped_func
# 可以理解为 foo()==timefun_arg("itcast")(foo)()
@timefun_arg(pre="itcast")
def foo():
    print("I am foo")

@timefun_arg("python")
def too():
    print("I am too")

foo()
foo()

too()
too()


class Person:
    def __init__(self,name,age):
        self.name = name
        if type(age) is int:
            self.__age = age
        else:
            print( '你输入的年龄的类型有误,请输入数字')
    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self,a):
        '''判断,你修改的年龄必须是数字'''
        if type(a) is int:
            self.__age = a
        else:
            print('你输入的年龄的类型有误,请输入数字')

    @age.deleter
    def age(self):
        del self.__age


p1 = Person('帅哥',20)
print(p1.age)
del p1.age


#迭代器Iterator 和 可迭代对象Iterable
from collections.abc import Iterable, Iterator
#DeprecationWarning: Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated, and in 3.8 it will stop working
#弃用警告,从collections导入ABCs已被弃用,在3.8中将停止工作. 可使用collections.abc代替他
aa=(1,'2',2.01,True)
bb={'a':'1','b':'2','c':'2.01','d':'True'}
print(isinstance(bb,Dict))
print(isinstance(bb,Iterable))
print(isinstance(bb,Iterator))
print(type(bb))



def join2str(iter:Iterable,split='|'):
    """
    将数组,tuple,(字典的value)等里面的元素用分隔符拼接成字符串
    :param iter: 数组,tuple,list 等可迭代对象
    :param split: 分割符
    :return: 返回可迭代对象里面的元素拼接成的字符串
    """
    text = ''
    if isinstance(iter,dict):iter=iter.values()
    for i,v in enumerate(iter):
        vv = str(v).strip() #strip()去掉两端空格
        if vv=='None':vv=''
        text += ( vv + split)
    if text.endswith(split): text=text[:len(text)-1]+'\n'
    print(text)
    return text

if __name__ == '__main__':
    aax={"a":"sda","b":"sdb","c":"sdc","d":"sdd"}
    aac=[1,3,6,9]
    join2str(aax)
    join2str(aac)