#! /usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import logging
import datetime
import copy
import codecs
import os
import re
import sqlite3
import time
import socket
import requests
from urllib import urlencode

#import socks
#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
#socket.socket = socks.socksocket

BASE_DIR= os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "databases", "test_01.db")

logging.basicConfig(
    level=logging.INFO,
    # filename="/home/louch/local/log/spider.log",
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)

def to_unix(date):
    return int(time.mktime(date.timetuple()))

def to_datetime(ts):
    return datetime.datetime.fromtimestamp(int(ts))

class DataItem(object):
    def __init__(self, id = None, date = None , value = None):
        self.id = id
        self.date = date
        self.value = value

    def to_tuple(self):
        return (self.id, to_unix(self.date), self.value)

    def __str__(self):
        return "[%s] [%s] [%s]" % (self.id, self.date, self.value)

    def __repr__(self):
        return self.__str__()

class DataFetcher(object):
    URL = "http://xxfb.hydroinfo.gov.cn/svg/svgwait.jsp" 
    HEADERS = {
        "Accept": "*/*",
        "REFERER": "http://xxfb.hydroinfo.gov.cn/svg/svghtml.html",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E)",
        "Host": "xxfb.hydroinfo.gov.cn",
    }
    PARAMS = {
        "gcxClass": "1",
        "gcxKind": "2",
        "DateL": "",
        "DateM": "",
        "gcxData": "7",
        "site": "",
    }
    REG = {
        "safety_level": {
            "exp": re.compile(ur"保证水位(?P<safety_level>[\d\.]+)"),
            "is_points": False
        },
        "warning_level": {
            "exp": re.compile(ur"警戒水位(?P<warning_level>[\d\.]+)"),
            "is_points": False 
        },
        "level_points": {
            "exp": re.compile(ur"水位.*points=\"(?P<level_points>[\d\.,\s]+)"),
            "is_points": True
        },
        "flow_points": {
            "exp":  re.compile(ur"流量.*points=\"(?P<flow_points>[\d\.,\s]+)"),
            "is_points": True
        }
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    

    def build_params(self, site_id, start_date):
        params = copy.deepcopy(self.PARAMS)
        params["DateL"] = str(start_date)
        params["DateM"] = datetime.date.today()
        params["site"]  = str(site_id)
        return params


    def parse_points(self, raw_str, start_date):
        ret = []
        start_date = datetime.datetime(*(start_date.timetuple()[:6])) # convert to datetime

        for p in raw_str.split():
            try:
                hours_delta, value = p.split(",")

                time = start_date + datetime.timedelta(hours=float(hours_delta))
                time = time.replace(second=0, microsecond=0) # strip off seconds

                value = float(value)

                ret.append(DataItem(date=time, value=value))
            except Exception as e:
                logging.error("Parsing error!")
                logging.exception(e)
                print p
                print e

        return ret

    def fetch_xml_data(self, site_id, start_date):
        logging.info("fetch_xml_data site_id=%s, start_date=%s" % (site_id, start_date))
    
        params = self.build_params(site_id, start_date)
        response = self.session.get(self.URL, params=params)

        logging.debug("Cookies: %s" % str(self.session.cookies))
    
        if response.status_code != 200:
            raise Exception("request_error status=%s" % response.status_code)

        return response.text

    def fetch_data(self, site_id, start_date):
        raw_data = self.fetch_xml_data(site_id, start_date)
        logging.debug("raw_date: %s", raw_data)

        result = {}
        for key, reg in self.REG.items():
            match = reg["exp"].search(raw_data)
            if match:
                if reg["is_points"]:
                    result[key] = self.parse_points(match.group(key), start_date)
                else:
                    result[key] = match.group(key)
            else:
                logging.warn("not found %s" % key)
                result[key] = None

        logging.debug("fetch_data result: %s" % result)
        return result
        
class Spider(object):
    def __init__(self, database):
        self.fetcher = DataFetcher() 
        self.db = sqlite3.connect(database)

    def fetch(self, site_id, start_date):
        logging.info("fetcing site_id=%s start_date=%s" % (site_id, start_date))

        cur = self.db.cursor()
        cur.execute("SELECT id, crawl_date FROM site WHERE site_id=?", (site_id,))
        row_id, crawl_date = cur.fetchone()

        data = self.fetcher.fetch_data(site_id, start_date)
        
        cur.execute("UPDATE site SET crawl_date=? WHERE id=?", (to_unix(datetime.datetime.now()), row_id))
        if data["safety_level"]:
            level = data["safety_level"]
            cur.execute("UPDATE site SET safety_level=? WHERE id=?", (level, row_id))
        if data["warning_level"]:
            level = data["warning_level"]
            cur.execute("UPDATE site SET warning_level=? WHERE id=?", (level, row_id))
        if data["flow_points"]:
            points = data["flow_points"]

            for i in range(len(points)): points[i].id=row_id;
            points = map(lambda p: p.to_tuple(), points)

            cur.executemany("INSERT INTO water_flow(sid, date, flow) VALUES(?, ?, ?)", points)
        if data["level_points"]:
            points = data["level_points"]

            for i in range(len(points)): points[i].id=row_id;
            points = map(lambda p: p.to_tuple(), points)
            
            cur.executemany("INSERT INTO water_level(sid, date, level) VALUES(?, ?, ?)", points)

        self.db.commit()

    def get_count(self, site_id, start_date):
        print site_id, start_date
        cur = self.db.cursor()
        cur.execute("SELECT count(*) FROM water_level WHERE sid=? AND date>?", (site_id, to_unix(start_date)))

        count = cur.fetchone()[0]
        return count

    def fetch_all(self, start_date):
        cur = self.db.cursor()
        cur.execute("SELECT id, site_id, site_name FROM site WHERE deleted=0 AND is_crawl=1 ORDER BY crawl_date ASC, id ASC")

        rows = cur.fetchall()
        print "Will fetch %s sites data!" % len(rows)
        
        for (id, site_id, site_name) in rows:
            # If a site which every day have more than 3 numbers data, skip it for protect original site.
            # :)
            #if self.get_count(id, datetime.date.today() - datetime.timedelta(days=5)) > 18:
            #    logging.info("Skip %s!" % site_name)
            #    print "Skip %s!" % site_name
            #    continue

            #print "Fetcing %s id=%s site_id=%s data." % (site_name, id, site_id)
            try:
                self.fetch(site_id, start_date)
            except Exception as e:
                print e
                logging.exception(e)
    
    def fetch_from_last_update(self):
        cur = self.db.cursor()
        cur.execute("SELECT id, site_id, site_name, crawl_date FROM site WHERE deleted=0 AND is_crawl=1 ORDER BY crawl_date ASC, id ASC")

        rows = cur.fetchall()
        for (id, site_id, site_name, crawl_date) in rows:
            crawl_date = to_datetime(crawl_date)
            if datetime.datetime.now() - crawl_date < datetime.timedelta(days=1):
                continue

            date = crawl_date.date() - datetime.timedelta(days=1)
            logging.info("Fetcing %s id=%s site_id=%s data." % (site_name, id, site_id))
            try:
                self.fetch(site_id, date)
            except Exception as e:
                print e
                logging.exception(e)

def run(db_path):
    s = Spider(db_path)
    while True:
        s.fetch_from_last_update()
        time.sleep(300)

if __name__ == "__main__":
    run(DB_PATH)
    #s = Spider(db_path)
    
    #sites = ["81100950"]
    #for site in sites:
    #    s.fetch(site, start_date=datetime.date.today() - datetime.timedelta(days=365)) 
    #s.fetch_all(start_date=datetime.date.today() - datetime.timedelta(days=30))
