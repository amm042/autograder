import zmq
import time
import sys
import logging
import threading
import bson
import os
import hashlib
from md5file import hashfile
import datetime
import subprocess
import shlex

class Server(threading.Thread):
    def __init__(self, port=5556, chunksize = 64*1024, 
                 uploaddir='./uploads/',
                 rubricsdir = './rubrics/'):
        threading.Thread.__init__(self)
        
        logging.info("server init")
        
        self.rpipe, self.wpipe = os.pipe()
        
        self.chunksize = chunksize
        self.portstr = "tcp://*:%d" % port
        self.context = zmq.Context()
        self.uploaddir = uploaddir
        self.rubricsdir = rubricsdir
        
        self.sessions = {} # active sessions
        self.transfers = {}  # active file transfers
        self.transno = 1        
        self.handlers = {'fileupload': self.fileuploadHandler,
                         'chunk': self.chunkHandler,
                         'error': self.errorHandler,
                         'beginsession': self.beginsessionHandler,
                         'gradefile': self.gradefileHandler,
                         'checkresult': self.checkresultHandler,
                         }
    def gradefileHandler(self, message):
        logging.debug("begin grading file {} for session {}".format(message['filename'],
                                                                    message['sessionid']))
        s = self.sessions[message['sessionid']]
        username = s['user'][0]
        pathloc = os.path.join(self.uploaddir, 
                               self.sessions[message['sessionid']]['user'][0],
                               message['sessionid'])
        fileloc = os.path.join(pathloc,
                               message['filename'])
        rubric = os.path.join(self.rubricsdir,
                              s['activity'],
                              'grade.py')
        if not os.path.exists(fileloc):
            return {"status": "fail",
                    "message": "file not found ({}) for session {}".format(message['filename'],
                                                                           message['sessionid'])}            
            
