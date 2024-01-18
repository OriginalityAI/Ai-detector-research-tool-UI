from threading import Lock
class SharedData:
    def __init__(self):
        self.task_status = {}
        self.lock = Lock()

shared_data = SharedData()