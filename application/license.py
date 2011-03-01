#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import hashlib
import cPickle as pickle
import time

class License:
    def __init__(self, uname="SLMG", uid=None, count=0, expire=None):
        self.uname = uname 
        self.uid = uid or str(uuid.uuid3(uuid.NAMESPACE_DNS,"test")).replace("-","").upper()[:12]
        self.hash = hashlib.md5(self.uid).hexdigest()
        #only to have some copies before registration
        self.count = 1000
        self.expire = expire or time.strptime("1103251843", "%y%m%d%H%M")

    def isvalid(self):
        return time.localtime() < self.expire
    
    def genkey(self, n):
        digits = "0123456789abcdf"
        num = hex(n)[2:]
        while len(num)%2:
            num = "0%s" % num
            
        l = hex(len(num))[2:]
        while len(l)%2:
            l = "0%s" % l
        tail = "".join([self.hash[digits.find(x)] for x in "%s%s" % (l, num)])
        return "%s%s%s" % (l, num, tail)
        
    def inc(self, key):
        digits = "0123456789abcdf"        
        l = int(key[:2])
        num = int(key[2:2+l],16)
        tail = "".join([self.hash[digits.find(x)] for x in "%s%s" % (key[:2], key[2:2+l])])
        if key.endswith(tail):
            self.count = self.count + num
            return True
        return False

    def dec(self, n):
        self.count = self.count - n
        
    def save(self, path):
        f = open(path, "w")
        p = pickle.Pickler(f, protocol=pickle.HIGHEST_PROTOCOL)
        p.dump(self)
        f.close()            

    @staticmethod
    def load(path):
        try:
            f = open(path, "r")
            lic = pickle.load(f)
            f.close()
        except:
            return License()
        return lic

    def __str__(self):
        return "Licensed to '%s'. Expires on %s. %d pages left." % (self.uname, time.strftime("%a, %d %b %Y ", self.expire), self.count)

    def __repr__(self):
        return "<License('%s',%d,'%s')>" % (self.uid, self.count, time.strftime("%a, %d %b %Y %H:%M:%S +0000", self.expire))

