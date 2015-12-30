#! /bin/env python
# -*- coding:utf-8 -*-

#  //pip/pip3 install Pysocks
#  //pip install requests
#  pip install requesocks

import socks
import socket
import requests

import requesocks
#import traceback
import sys
import timeit

import urllib  
import urllib2
import cookielib
import re
import string

import threading
import time

class WhySpider:
    def __init__(self):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(\
                urllib2.HTTPCookieProcessor(self.cookie_jar))
        self.headers = {'User-Agent' : \
                'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:28.0)'\
                ' Gecko/20100101 Firefox/28.0'}

    def send_get(self, get_url):
        result = ''
        try:
            my_request = urllib2.Request(url = get_url, headers = self.headers)
            result = self.opener.open(my_request).read()
        except Exception as e:
            print('Exception : ' + e)
        return result

    def send_post(self, post_url, post_data):
        result = ''
        try:
            my_request = urllib2.Request(url = post_url,\
                    data = post_data, headers = self.headers)
            result = self.opener.open(my_request).read()
        except Exception as e:
            print ('Exception : ' + e)
        return result
    
    def set_computer(self):
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:28.0)'\
                ' Gecko/20100101 Firefox/28.0'
        self.headers = { 'User-Agent' : user_agent }    

    def set_mobile(self):
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X)'\
                ' AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0'\
                ' Mobile/10A403 Safari/8536.25'
        self.headers = { 'User-Agent' : user_agent }    

class WorkThread (threading.Thread):
    # static
    entries_enable = list()
    threadLock     = threading.Lock()
    progress       = 0
    progressLock   = threading.Lock()

    def __init__(self, entry, counter, total_count):
        threading.Thread.__init__(self)
        self.counter     = counter
        self.total_count = total_count
        self.session     = requesocks.session()
        self.entry       = entry

    def run(self):
        current = str(self.counter) + '/' + str(self.total_count)
        self.printr('------------*- Starting ['+current+'] -*--------------') 
        self.socks_proxy_test_entry()
        self.printr('************** Finished ['+current+'] ****************')
        self.__class__.progressLock.acquire()
        self.__class__.progress = self.__class__.progress + 1
        self.__class__.progressLock.release()

    def get_progress(self):
        n = float(self.__class__.progress) / float(self.total_count)
        return '%.2f%%' % (n * 100)

    def printr(self, msg):
        threads_count = 'jobs: '+ str(threading.activeCount()) + ', '
        progress = 'Completed: ' + self.get_progress() 
        if msg == '':
            sys.stdout.write('\r' + threads_count + progress)
        else:
            sys.stdout.write('\r' + str(msg) + '\n' + threads_count + progress)
        sys.stdout.flush()

    def socks_proxy_test_entry(self):
        current = '[' + str(self.counter) + '/' + str(self.total_count) + '] '
        host    = self.entry['host']
        port    = int(self.entry['port'])
        version = int(self.entry['version'][-1])
        Country = self.entry['country']
        self.printr(current + \
                'host = %s, port = %s, protocol = socks%s, Country = %s'\
                % (host, port, version, Country))
        if   version == 4:
            proxy = 'socks4://' + self.entry['host'] + ':' +self.entry['port'] 
        elif version == 5:
            proxy = 'socks5://' + self.entry['host'] + ':' +self.entry['port'] 
        else:
            self.printr(current + 'bad socks-proxy version')
            return 3
        self.session.proxies = {'http': proxy, 'https': proxy}

        def requesocks_test():
             #self.session.get('http://baidu.com')
             self.session.get('http://baidu.com', timeout = 20)
             #resp = self.session.get('http://baidu.com')
             #resp.status_code, resp.headers['content-type'], resp.text

        try:
            t = timeit.Timer(requesocks_test)
            #ret = str(t.timeit(2))
            ret = t.repeat(3, 1)
            for k in range(0, len(ret)):
                ret[k] = round(ret[k], 3)

            self.entry['time_consuming'] = str(ret)
            
            #可选的timeout参数不填时将一直阻塞直到获得锁定
            self.__class__.threadLock.acquire()
            self.__class__.entries_enable.append(self.entry)
            self.__class__.threadLock.release()

            self.printr(current + self.entry['version'] \
                    + ': ' + host + ':' + self.entry['port'] + ' ' + Country)
            self.printr(current + 'time consuming (3 times): ' + str(ret))
            self.printr(current + str(self.entry))
            return 0
        except Exception as e:
            self.printr('[Error] ' + current + str(e))
            return 2


def print_safe(msg):
    sys.stdout.write(msg)
    sys.stdout.write('\n')
    sys.stdout.flush()

def requests_test():
    requests.get('http://baidu.com', timeout = 20)
    #r = requests.get('http://baidu.com')
    #print(r.text) # check ip

