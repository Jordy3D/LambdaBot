import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

        self.usecase = None

    def start(self, usecase=None):
        self.start_time = time.time()
        self.usecase = usecase if usecase != None else self.usecase

    def stop(self, usecase=None):
        self.end_time = time.time()
        self.usecase = usecase if usecase != None else self.usecase

    def __str__(self, precision=2):
        precision = f"0.{precision}f"
        if self.usecase != None:
            return f"Time taken to {self.usecase}: {self.end_time - self.start_time:{precision}}"
        return f"Time taken: {self.end_time - self.start_time:{precision}}"