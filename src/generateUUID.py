#!/bin/python
# -*- coding:utf-8 -*-
import sys
import datetime
import uuid

for line in sys.stdin:
    line = line.strip()
    # movieid, rating, unixtime,userid = line.split('\t')
    # weekday = datetime.datetime.fromtimestamp(float(unixtime)).isoweekday()
    # print('\t'.join([movieid, rating, str(weekday),userid]))
    suid = ''.join(str(uuid.uuid4()).split('-'))
    print(suid)


#print(uuid.uuid1())  #bf1dfacf-67d8-11e8-9a23-408d5c985711
#print(uuid.uuid3(uuid.NAMESPACE_DNS, 'yuanlin'))  #ddb366f5-d4bc-3a20-ac68-e13c0560058f
#print(uuid.uuid4())   #144d622b-e83a-40ea-8ca1-66af8a86261c
#print(uuid.uuid5(uuid.NAMESPACE_DNS, 'yuanlin'))   #4a47c18d-037a-5df6-9e12-20b643c334d3
#
#uid = str(uuid.uuid4())
#suid = ''.join(uid.split('-'))
#print(suid)


