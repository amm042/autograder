import zmq
import time
import sys
import logging
import bson
import platform
import pwd
import os
import os.path
from md5file import hashfile
import hashlib
import argparse

class Client():
    def __init__(self, activity, server = '127.0.0.1', port = 5556):
        self.remoteuri = "tcp://{}:{}".format(server, port)
        self.connected = False
        self.activity = activity
        self.context = zmq.Context()
        self.context.setsockopt(zmq.RCVTIMEO, 3 * 1000) # in milliseconds
        self.sessionid = None
        self.begin_session()
        
    def begin_session(self):
        logging.debug("Starting new session")
        self.connect()
        req = {"type": "beginsession",
               "host": platform.node(),
               "user": pwd.getpwuid(os.getuid()),
               "activity": self.activity,               
               }
        
        self.socket.send(bson.BSON.encode(req))
        response = bson.BSON.decode(self.socket.recv())
        
        if 'status' in response and response['status'] == 'success':
            self.sessionid = response['sessionid']
        elif 'message' in response:
            logging.info('Could not begin session: {}'.format(response['message']))
        
    def connect(self):
        if not self.connected:
            logging.info("Connecting to server at {}".format(self.remoteuri))                    
            self.socket = self.context.socket(zmq.REQ)            
            self.socket.connect (self.remoteuri)
            self.connected = True

    def grade_file(self, filename):
        req = {"type": "gradefile",
               "sessionid": self.sessionid,
               "filename": filename}
        
        logging.debug("sending grade request for {} on file {}".format(self.sessionid,
                                                                       filename))
        self.socket.send(bson.BSON.encode(req))
        message = bson.BSON.decode(self.socket.recv())
        if message['type'] == 'result':
            logging.debug("  grading started for {} on file {}".format(self.sessionid,
                                                                       filename))
            return True
        elif message['type'] == 'error':
            logging.error("server error: {}".format(message['message']))
        elif message['type'] == 'goodbye':
            logging.error("server rejected us with a goodbye message")
        return False
    def check_result(self):
        req = {'type': 'checkresult',
               'sessionid': self.sessionid}
        logging.debug("Checking status of {}".format(self.sessionid))
        self.socket.send(bson.BSON.encode(req))
        message = bson.BSON.decode(self.socket.recv())
        logging.debug("Result was {}".format(message))
        return message
        
    def send_file(self, pathfilename):
        self.connect()
        logging.info("sending file: {}".format(pathfilename))
        
        req = {"type": "fileupload",
               "sessionid": self.sessionid,
               "host": platform.node(),
               "user": pwd.getpwuid(os.getuid()),
               "filename": os.path.split(pathfilename)[-1],               
               "filesize": os.stat(pathfilename).st_size,
               "md5": hashfile(open(pathfilename, 'rb'), hashlib.md5())}        
        
        self.socket.send (bson.BSON.encode(req))
        
        done = False
        with open(pathfilename, 'rb') as fd:
            while not done:
                message = bson.BSON.decode(self.socket.recv())
                logging.debug( "Received reply: {}".format(message))
                
                if message['type'] == 'sendchunk':
                    # server requested a file chunk
                    if message['pos'] > req['filesize']:
                        rsp = {'type':'error',
                               'message': 'requested chunk past EOF'}
                    else:
                        if (fd.tell() != message['pos']): # go to the requested spot
                            logging.info( "  seeking in file from {} to {}".format(fd.tell(), message['pos']))
                            fd.seek(message['pos'])
                        data = fd.read(message['size'])
                        
                        logging.info("sending chunk at {} ({}%)".format(
                            message['pos'],
                            100 * float(message['pos'] + len(data)) / float(req['filesize'])))
                        if len(data) < message['size']:
                            logging.info( "  this is the last chunk")
                        
                        rsp = {'type': 'chunk',
                               'pos': message['pos'],
                               'sessionid': self.sessionid,
                               'transno': message['transno'],
                               'size': len(data),
                               'data': data
                               }
                elif message['type'] == 'transfercomplete':
                    logging.info( "  transfer complete status: {}".format(message['status']))
                    done = True
                    rsp = None
                elif message['type'] == 'error':
                    logging.error("server error: {}".format(message['message']))
                    done = True
                    rsp = None
                elif message['type'] == 'goodbye':
                    logging.error("server rejected us with a goodbye message")
                    done = True
                    rsp = None
                else:
                    rsp = {'type': 'error',
                           'message': 'unsupported message {}'.format(message['type'])
                           }
                if rsp:
                    logging.debug( "  sending{}".format(rsp))                
                    self.socket.send(bson.BSON.encode(rsp))
def run():
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logging.info('starting client')
    
    parser = argparse.ArgumentParser(description = "An automated grading utility.",
                                     epilog = "Bucknell University")
    parser.add_argument('-f', '--file', help = 'A single file to grade')
    parser.add_argument('-g', '--git', help = 'The git repo name to clone for grading')
    parser.add_argument('-b', '--branch', help = 'The branch in the git repo to checkout', 
                        default = 'master')
    parser.add_argument('-a', '--activity', 
                        help = 'The activity ID to grade against (provided by your instructor)',
                        required = True)
    parser.add_argument('-d', '--debug',
                        help = 'Debugging level: DEBUG, INFO, WARN, ERROR, CRITIAL',
                        default = 'WARN')
    args = parser.parse_args()
    
    levels =  ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
    assert args.debug in levels, "Debugging level not valid. Use one of: {}".format(levels)
    logging.getLogger().setLevel(args.debug)
    if not args.git and not args.file:
        logging.critical("Error, either -f FILE or -g GIT is required.")
        exit(1)
    try:
        c = Client(args.activity)
        
        if c.sessionid == None:
            logging.critical('Server was unable to start the session, check the activity ID.')
            exit(2)
        if args.git:
            logging.critical ("git grading not yet implemented.")
            exit(3)
            
        if args.file:
            c.send_file(args.file)
            
            if c.grade_file(args.file):
                count = 0
                maxtries = 3
                while count < maxtries:
                    rslt = c.check_result()
                    if rslt['returncode'] != None:
                        break
                    time.sleep(0.1)
                    count += 1
                if count >= maxtries:
                    logging.error("Timed out waiting for result ({})".format(c.sessionid))
                else:
                    logging.info("got returncode {}".format(rslt['returncode']))
            else:
                logging.error("Grade file request failed.")
    except KeyboardInterrupt:
        logging.info('shutting down') 
        
if __name__=="__main__":
    run()