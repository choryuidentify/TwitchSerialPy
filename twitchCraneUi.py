from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.ttk import *

from twitchCrane import TwitchCrane

import queue
import threading

import asyncio

import sys
import glob
import serial


class TwitchCraneUi:
    oauthToken: str

    def __init__(self):
        # 화면 표시는 최대 300줄만
        self.sizeOfLinesMax = 300
        self.sizeOfLines = 0

        self.queue = queue

        self.window = Tk()

        self.window.title("똘삼크레인 By Choryu Park")

        self.window.geometry('345x218')

        self.combo = Combobox(self.window, state="readonly")

        self.button = Button(self.window, text="선택", command=self.clicked)

        self.txt = scrolledtext.ScrolledText(self.window, width=46, height=14)

        self.combo.grid(column=0, row=0)
        self.button.grid(column=1, row=0)
        self.txt.grid(column=0, row=1, columnspan="2")

    @staticmethod
    def serial_ports():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    @staticmethod
    def connect_to_twitch_and_serial(loop, queue, ser, oauth):
        asyncio.set_event_loop(loop)
        client = TwitchCrane('TwitchCrane')
        client.set_serial_device(ser)
        client.set_message_callback(staticmethod(lambda x: queue.put(x)))
        loop.run_until_complete(
                client.run('irc.chat.twitch.tv', port=6697, tls=True, tls_verify=False,
                           password=oauth)
            )

    def read_queue(self):
        """ Check for updated temp data"""
        try:
            while self.queue.qsize() > 0:
                self.sizeOfLines += 1
                temp = self.queue.get_nowait()
                (target, source, message) = temp
                self.txt.configure(state='normal')
                self.txt.insert(END, "\n" + source + ", " + message)
                if self.sizeOfLines >= self.sizeOfLinesMax:
                    self.txt.delete("1.0", '1.end+1c')
                self.txt.configure(state='disabled')
                self.txt.see(END)
        except queue.Empty:
            # It's ok if there's no data to read.
            # We'll just check again later.
            pass
        # Schedule read_queue again in one second.
        self.window.after(500, self.read_queue)

    def clicked(self):
        try:
            with open("./oauth.txt", "r") as file:
                self.oauthToken = file.read()
        except FileNotFoundError:
            messagebox.showerror("OAuth Error", "OAuth Token file (oauth.txt) not found.")
            return

        while self.oauthToken.endswith("\n") or self.oauthToken.endswith("\r"):
            self.oauthToken = self.oauthToken[:-1]

        if self.oauthToken is None or self.oauthToken == '':
            messagebox.showerror("OAuth Error", "OAuth Token not found.")
            return

        serial_port = self.combo.get()
        self.combo.configure(state='disabled')

        self.txt.configure(state='normal')
        self.txt.insert(END, "Trying to connect " + serial_port)
        self.txt.configure(state='disabled')

        self.queue = queue.Queue()
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.connect_to_twitch_and_serial, args=(loop, self.queue, serial_port, self.oauthToken))
        t.daemon = True
        t.start()

        self.window.after(500, self.read_queue)

        self.button['state'] = DISABLED

    def main(self):
        self.combo['values'] = self.serial_ports()

        self.window.mainloop()


if __name__ == '__main__':
    twitchCraneUi = TwitchCraneUi()
    twitchCraneUi.main()
