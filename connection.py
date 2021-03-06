import socket
import datetime
import os
import sys

class IrcConnection(object):

    def __init__(self, host, port, log_folder=None):
        self.log = log_folder
        self.init_logs()
        self.host, self.port = host, port
        self.socket = None
        self.buffer = ""
        self.init_connection()
        if not self.socket:
            if self.log:
                self.error_log("Connection failed to initialise.")
                sys.exit(1)

    def init_logs(self):
        if self.log:
            if not os.path.exists(self.log):
                print "Log folder does not exist or is not accessible!"
                sys.exit(1)
                
    def init_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)

    def send_line(self, line):
        self.socket.sendall(line+"\r\n")

    def receive_lines(self):
        lines = []
        if self.buffer != "":
            lines = [ self.buffer ]
        try:
            while(1):
                buffer = self.socket.recv(4096)
                if buffer[-1:] == '\n':
                    lines += buffer.replace("\r","").split("\n")
                    self.buffer = ""
                else:
                    lines += buffer.replace("\r","").split("\n")[:-1]
                    self.buffer = buffer.replace("\r","").split("\n")[-1:][0]
        except socket.error as e:
            pass #dammit, I do need to fix this, don't I? Also messages getting cut off.
        return lines
    
    def get_timestamp(self):
        ret = "["
        ret += datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
        ret += "] "
        return ret

    def debug_log(self, line):
        with open(self.log+"/debug.log", "a+") as f:
            f.write(self.get_timestamp()+line+"\n")

    def error_log(self, line):
        with open(self.log+"/error.log", "a+") as f:
            f.write(self.get_timestamp()+line+"\n")
    
    def close(self):
        self.socket.close()
