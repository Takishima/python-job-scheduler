import os

pjs_dir = os.path.dirname(os.path.realpath(__file__))
job_queue_file = os.path.join(pjs_dir, 'job_queue')

log_file = os.path.join(pjs_dir, 'scheduler.log')
pause_file = os.path.join(pjs_dir, 'AGENT_PAUSED')
running_file = os.path.join(pjs_dir, 'AGENT_RUNNING')

command_name=''.join(['python ', os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 'pjs_agent.py')
    )])

def read_job_from_line(line):
    return [i.strip().lstrip('*# ') for i in line.split(',')]

def remake_list(infile, mark_done=False):
    qfile = open(infile, 'w')
    bakfile = open(infile + '.bak','r')
    for line in bakfile:
        if mark_done and line.startswith('#'):
            line = '*' + line[1:]
        qfile.write(line)
    qfile.close()
    bakfile.close()
    return 0
