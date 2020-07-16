#!/usr/bin/env python
# coding=utf-8


def sum_sum(numa, numb):
    """
    求和
    :param numa:
    :param numb:
    :return:
    """
    # numa = 10
    # numb = 20

    print("%d + %d = %d" % (numa, numb, numa + numb))
    return numa + numb


ss = sum_sum(10, 13)
print("ss的值:%d" % ss ,sep="aa",end="bb")
