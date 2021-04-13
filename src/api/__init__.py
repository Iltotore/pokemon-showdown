from typing import List, Callable


class WithHeader:

    def __init__(self, f):
        self.f = f


class Client:

    def __init__(self):
        self.receive_bindings = {}

    def on_message_received(self, header: str, values: List[str]):
        bindings = self.receive_bindings.get(header)
        print(bindings)
        if bindings is not None:
            if isinstance(bindings, Callable):
                bindings = [bindings]
            for callback in bindings:
                if isinstance(callback, WithHeader):
                    callback.f(header, values)
                else:
                    callback(values)
            self.on_registered_message_received(header, values)

    def on_registered_message_received(self, header: str, values: List[str]):
        pass
