#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import fcntl
import gevent
import syslog
import json
import argparse
from gevent.socket import wait_read
import gevent_inotifyx as inotify
from urlparse import urlparse


def log(text):
    syslog.syslog(text)


def argParser():
    parser = argparse.ArgumentParser(description=u"Squid redirector %(prog)s",
                                     epilog=u"Эпилог программы %(prog)s")
    parser.add_argument('path',
                        help='Path to configuration file',)
    return parser.parse_args()


def main_worker(redirect_rules):
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    while True:
        wait_read(sys.stdin.fileno())
        param_list = sys.stdin.readline().split(' ')
        parsed_uri = urlparse(param_list[0])
        domain = parsed_uri.netloc
        if not domain:
            res = re.match('^([\w|\.]+):([\d])+', param_list[0])
            if res:
                domain = res.group(1)
        if domain.startswith('www.'):
            domain = domain[4:]
        out = '\n'
        if domain in redirect_rules:
            out = '302:' + redirect_rules[domain] + out
            log('url ' + domain + ' found replace to ' + out)
        sys.stdout.write(out)
        sys.stdout.flush()


def reload_config(file_name):
    if os.path.exists(file_name):
        with open(file_name) as in_file:
            redirect_rules = json.load(in_file)
            log('reload redirect rules ' + str(redirect_rules))
            return redirect_rules
    else:
        log('Config file not exists ' + file_name)
    return {}


def inotify_event(file_path, rules):
    fd = inotify.init()
    (config_path, config_name) = os.path.split(file_path)
    if not config_path:
        config_path = os.getcwd()
    file_name = config_path + '/' + config_name
    wd = inotify.add_watch(
        fd, config_path, inotify.IN_MODIFY | inotify.IN_CREATE)
    rules.update(reload_config(file_name))
    while True:
        events = inotify.get_events(fd)
        update = False
        for event in events:
            if event.name == config_name:
                update = True
        if update:
            rules.update(reload_config(file_name))


def main(file_path):

    syslog.openlog('SquidPyRedirect', syslog.LOG_PID)
    gr = []

    redirect_rules = {}
    gr.append(gevent.spawn(inotify_event, file_path, redirect_rules))
    gr.append(gevent.spawn(main_worker, redirect_rules))

    log('Process started')
    gevent.joinall(gr)


if __name__ == '__main__':
    options = argParser()
    main(options.path)
