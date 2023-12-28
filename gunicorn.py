import os
from multiprocessing import cpu_count

bind = f'0.0.0.0:{os.getenv("PORT")}'
timeouts = 60
max_requests = 1000
workers = cpu_count()

reload = True
name = 'migration_control_web'