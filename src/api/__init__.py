from typing import List


class Client:

    def __init__(self):
        self.receive_bindings = {}

    def on_message_received(self, header: str, values: List[str]):
        bindings = self.receive_bindings.get(header)
        if bindings is not None:
            for callback in bindings:
                callback(values)
                self.on_registered_message_received(header, values)

    def on_registered_message_received(self, header: str, values: List[str]):
        pass
