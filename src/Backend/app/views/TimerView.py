from app.views import RequestsView, GraphView
import atexit
import logging

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=RequestsView.delete_old_requests,
    trigger=IntervalTrigger(hours=1),
    id='delete_old_requests',
    name='Delete old requests every one hour',
    replace_existing=True)

scheduler.add_job(
    func=GraphView.delete_old_graph_edges,
    trigger=IntervalTrigger(hours=1),
    id='delete_old_graph_edges',
    name='Delete old edges in the nearby users graph every one hour',
    replace_existing=True)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())