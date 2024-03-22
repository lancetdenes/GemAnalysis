import Mysbatch_
import sys 

cmd = 'python track_processing.py %s'%sys.argv[1]
scriptOptions = {'jobname':'track_nuc_gems','time':'12:00:00','partition':'cpu_short','mem-per-cpu':'2gb', 'cpus-per-task':'4', 'gres':'0'}
Mysbatch_.launchJob(cmd,scriptOptions)