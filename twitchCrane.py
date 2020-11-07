import pydle
import serial


# Simple echo bot.
class TwitchCrane(pydle.Client):
    serialDevice: serial.Serial
    onMessageCallback: staticmethod

    def set_serial_device(self, serialDevName):
        self.serialDevice = serial.Serial(serialDevName, baudrate=9600)

    def set_message_callback(self, method):
        self.onMessageCallback = method

    async def on_connect(self):
        await self.join('#jungtaejune')

    async def on_message(self, target, source, message):
        # 메세지 핸들러
        self.onMessageCallback.__func__((target, source, message))
        if message.startswith("!위"):
            self.serialDevice.write(b"w")
            print("위 Hooked!")
            pass
        elif message.startswith("!아래"):
            self.serialDevice.write(b"s")
            print("아래 Hooked!")
            pass
        elif message.startswith("!왼쪽"):
            self.serialDevice.write(b"a")
            print("왼쪽 Hooked!")
            pass
        elif message.startswith("!오른쪽"):
            self.serialDevice.write(b"d")
            print("오른쪽 Hooked!")
            pass
        elif message.startswith("!내려"):
            self.serialDevice.write(b"f")
            print("내려 Hooked!")
            pass


if __name__ == '__main__':
    client = TwitchCrane('TwitchCrane')
    client.set_serial_device("COM1")
    client.run('irc.chat.twitch.tv', port=6697, tls=True, tls_verify=False, password="***REMOVED***")
