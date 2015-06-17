#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import fcntl
import gevent
import syslog
import json
from gevent.socket import wait_read
import gevent_inotifyx as inotify
from urlparse import urlparse


def log(text):
    syslog.syslog(text)


def main_worker():
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    while True:
        global redirect_rules
        wait_read(sys.stdin.fileno())
        param_list = sys.stdin.readline().split(' ')
        parsed_uri = urlparse(param_list[0])
        domain = parsed_uri.netloc
        out = '\n'
        if domain in redirect_rules:
            out = redirect_rules[domain] + out
            log('url found replace to ' + out)
        sys.stdout.write(out)
        sys.stdout.flush()


def reload_config():
    file_name = config_path + '/' + config_name
    if os.path.exists(file_name):
        with open(file_name) as in_file:
            global redirect_rules
            redirect_rules = json.load(in_file)
            log('reload redirect rules ' + str(redirect_rules))
    else:
        log('Config file not exists ' + file_name)


def inotify_event(fd, name):
    while True:
        events = inotify.get_events(fd)
        update = False
        for event in events:
            if event.name == name:
                update = True
        if update:
            reload_config()

fd = inotify.init()
syslog.openlog('SquidPyRedirect', syslog.LOG_PID)
gr = []
config_raw = 'redirect.json'
(config_path, config_name) = os.path.split(config_raw)
if not config_path:
    config_path = os.getcwd()
redirect_rules = {}
reload_config()
try:
    wd = inotify.add_watch(
        fd, config_path, inotify.IN_MODIFY | inotify.IN_CREATE)
    gr.append(gevent.spawn(inotify_event, fd, config_name))
    gr.append(gevent.spawn(main_worker))

    log('Process started')
    gevent.joinall(gr)
finally:
    os.close(fd)
    log('Process stopped')