def socks_proxy_test(host, port, version = 5, Country = 'unknown'):
    print('\nhost = %s, port = %s, protocol = socks%s, Country = %s'\
            %(host, port, version, Country))
    port    = int(port)
    version = int(version)
    if version == 4:
        socks.set_default_proxy(socks.SOCKS4, host, port)
    elif version == 5:
        socks.set_default_proxy(socks.SOCKS5, host, port)
    else:
        print('bad socks-proxy version')
        return 3
    socket.socket = socks.socksocket
    try:
        t = timeit.Timer('requests_test()', \
                'from __main__ import requests_test')
        #ret = str(t.timeit(2))
        ret = str(t.repeat(3, 1))
        print('socks' + str(version) + ': ' + host + ':' + str(port)\
                + ' ' + Country)
        print('time consuming (3 times): ' + ret)
        return 0
    except Exception as e:
        print(e)
        return 2


def auto(max_jobs):
    my_spider = WhySpider()
    response = my_spider.send_get('http://socks-proxy.net/')

    #print(response)
    print('')
    pattern = re.compile('<tr><td>(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})</td>'\
            '<td>(\d+)</td><td>([A-Z]{2})</td><td>([a-zA-Z,\s]+)</td>'\
            '<td>([Ss]ocks[45])</td><td>(\w+)</td><td>(\w+)</td>'\
            '<td>(\d{1,3}[^<]+)</td></tr>', re.S)
    items = re.findall(pattern, response)
    entries = list() 
    for item in items:
        entry = {'host': item[0], 'port': item[1], 'code': item[2], \
                'country': item[3], 'version': item[4], 'anonymity': item[5],\
                'https': item[6], 'last_checked': item[7]}
        entries.append(entry)

    print('')
    print('%-15s %-5s %-4s %-18s %-7s %-9s %-5s %-13s' % \
            ('Host/Ip Address', 'Port', 'Code', 'Country', 'Version', \
            'Anonymity', 'Https', 'Last Checked'))
    for entry in entries:
        print('%-15s %-5s %-4s %-18s %-7s %-9s %-5s %-13s' % \
                (entry['host'], entry['port'], entry['code'], \
                entry['country'], entry['version'], entry['anonymity'], \
                entry['https'], entry['last_checked']))


    count_entries = len(entries)
    print('\n[info]found ' + str(count_entries) \
            + ' entry points from http://socks-proxy.net')

    threads = list()
    counter = 1
    for entry in entries:
        while True:
            if threading.activeCount() < int(max_jobs):
                #WorkThread(entry, counter, count_entries).start()
                work_thread = WorkThread(entry, counter, count_entries)
                work_thread.start()
                threads.append(work_thread)
                counter = counter + 1
                break
            else:
                time.sleep(1)

    # join all threads
    for thread in threads:
        thread.join()

    print('\n\n')
    line1 = '==============================================================='
    line2 = '---------------------------------------------------------------'
    count_entries_enable = len(WorkThread.entries_enable)
    if count_entries_enable != 0:
        print('[info]found ' + str(count_entries_enable) \
                + ' available entry points :')
        print(line1)
        print('%-15s %-5s %-18s %-7s %s' % \
                ('Host/Ip Address', 'Port', 'Country', \
                'Version', 'Time Consuming'))
        print(line2)
        for entry in WorkThread.entries_enable:
            print('%-15s %-5s %-18s %-7s %s' % \
                    (entry['host'], entry['port'], entry['country'], \
                    entry['version'], entry['time_consuming']))
        print(line1)
    else:
        print('[warning]No available entry was found, please try again later.')
        

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if argv_len == 4:
        host = sys.argv[1]
        port = sys.argv[2]
        version = sys.argv[3]
        socks_proxy_test(host, port, version)
    elif argv_len == 2 and sys.argv[1] == 'auto':
        default_jobs = 40
        auto(default_jobs)
    elif argv_len == 3 and sys.argv[1] == 'auto' \
            and sys.argv[2].isdigit() and int(sys.argv[2]) > 0:
        auto(sys.argv[2])
    else:
        print('Usage:')
        print('\t' + sys.argv[0] + ' auto [<max-jobs>]')
        print('\t' + sys.argv[0] + ' <host> <port> <socks-version>')
        #print('Option:')
        #print('  xxxx')
        #print('  xxxx')
        #print('  xxxx')
        #print('  xxxx')
        print('Examples:')
        print('')
        print('$ # Automatically get socks proxy entries from \
http://socks-proxy.net/ ')
        print('$ # and, Identify the available entries with default 40 jobs.')
        print('$ ' + sys.argv[0] + ' auto')
        print('')
        print('$ # Automatically get socks proxy entries from \
http://socks-proxy.net/ ')
        print('$ # and, Identify the available entries with 38 jobs.')
        print('$ ' + sys.argv[0] + ' auto 38')
        print('')
        print('$ # Verify if socks4://127.0.0.1:1080 is available.')
        print('$ ' + sys.argv[0] + ' 127.0.0.1 1080 4')
        print('')
        print('$ # Verify if socks5://127.0.0.1:1080 is available.')
        print('$ ' + sys.argv[0] + ' 127.0.0.1 1080 5')
        print('')
        print('$ # Verify if socks5://socks5-proxy.examples.com is available.')
        print('$ ' + sys.argv[0] + ' socks5-proxy.examples.com 1080 5')
        exit(1)
        
