#! /bin/env python
# -*- coding:utf-8 -*-

#  pip install PySocks
#  pip install requests
#  pip install requesocks

import socks
import socket
import requests

import requesocks # python 2.7.x
#import traceback
import sys
#import timeit

import urllib
import urllib2
import cookielib
import re
import string

import threading
import time
import version

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
            print('Exception: ' + str(e))
        return result

    def send_post(self, post_url, post_data):
        result = ''
        try:
            my_request = urllib2.Request(url = post_url,\
                    data = post_data, headers = self.headers)
            result = self.opener.open(my_request).read()
        except Exception as e:
            print ('Exception: ' + str(e))
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
    progress       = 1
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
            t = SPT_Timer(self.printr, current)
            t.action(requesocks_test, 3, 4)
            ret = t.get_result_format(2)

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
            blank_placeholder = '            '
            self.printr('[Warning] ' + current + str(e) + blank_placeholder)
            return 2

#import os
#def get_module():
#    def main_module_name():
#        mod = sys.modules['__main__']
#        file = getattr(mod, '__file__', None)
#        return file and os.path.splitext(os.path.basename(file))[0]
#
#    def modname(fvars):
#        file, name = fvars.get('__file__'), fvars.get('__name__')
#        if file is None or name is None:
#            return None
#        if name == '__main__':
#            name = main_module_name()
#        return name
#
#    return modname(globals())

def print_safe(msg):
    sys.stdout.write(msg)
    sys.stdout.write('\n')
    sys.stdout.flush()

class SPT_Timer:
    def __init__(self, printv = print_safe, pre_str = ''):
        self.counter = 0
        self.printv  = printv
        self.pre_str = pre_str
        self.result  = list()
        self.timeout = 'timeout'
    def action(self, expr, num = 3, try_max = 10):
        if (self.counter >= num):
            return

        for loop in range(self.counter, num):
            start = time.time()
            try:
                expr()
                consuming = time.time() - start
                self.counter = self.counter + 1
                self.printv(self.pre_str + 'Successful connection: '\
                        + str(self.counter) + ' times, time-consuming: '\
                        + str(consuming) + ' s')
                self.result.append(consuming)
                if (self.counter >= num):
                    break
            except Exception as e:
                e = str(e)
                if 'NoneType' in e:
                    e = self.timeout
                blank_placeholder = '                            '
                if len(self.pre_str + e) <= 40:
                    self.printv(self.pre_str + e + blank_placeholder)
                else:
                    self.printv(self.pre_str + e)

                self.result.append(self.timeout)
                if (len(self.result) < try_max):
                    #self.printv(self.pre_str + 'one more try' \
                    self.printv(self.pre_str + 'try again...' \
                            + blank_placeholder)
                    self.action(expr, num, try_max)
                break

    def get_result(self):
        return self.result

    def get_result_format(self, valid = 2, max_count = 3):
        valid_counter = 0
        ret = list()
        for v in self.result:
            if isinstance(v, float):
                valid_counter = valid_counter + 1
                ret.append(round(v, 3))

        if valid_counter < valid:
            raise Exception('the number of valid values is less than '\
                    + str(valid))

        if valid_counter < max_count:
            for i in range(0, max_count - valid_counter):
                ret.append(self.timeout)

        return ret



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
        t = SPT_Timer()
        t.action(requests_test)
        ret = t.get_result()
        print('socks' + str(version) + ': ' + host + ':' + str(port)\
                + ' ' + Country)
        print('time consuming (' + str(len(ret)) + ' times): ' + str(ret))
        return 0
    except Exception as e:
        print(e)
        return 2

def auto(max_jobs):
    default_timeout = 20
    socket.setdefaulttimeout(default_timeout)
    print('[info] Getting the list of SOCKS proxy sites from '\
            'http://socks-proxy.net, please be patient...')
    my_spider = WhySpider()
    response = my_spider.send_get('http://socks-proxy.net/')
    if response == '':
        print('[Error] please try again later')
        exit(-1)

    #print(response)
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


def show_version():
    v = version.script_name + ' v' + version.__version__
    print(v)

def check_upgrade():

    releases = 'https://github.com/DD-L/socks-proxy-tester/releases'
    upgrade_check_default = 'https://raw.githubusercontent.com/DD-L'\
            '/socks-proxy-tester/master/version.py'
    if version.upgrade_check == '' or version.upgrade_check == None:
        upgrade_check = upgrade_check_default
    else:
        upgrade_check = version.upgrade_check

    default_timeout = 10
    socket.setdefaulttimeout(default_timeout)
    print('[info] Checking for upgrade from ' + upgrade_check + \
            ', please be patient...')

    version_spider = WhySpider()
    response = version_spider.send_get(upgrade_check_default)
    if response == '':
        print('[Error] please try again later')
        exit(-1)
    exec(response)
    if cmp_version(version.__version__, __version__) < 0:
        v = script_name + ' v' + __version__
        print('\nFind a new release: ' + v + ', Please go to ' + releases \
                + ' to download the new version')
    else:
        print('\nNo new release')


def cmp_version(v1, v2):
    assert(isinstance(v1, str))
    assert(isinstance(v2, str))
    ver1, ver2 = v1.split('.'), v2.split('.')
    loop = min(len(ver1), len(ver2))
    for i in range(0, loop):
        try:
            vs = int(ver1[i]) - int(ver2[i])
        except ValueError:
            vs = cmp(ver1[i], ver2[i])
        if vs != 0:
            return vs
    return 0


def usage():
        print('Usage:')
        print('\t' + sys.argv[0] + ' auto [<max-jobs>]')
        print('\t' + sys.argv[0] + ' <host> <port> <socks-version>')
        print('\t' + sys.argv[0] + ' [<option>]')
        print('Option:')
        print('  -h, --help         Print this message and exit')
        print('  -v, --version      Show version')
        print('  --check-upgrade    Check for upgrade')
        print('')
        print('Examples:')
        print('')
        print('$ # Automatically get socks proxy entries from \
http://socks-proxy.net/ ')
        print('$ # and, Identify the available entries with default 40 jobs.')
        print('$ ' + sys.argv[0] + ' auto')
        print('')
        print('$ # Automatically get socks proxy entries from \
http://socks-proxy.net/ ')
        print('$ # and, Identify the available entries with 80 jobs.')
        print('$ ' + sys.argv[0] + ' auto 80')
        print('')
        print('$ # Verify if socks4://127.0.0.1:1080 is available.')
        print('$ ' + sys.argv[0] + ' 127.0.0.1 1080 4')
        print('')
        print('$ # Verify if socks5://127.0.0.1:1080 is available.')
        print('$ ' + sys.argv[0] + ' 127.0.0.1 1080 5')
        print('')
        print('$ # Verify if socks5://socks5-proxy.examples.com is available.')
        print('$ ' + sys.argv[0] + ' socks5-proxy.examples.com 1080 5')

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if argv_len == 4:
        host = sys.argv[1]
        port = sys.argv[2]
        version = sys.argv[3]
        socks_proxy_test(host, port, version)
    elif argv_len == 3 and sys.argv[1] == 'auto' \
            and sys.argv[2].isdigit() and int(sys.argv[2]) > 0:
        auto(sys.argv[2])
    elif argv_len == 2:
        if sys.argv[1] == 'auto':
            default_jobs = 40
            auto(default_jobs)
        elif sys.argv[1] == '-v' or sys.argv[1] == '--version':
            show_version()
        elif sys.argv[1] == '--check-upgrade':
            check_upgrade()
        else:
            usage()
            exit(1)
    else:
        usage()
        exit(1)

    exit(0)

