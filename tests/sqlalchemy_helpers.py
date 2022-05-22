from sqlalchemy import event


class QueryCounter:
    def __init__(self, engine):
        self.engine = engine
        self.count = 0

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self.callback)
        return self

    def __exit__(self, *args, **kwargs):
        event.remove(self.engine, "before_cursor_execute", self.callback)

    def callback(self, *args, **kwargs):
        self.count += 1