#        with open(stubloc, 'w') as f:
##           f.write ("""#grading stub
##import rubrics.{}.grade as g
#g.grade_file('{}')
#""".format(s['activity'], fileloc))
        
        #escape spaces in filename for shell
        #stubloc = stubloc.replace(' ', '\\ ')
        outputloc = os.path.join(pathloc, 'output.log').replace(" ", "\\ ")
        cmd = 'python3 {} > {} 2>&1'.format(rubric, outputloc)
        
        logging.debug("executing subprocess: {}".format(cmd))
        p = subprocess.Popen(shlex.split(cmd), 
                             cwd=os.getcwd(),
                             stdin=None, stdout=None, stderr=None)
        
        s['process'] = p
        logging.debug("started subprocess: {}".format(p))
    
        return {"type": "result", "status": "success"}
        
    def checkresultHandler(self, message):
        logging.info("checkresult for {}".format(message))
    
        if message['sessionid'] not in self.sessions:
            return {"type":"error", "message": "session not found ({})".format(message['sesionid'])}
        if 'process' not in self.sessions[message['sessionid']]:
            return {"type":"error", "message": "grading process not found for session {}".format(message['sesionid'])}            
        proc = self.sessions[message['sessionid']]['process']
        proc.poll()
        
        return {"type":"checkresult",
                "returncode": proc.returncode}
        
    def beginsessionHandler(self, message):
        logging.info("creating session for {}".format(message))
        
        #validate activity first
        actdir = os.path.join(self.rubricsdir, 
                              message['activity'],
                              'grade.py')
        
        if not os.path.exists(actdir):
            return {"status": "fail",
                    "message": "activity not found ({})".format(message['activity'])}
        sessionpath = os.path.join(self.uploaddir, message['user'][0])
        if not os.path.exists(sessionpath):
            os.mkdir(sessionpath)
            
        sessionid = str(datetime.datetime.utcnow())
        
        if os.path.exists(os.path.join(sessionpath, sessionid)):
            rsp = {'status': "fail",
                   'message': 'Session with that timestamp already exists, try again later.'}
        else:
            rsp = {'status' : 'success',
                   'sessionid': sessionid}
            self.sessions[sessionid] = message
        return rsp
        
        
    def errorHandler(self, message):
        logging.info("client sent error {}".format(message['message']))
        return {'type': "goodbye"}       
    
    def fileuploadHandler(self, message):
        
        if message['sessionid'] in self.sessions:
             # start a new file upload
            logging.info("starting new upload with transno {} for file {}".format(self.transno, 
                                                                                  message['filename']))
            #cache transfer info
            self.transfers[self.transno] = message
            rsp = {'type': 'sendchunk',
                   'transno': self.transno,
                   'pos': 0,
                   'size': self.chunksize}
            self.transfers[self.transno]['pos'] = 0
            
            self.transno += 1 # increment global counter for next transfer
        else:
            logging.info("file upload request with invalid session: {}".format(message['sessionid']))
            rsp = {'type':'error',
                   'message': 'invalid session id'}
        return rsp
    
    def chunkHandler(self, message):
        if message['transno'] not in self.transfers:
            logging.error("got chunk for invalid transfer")
            return {'type': 'error', 'message': 'invalid transno'}
            
        tr = self.transfers[message['transno']]
                
        logging.info("got chunk at {} ({}%) for transno {} of file {}".format(
                    message['pos'],
                    100 * float(message['pos']  + message['size']) / float(tr['filesize']),                                            
                    message['transno'], 
                    tr['filename']))
        
        if tr['pos'] == message['pos']:
            #todo: change upload path to uploaddir/username/session name
            fileloc = os.path.join(self.uploaddir, 
                                   self.sessions[message['sessionid']]['user'][0],
                                   message['sessionid'],
                                   tr['filename'])
            if os.path.exists(fileloc):
                fmode = 'rb+'
            else:
                os.mkdir(os.path.split(fileloc)[0])
                fmode = 'wb+'
            with open(fileloc, fmode) as f:
                f.seek(message['pos'])
                f.write(message['data'])
            tr['pos'] += message['size']
            
            if tr['pos'] == tr['filesize']:
                # check md5
                md5 = hashfile(open(fileloc, 'rb'), hashlib.md5())                
                
                logging.info("  this is the last block, sending transfercomplete")
                rsp = {'type': 'transfercomplete',
                       'transno': message['transno'],
                       'status': {True:'success',
                                  False: 'fail'}[md5==tr['md5']]
                        }
            else:
                rsp = {'type': 'sendchunk',
                       'transno': message['transno'],
                       'pos': tr['pos'],
                       'size': self.chunksize}
        else:
            logging.warn("  chunk at wrong pos, got {} expected {}".format(message['pos'], 
                                                                          tr['pos']))
            rsp = {"type": 'error',
                   'message': 'position missmatch'}
        return rsp
    
    def run(self):
        socket = self.context.socket(zmq.REP)
        
        socket.bind(self.portstr)
        logging.info ("Running server on port: {}".format(self.portstr) )
        
        p = zmq.Poller()
        p.register(socket)
        p.register(self.rpipe)
        quit = False
        while not quit:
            
            rdy = p.poll()
            
            for e in rdy:                
                if e[0] == socket:
                    # Wait for next request from client
                    message = bson.BSON.decode(socket.recv(zmq.NOBLOCK))
                    logging.debug ("Received message: {}".format(message))
                    
                    if message['type'] in self.handlers:
                        rsp = self.handlers[message['type']](message)
                    else:
                        rsp = {'type': 'error',
                               'message': 'no handler for {}'.format(message['type'])}
                    
                    if rsp:
                        logging.debug( "  sending{}".format(rsp))  
                        socket.send(bson.BSON.encode(rsp))
                elif e[0] == self.rpipe:
                    # read at most 16K from the pipe, could the message ever be larger?
                    msg = bson.BSON.decode(os.read(self.rpipe, 16*1024))
                    logging.info ("server got shutdown request ({}), goodbye.".format(msg))
                    quit = True
          
    def stop(self):
        os.write(self.wpipe, bson.BSON.encode({"type": "quit"}))
        self.join(5)
        
def run():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logging.info('starting server')
    
    try:
        s = Server()
        s.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('shutting down') 
        s.stop()
    
if __name__=="__main__":
    run()