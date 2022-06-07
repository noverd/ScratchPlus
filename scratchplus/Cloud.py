import websocket
import json
import time
import threading
from pymitter import EventEmitter
import string


class Encoder():
    def __init__(self,
                 codec="""AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789 -_`~!@#$%^&*()+=[];:'"\|,.<>/?}{"""):
        self.codec = codec

    def decode(self, value) -> str:
        out = str()
        value = str(value)
        y = 0
        for i in range(0, len(value) // 2):
            x = self.codec[int(str(value[y]) + str(value[int(y) + 1])) - 1]
            out = str(out) + str(x)
            y += 2
        return out

    def encode(self, text) -> str:
        out = ""
        _len = int(len(text))
        for i in range(0, _len):
            try:
                x = int(self.codec.index(text[i]) + 1)
                if x < 10:
                    x = str(0) + str(x)
                out = out + str(x)
            except ValueError:
                raise ValueError('Symbol not supported')
        return out


class CloudScCodeVariable:
    def __init__(self, name: str, value: str, Encoder):
        self.name = name
        self.value = value
        self.Encoder = Encoder

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def decode(self, data):
        return self.Encoder.decode(self.value)

    def encode(self):
        return self.Encoder.encode(self.value)


class CloudConnection(EventEmitter):
    def __init__(self, project_id: int, client, website="scratch.mit.edu", ScCode=CloudScCodeVariable, auth=True,
                 Encoder=Encoder()):
        EventEmitter.__init__(self)
        self.ScCode = ScCode
        self.encoder = Encoder
        self._client = client
        self._website = website
        self.auth = auth
        self.connect(project_id)

    def _send_packet(self, packet):
        self._ws.send(json.dumps(packet) + "\n")

    def connect(self, project_id):
        if project_id:
            self.project_id = project_id
        self._ws = websocket.WebSocket()
        self._cloudvariables = []
        self._timer = time.time()
        if self.auth:
            self._ws.connect(
                f"wss://clouddata.{self._website}",
                cookie="scratchsessionsid=" + self._client.session_id + ";",
                origin=self._website,
                enable_multithread=True,
            )  # connect the websocket( Auth
        else:
            self._ws.connect(
                f"wss://clouddata.{self._website}",
                origin=self._website,
                enable_multithread=True,
            )  # connect the websocket
        self._send_packet(
            {
                "method": "handshake",
                "user": self._client.username,
                "project_id": str(self.project_id),
            }
        )
        self.emit("handshake")
        response = self._ws.recv().split("\n")
        for variable in response:
            try:
                variable = json.loads(str(variable))
            except:
                pass
            else:
                self._cloudvariables.append(
                    self.ScCode(variable["name"], variable["value"], self.encoder)
                )
        self._start_cloud_var_loop()

    def set_cloud_variable(self, variable, value):
        if time.time() - self._timer > 0.1:
            if not str(value).isdigit():
                raise ValueError(
                    "Cloud variables can only be set to a combination of numbers"
                )
            try:
                packet = {
                    "method": "set",
                    "name": (
                        "☁ " + variable if not variable.startswith("☁ ") else variable
                    ),
                    "value": str(value),
                    "user": self._client.username,
                    "project_id": str(self.project_id),
                }
                self._send_packet(packet)
                self.emit("outgoing", packet)
                self._timer = time.time()
                for cloud in self._cloudvariables:
                    if (
                            cloud.name == "☁ " + variable
                            if not variable.startswith("☁ ")
                            else variable
                    ):
                        cloud.value = value
                        self.emit("set", cloud)
                        break
            except (
                    BrokenPipeError,
                    websocket._exceptions.WebSocketConnectionClosedException,
            ):
                self.connect()
                time.sleep(0.1)
                self.set_cloud_variable(variable, value)
                return
        else:
            time.sleep(time.time() - self._timer)
            self.set_cloud_variable(variable, value)

    def _cloud_var_loop(self):
        while True:
            if self._ws.connected:
                response = self._ws.recv()
                response = json.loads(response)
                for cloud in self._cloudvariables:
                    if response["name"] == cloud.name:
                        cloud.value = response["value"]
                        self.emit("set", cloud)

            else:
                self.connect()

    def _start_cloud_var_loop(self):
        """Will start a new thread that looks for the cloud variables and appends their results onto cloudvariables"""
        thread = threading.Thread(target=self._cloud_var_loop)
        thread.start()

    def get_cloud_variable(self, name):
        try:
            var = next(
                x
                for x in self._cloudvariables
                if x.name == ("☁ " + name if not name.startswith("☁ ") else name)
            )
            return var
        except StopIteration:
            raise ValueError(
                "Variable '"
                + ("☁ " + name if not name.startswith("☁ ") else name)
                + "' is not in this project"
            )
