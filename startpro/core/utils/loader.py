"""
Created on Dec 2, 2014

@author: Allen
"""

import os
import sys
import functools

from startpro.common.utils.log4py import base_log, log
from startpro.core import settings
from startpro.common.utils.config import Config
from startpro.core.utils.opts import load_script_temp


def load_config(config_file, section):
    """
    load custom configure by section
    """
    config = Config(config_file=config_file)
    settings.CONFIG = config
    for re in config.get_config_list(section):
        setattr(settings, re[0].upper(), re[1])


def get_settings(attr_name, default=None):
    """
    get attribute of settings attribute safety default value
    """
    if hasattr(settings, attr_name.upper()):
        return getattr(settings, attr_name.upper())
    else:
        return default


def safe_init_run(func):
    @functools.wraps(func)
    def _deco(*args, **kwargs):
        loader(**kwargs)
        func(*args, **kwargs)

    return _deco


def loader(**kwargs):
    """
    init context loader
    :param kwargs:
    :return:
    """
    if settings.HAS_LOAD:
        return
    script_name, log_name = get_log_name()
    root_path = os.getcwd()
    root_path = kwargs.get('root_path', root_path)
    # set system context vars
    settings.NAME = script_name
    settings.ROOT_PATH = root_path
    # load configure
    cfg_file = os.path.join(settings.ROOT_PATH, settings.CONFIG_FILE)
    load_config(cfg_file, "common")
    load_config(cfg_file, script_name)
    # init path
    settings.CLIENT_FILE = os.path.join(settings.ROOT_PATH, settings.CLIENT_FILE)
    settings.RESULT_FILE = os.path.join(settings.ROOT_PATH, settings.RESULT_FILE)
    paths = [settings.CLIENT_FILE, settings.RESULT_FILE]
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)
    # set log
    log_path = os.path.join(kwargs.get('log_path', settings.ROOT_PATH), 'log')
    # set mail to address
    base_log.set_mail(get_settings('mail_un', ''), get_settings('mail_pw', ''), get_settings('mail_host', ''))
    base_log.set_mailto(get_settings('mail_to', '').split(','))
    # set log error count limit
    base_log.set_error_limit(int(get_settings('log_error_limit', 50)))
    # set log error time window to flush MemoryHandler
    base_log.set_error_window(int(get_settings('log_error_window', 0)))
    # set log file name
    base_log.set_logfile(kwargs.get('log', None) or log_name, log_path)
    # set log level
    log_level = get_settings('log_level', 'INFO')
    base_log.logger.setLevel(log_level)
    log.setLevel(log_level)
    log.info("init context : {}".format(script_name))
    # set process id
    pid_file = kwargs.get('pid', None) or log_name
    if not pid_file.endswith('.pid'):
        pid_file = '%s.pid' % pid_file
    # write pid file
    with open(os.path.join(settings.CLIENT_FILE, pid_file), 'w') as p_file:
        p_file.writelines(["%s" % os.getpid()])
        p_file.flush()
    # reset load flag
    settings.HAS_LOAD = True


def get_script_name():
    if len(sys.argv) < 3:
        print('[WARN]:need start script name.')
        sys.exit(0)
    script_name = str(sys.argv[2])
    scripts = load_script_temp()
    if not scripts:
        print('[INFO]:please execute command [startpro list] first')
        sys.exit(0)
    try:
        if script_name.isdigit() and script_name not in scripts:
            script_name = scripts.keys()[int(script_name)]
        if script_name not in scripts:
            raise RuntimeError('Unsupported script')
        return script_name, scripts[script_name]
    except Exception:
        print('[ERROR]:Unsupported script.')
        sys.exit(0)


def get_log_name():
    try:
        script_name, _ = get_script_name()
        script_split = script_name.split('.')
        if len(script_split) > 1:
            script_name = script_split[-2]
        log_name = script_split[-1]
        return script_name, log_name
    except:
        print('[INFO]:Please chose a script.')
        sys.exit(0)
