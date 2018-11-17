#####################################################################
#
# oscbridge.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

# used to forward OSC messages from a localhost OSC client/server to a remote machine's 
# OSC client/server

from OSC import OSCServer, ThreadingOSCServer, OSCClient, OSCMessage
import time
import threading
import sys
from time import sleep
import traceback
import socket



# class that forwards messages from one OSC client to another OSC client
class OSCForwarder(threading.Thread):
   def __init__(self, from_ip, from_port, to_ip, to_port):
      super(OSCForwarder, self).__init__()

      # create the server to listen to messages arriving at from_ip
      self.server = OSCServer( (from_ip, from_port) )
      self.server.addMsgHandler( 'default', self.callback )

      # create the clieent to forward those message to to_ip
      self.client = OSCClient()
      self.client.connect( (to_ip, to_port) )

      print '%s:%d --> %s:%d' % (from_ip, from_port, to_ip, to_port)

      self.done_running = False

      # start the server listening for messages
      self.start()

   # close must be called before app termination or the app might hang
   def close(self):
      # this is a workaround of a bug in the OSC server
      # we have to stop the thread first, make sure it is done,
      # and only then call server.close()
      self.server.running = False

      while not self.done_running:
         time.sleep(.01)
      self.server.close()

   def run(self):
      #print "Worker thread entry point"
      self.server.serve_forever()
      self.done_running = True


   def callback(self, path, tags, args, source):
      #print 'got:', path, args, 'from:', source
      self.client.send( OSCMessage(path, args ) )



def start_bridge(remote_ip) :
   synapse_send_port = 12345
   synapse_listen_port = 12346
   bridge_listen_port = 12321

   my_ip = socket.gethostbyname(socket.gethostname())
   print 'My IP is:', my_ip

   #remote_ip = '172.18.98.73'

   from_synapse = OSCForwarder('localhost', synapse_send_port, remote_ip, synapse_send_port)
   to_synapse = OSCForwarder(my_ip, bridge_listen_port, 'localhost', synapse_listen_port)

   try:
      while(1):
         sleep(1)
   except:
      traceback.print_exc()

   print 'Shutting down servers...'      
   from_synapse.close()
   to_synapse.close()
   print 'Done'


def main():
   if len(sys.argv) == 1:
      print "This machine's IP is:", socket.gethostbyname(socket.gethostname())
      print "Obtain <remote_ip> from other machine"
      print "run: python oscbridge.py <remote_ip>"

   else:
      remote_ip = sys.argv[1]
      start_bridge(remote_ip)
main()
