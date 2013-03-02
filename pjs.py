#! /usr/bin/env python

import crontab
import os
import sys
import pjs_common as pjs

# ==============================================================================
# Usage message and helper functions

def options2str(options):
    tmp = ''.join(sorted([i + ' | ' for i in options.keys()]))
    return tmp.rstrip(' | ')

def print_usage(options):
    print 'Python Job Scheduler'
    print '''usage: pjs.py [ %s ]''' % options2str(options)

def is_in_path(program):
    '''Looks for program in the PATH'''
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath and fpath != '.':
        return is_exe(program)
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False

# ==============================================================================
# Function for all possible actions

def start_scheduler():
    if os.path.exists(pjs.pause_file):
        os.remove(pjs.pause_file)
    cron = crontab.CronTab()
    if len(cron.find_command(pjs.command_name)) == 0:
        job = cron.new(command=pjs.command_name)
        job.minute.every(30)
        cron.write()
    print 'Added scheduler as cron task...'

def pause_scheduler():
    if os.path.exists(pjs.pause_file):
        os.remove(pjs.pause_file)
        print 'Resuming PJS at next cron task'
    else:
        print 'PJS paused'
        pfile = open(pjs.pause_file, 'w').close()

def stop_scheduler():
    pause_scheduler()
    cron = crontab.CronTab()
    cron.remove_all(pjs.command_name)
    cron.write()
    print 'Removed scheduler as cron task...'

def status_scheduler():
    if not os.path.exists(pjs.job_queue_file):
        open(pjs.job_queue_file, 'w').close()
        print '''Created job queue file: %s''' % pjs.job_queue_file

    qfile = open(pjs.job_queue_file, 'r')
    running = []
    done=[]
    queued=[]
    for line in qfile:
        if line.startswith('#'):
            running += [pjs.read_job_from_line(line)]            
        elif line.startswith('*'):
            done += [pjs.read_job_from_line(line)]
        else:
            queued += [pjs.read_job_from_line(line)]
    qfile.close()

    if len(crontab.CronTab().find_command(pjs.command_name)) == 0:
        cron_status = '(NOT scheduled)'
    else:
        cron_status = '(scheduled)'
        
    print '''Python Job Scheduler current status:'''
    if os.path.exists(pjs.running_file):
        print '\tPJS is running %s' % cron_status
    elif os.path.exists(pjs.pause_file):
        print '\tPJS is paused %s' % cron_status
    else:
        print '\tPJS is not running %s' % cron_status

    if len(running) != 0:
        print '''\t*Currently running job*'''
        for i in running:
            print '\t\t%s\t\t%s' % (i[0], i[1])
    

    print '''\n\t*Job Queue*'''
    if len(queued) == 0:
        print '\t\tNo jobs queued at this time'
    else:
        for i in queued:
            print '\t\t%s\t\t%s' % (i[0], i[1])

    if len(done) != 0:
        print '\n\t*Completed Jobs*'
        for i in done:
            print '\t\t%s\t\t%s' % (i[0].lstrip('*'), i[1])

def add_job():
    if len(sys.argv) < 4:
        print '''    ERROR: missing *job_name* and/or *job_cmd*'''
    elif len(sys.argv) != 4:
        print '''    ERROR: too many arguments'''
    else:
        job_name, job_cmd = sys.argv[2:4]
        if not is_in_path(job_cmd):
            job_cmd = os.path.abspath(os.path.join(os.getcwd(), job_cmd))
        qfile = open(pjs.job_queue_file, 'a')
        qfile.write(''.join([job_name, ', ', job_cmd, '\n']))
        qfile.close()

def delete_job():
    if len(sys.argv) < 3:
        print '''    ERROR: missing *job_name*'''
    elif len(sys.argv) != 3:
        print '''    ERROR: too many arguments'''
    else:
        delete_job_helper(pjs.job_queue_file, sys.argv[2], delete_all=False)

def delete_many_job():
    if len(sys.argv) < 3:
        print '''    ERROR: missing *job_name*'''
    elif len(sys.argv) != 3:
        print '''    ERROR: too many arguments'''
    else:
        delete_job_helper(pjs.job_queue_file, sys.argv[2], delete_all=True)

def delete_all_jobs():
    if len(sys.argv) > 2:
        print '''    ERROR: too many arguments'''
    else:
        qfile = open(pjs.job_queue_file, 'w')
        qfile.close()

def edit_job_queue():
    os.execl(os.getenv('EDITOR'), os.getenv('EDITOR'), pjs.job_queue_file)

# ==============================================================================
# Log file related functions

def show_log():
    print 'Python Job Scheduler\n'
    if not os.path.exists(pjs.log_file):
        clear_log()
    lfile = open(pjs.log_file, 'r')
    for line in lfile:
        print line

def clear_log():
    open(pjs.log_file, 'w').close()

# ==============================================================================

def display_help():
    print '''Python Job Scheduler

Possible actions:
    help          Display this help message

    start         Start PJS (set cron task)
    pause         Pause PJS (does not remove cron task)
    stop          Stop PJS (remove cron task) 
                  NB: does not kill a current running PJS
    status        Display PJS status

    log           Print content of log file
    clear         Clear PJS log

    add           Add a job. 
                  Requires 2 arguments: 'job_title' & 'job_cmd'
    edit          Manually edit job queue file (using $EDITOR)
    delete        Cancel first matching job
                  Requires 1 argument: 'job_title'
    delete_many   Cancel all matching jobs
                  Requires 1 argument: 'job_title'
    delete_all    Cancel all jobs
'''

options = { 
    'start' : start_scheduler,
    'pause' : pause_scheduler,
    'stop' : stop_scheduler,
    'status' : status_scheduler,
    'add' : add_job,
    'edit' : edit_job_queue,
    'delete' : delete_job,
    'log' : show_log,
    'clear' : clear_log,
    'delete_many' : delete_many_job,
    'delete_all' : delete_all_jobs,
    'help' : display_help
    }

# ==============================================================================
# Helper functions

def delete_job_helper(infile, job_name, delete_all=False):
    qfile = open(infile, 'r')
    bakfile = open(infile + '.bak','w')
    lines = ''
    found=False
    first=True
    for line in qfile:
        tmp_n, tmp_c = pjs.read_job_from_line(line)
        if tmp_n != job_name:
            lines += line
        else:
            found = True
            if not delete_all and not first:
                lines += line
            else:
                first = False

    bakfile.write(lines)
    qfile.close()
    bakfile.close()
    pjs.remake_list(infile)
    return found

# ==============================================================================

if len(sys.argv) <= 1:
    print_usage(options)
    print '''    ERROR: missing action argument'''
    sys.exit(1)

action = sys.argv[1]

# ==============================================================================
# Actual execution of program

try:
    options[action]()
except KeyError:
    print_usage(options)
    print '''    ERROR: unknown action argument'''
    sys.exit(1)
