'''
This module implements a simple job scheduler in Python based on a file
containing the job list.

The format of the file is:
job_title , job_command
job_title2 , job_command2
...

Completed job are marked by prepending a '*' to any line.
When stopping the PJS, all lines qith uncompleted jobs are prepended with '#'
until current running job is finished

====
Modified from the original 'Very Simple Python Queue Manager' found at
http://verahill.blogspot.ch/2012/03/very-simple-python-queue-manager.html:

Rudimentary queue manager. Handles a single node,
submitting a series of jobs in sequence. use python v2.4-2.7
'''

import logging
import os
import subprocess
import time
import datetime

import pjs_common as pjs

# ==============================================================================
# Functions to execute the job queue

def launchjob(job):
    job_name, job_cmd = job

    start_time = time.time()
    # job_cmd = os.path.join(job_cmd)
    proc = subprocess.Popen(job_cmd, shell=True)
    i = proc.wait()
    elapsed = time.time() - start_time
    d = datetime.timedelta(0, elapsed)
    if (i == 0):
        logger.info('\tJob *' + job_name + '* successful'
                    +'\n\tElapsed time ' + str(d))
    else:
        logger.error('\tJob *' + job_name + '* failed')
    return i

def get_next_job(infile):
    qfile = open(infile, 'r')
    bakfile = open(infile + '.bak','w')
    job_name=''
    job_cmd=''
    for line in qfile:
        tmp_n, tmp_c = pjs.read_job_from_line(line)
        if line.startswith('#'):
            line = '*' + line[1:]
        elif not line.startswith('*'):
            if job_cmd == '' and (tmp_c != '' or tmp_n != ''):
                job_name, job_cmd = tmp_n, tmp_c
                line = '#' + line
        bakfile.write(line)
    qfile.close()
    bakfile.close()
    return (job_name, job_cmd)

def main(infile):
    rfile = open(pjs.running_file, 'w')
    rfile.close()
    jobs=1
    while (jobs == 1 and not os.path.exists(pjs.pause_file)):
        newjob = get_next_job(infile)
        pjs.remake_list(infile)
        if newjob[0] != '' or newjob[1] != '':
            jobs = 1
            if newjob[1] != '':
                logger.info('\tStarting job *' + newjob[0] + '*')
                echojob = launchjob(newjob)
            # if os.path.exists(newjob[1]):
            #     echojob = launchjob(newjob)
            # elif newjob[1] != '':
            #     logger.error('\tUnable to find script ' + newjob[1] 
            #                  + ' for job *' + newjob[0]+ '*')
            else:
                logger.error('\tJob *' + newjob[0] + '* has an empty command')                
        else:
            # print 'No jobs found at ' + str(time.asctime())
            jobs = 0
        pjs.remake_list(infile, True)

    os.remove(pjs.running_file)
    return 0



# ==============================================================================

if __name__ == "__main__":
    # ==========================================================================
    # Setup logging system

    logger = logging.getLogger('Python Job Scheduler')
    hdlr = logging.FileHandler(pjs.log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s\n %(message)s\n')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    # ==========================================================================

    main(pjs.job_queue_file)
    # rewind(pjs.job_queue_file)


