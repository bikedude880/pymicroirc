import bot
import time

CHANNELS = ("#pyendor", )
GITHUB = "<to be added.>"

class Bot(bot.IrcBot):
        
    def end_of_motd(self):
        for chan in CHANNELS:
            self.join_channel(chan)

    def handle_chan_msg(self, nick, host, chan, msg):
        if self.debug:
            print "Got channel message: "+chan+": <"+nick+"> "+msg
        #first, test for some basic commands.
        if msg.startswith("."):
            #it's a command, let's pass the call down the line.
            self.handle_command(nick, host, chan, msg[1:])
        else:
            #it's not a command, it's just chatter.
            pass

    def handle_self_mode(self, flag):
        if self.debug:
            print "Set: "+flag

    def handle_chan_mode(self, nick, host, chan, mode):
        if self.debug:
            print "Set on channel "+chan+": "+mode+" by "+nick

    def handle_command(self, nick, host, chan, cmd):
        #we just got a bot command. 
        auth = self.get_auth(nick, host, chan)
        if cmd.startswith("quit") and auth == 2:
            if " " in cmd:
                self.quit(cmd.split(" ",1)[1])
            else:
                self.quit()
        elif cmd.startswith("part") and auth:
            self.part(chan)
        elif cmd.startswith("docs"):
            lines = ( 
            "My github page is available at: "+GITHUB,
            )
            for line in lines:
                self.send_chan_line(chan, nick + ": "+line)
    
    def get_auth(self, nick, host, chan):
        """Returns a level of authentication for the nick, depending on the nick,
        the host, and the channel it's about. This allows per-channel auths."""
        if nick == "mike" and "ssnet.ro" in host:  #for debugging, mostly.
            return 2  # Global authentication for author.
        else:
            return 0  # No admin capabilities, only standard permissions.

    
b = Bot("irc.foonetic.net", 6667, "Bot", "Real Bot", "microphone", "logs")

while not b.quitting:
    b.update()
