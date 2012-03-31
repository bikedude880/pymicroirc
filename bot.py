import connection


class IrcBot(object):
    """Default bot implementation. 

    You're supposed to subclass this and add your own logic to it. This means overriding methods
    like X{end_of_motd}, X{handle_chan_msg}, etc. Pass a folder name to place logs in to log, and 
    a debug level to debug. 0 means no printing, 1 means printing SOME debug messages, 2 means
    printing MORE debug messages, 3 means printing ALL the messages. Recommended use is 1 or 0.

    Preferably, use X{send_chan_line} and X{send_priv_line} to communicate with the server, along
    with the other specialised methods, and not X{send_raw_line}.
    """

    def __init__(self, host, port, user, realname, nick, log=None, debug=1):
        self.host = host
        self.port = port
        self.user = user
        self.realname = realname
        self.nick = nick
        self.log = log
        self.debug = debug
        self.quitting = False
        self.init()

    def init(self):
        self.connection = connection.IrcConnection(self.host, self.port, self.log)
        if self.log and self.debug:
            print "Connection established."
        self.send_init()
        return self.handle_input()

    def send_raw_line(self, line):
        self.connection.send_line(line)

    def send_chan_line(self, channel, line):
        self.send_raw_line("PRIVMSG "+channel.strip()+" :"+line)

    def send_priv_line(self, target, line):
        self.send_raw_line("PRIVMSG "+target.strip()+" :"+line)
        # yes, I know it's the same
    
    def part_channel(self, channel, reason="No reason given."):
        self.send_raw_line("PART "+channel+" :"+reason)

    def set_self_mode(self, flags):
        self.send_raw_line("MODE "+self.nick+" :"+flags)

    def set_chan_mode(self, channel, flags):
        self.send_raw_line("MODE "+channel+" :"+flags)

    def quit(self, reason="No reason given."):
        self.quitting = True
        self.send_raw_line("QUIT :"+reason)
        self.connection.close()

    def send_init(self):
        self.change_nick(self.nick)
        self.send_raw_line('USER '+self.nick+' '+self.user+' '+self.user+' :'+self.realname)
    
    def change_nick(self, new_nick):
        self.nick = new_nick
        self.send_raw_line('NICK '+self.nick)
    
    def join_channel(self, channel):
        self.send_raw_line('JOIN '+channel)
    
    def handle_input(self):
        lines = self.connection.receive_lines()
        if lines != "":
            for line in lines:
                self.handle_raw_line(line)
            return 0
        else:
            return 1
        
    def handle_raw_line(self, line):
        if self.log:
            self.debug_log(line)
        if self.debug>2:
            print(line)
        if line.startswith("PING"):
            self.send_raw_line("PONG "+line.replace("PING ",""))
        elif line.startswith(":"):
            #we assume command is the bits between colons, if there are at least two, else whole line
            command = line[1:]
            if line.count(":")>1:
                command = line[1:].split(":",1)[0]

            if " PRIVMSG " in command:
                #it's a privmsg          
                tmp, target = command.split(" PRIVMSG ",1)
                nick, host = tmp.split("!",1)
                message = line[1:].split(":",1)[1]
                if self.nick not in target:
                    self.handle_chan_msg(nick, host, target, message)
                else:
                    self.handle_priv_msg(nick, host, message)
            elif " JOIN " in command:
                #it's a join notification
                tmp, channel = line.split(" JOIN ",1)
                nick, host = tmp.split("!",1)
                channel = "#" + channel.split("#",1)[1] #fix for missing join :'s in some ircds
                self.handle_join(nick, host, channel)
            elif " PART " in command:
                #it's a part notification
                tmp, channel = line.split(" PART ",1)
                nick, host = tmp.split("!",1)
                channel = "#" + channel.split("#",1)[1] #fix for missing part :'s in some ircds
            elif " MODE " in command:
                #it's a mode change
                origin, target = command.split(" MODE ",1)
                if self.nick in origin and self.nick in target:
                    flags = line[1:].split(":",1)[1]
                    op = "+"
                    for flag in flags:
                        if flag == " ":
                            break
                        elif flag in ("+", "-"):
                            op = flag
                        else:
                            self.handle_self_mode(op + flag)
                else:
                    nick, host = origin.split("!", 1)
                    chan, flags = target.split(" ",1)
                    flags = flags.replace(":","").strip()
                    op = None
                    for flag in flags:
                        if flag == " ":
                            break
                        elif flag in ("+","-"):
                            op = flag
                        else:
                            self.handle_chan_mode(nick, host, chan, op + flag)
        if line.count("End of /MOTD"):
            self.end_of_motd()

    def handle_chan_msg(self, nick, host, channel, msg):
        channel = channel.strip()
        if self.debug:
            print("Got channel message: <"+nick+channel+"> "+msg)

    def handle_priv_msg(self, nick, host, msg):
        if self.debug:
            print("Got private message: <"+nick+"@"+host+"> "+msg)

    def handle_join(self, nick, host, channel):
        if self.debug:
            print(nick +" joined "+channel+".")
    
    def handle_part(self, nick, host, channel):
        if self.debug:
            print(nick +" has left "+channel+".")

    def handle_self_mode(self, mode):
        if self.debug:
            print("Set mode on self: "+mode)
    
    def handle_chan_mode(self, nick, host, channel, mode):
        channel = channel.strip()
        if self.debug:
            print("Set mode on channel "+channel+": "+mode)
    
    def end_of_motd(self):
        self.set_self_mode("+B")

    def debug_log(self, line):
        self.connection.debug_log(line)
    
    def update(self):
        err = self.handle_input()
        while err and not quitting:
            if self.log:
                self.connection.error_log("Disconnected from server. Reconnecting.. ")
            time.sleep(5)
            err = self.init()
