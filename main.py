#!/usr/bin/env python
import bot
import time

CHANNELS = ("#bots", )
GITHUB = "http://github.com/RedMike/pymicroirc"

class Bot(bot.IrcBot):
        
    def end_of_motd(self):
        super(Bot,self).end_of_motd()
        for chan in CHANNELS:
            self.join_channel(chan)

    def handle_priv_msg(self, nick, host, msg):
        super(Bot,self).handle_priv_msg(nick, host, msg)
        auth = self.get_auth(nick, host, None)
        if msg.startswith("join") and auth == 2:
            chan = msg.split(" ",1)[1]
            self.join_channel(chan)

    def handle_chan_msg(self, nick, host, chan, msg):
        super(Bot,self).handle_chan_msg(nick, host, chan, msg)
        #first, test for some basic commands.
        if msg.startswith("."):
            #it's a command, let's pass the call down the line.
            self.handle_command(nick, host, chan, msg[1:])
        else:
            #it's not a command, it's just chatter.
            pass

#  from here on are methods only for this subclass

    def handle_command(self, nick, host, chan, cmd):
        #we just got a bot command. 
        auth = self.get_auth(nick, host, chan)
        if cmd.startswith("quit") and auth == 2:
            if " " in cmd:
                self.quit(cmd.split(" ",1)[1])
            else:
                self.quit()
        elif cmd.startswith("part") and auth:
            self.part_channel(chan)
        elif cmd.startswith("docs"):
            line  = "My github page is available at: "+GITHUB
            self.send_priv_line(nick, line)
    
    def get_auth(self, nick, host, chan):
        """Returns a level of authentication for the nick, depending on the nick,
        the host, and the channel it's about. This allows per-channel auths."""
        if nick == "mike" and "ssnet.ro" in host:  #for debugging, mostly.
            return 2  # Global authentication for author.
        else:
            return 0  # No admin capabilities, only standard permissions.

    
b = Bot("irc.foonetic.net", 6667, "Bot", "Real Bot", "Sample_Bot", "logs")

while not b.quitting:
    b.update()
