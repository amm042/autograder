from flask import Flask, g, request, session
import flask
from config import Config
import logging
import json
import uuid

#from multiprocessing import Process

logging.basicConfig(format = '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)-100s',
                    level=logging.DEBUG)
app = Flask(__name__)

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
            millis = int(
                calendar.timegm(obj.timetuple()) * 1000 +
                obj.microsecond / 1000
            )
            return millis
    elif isinstance(obj, datetime.timedelta):
        return str(obj)
    
    
@app.route("/begin", methods=['POST'])
def beginSession():
    j = json.loads(request.data.decode("UTF-8"))
    logging.info("beginSession: {}".format(j))
    #logging.info("beginSession")
    #logging.info(str(request.data))
    
    uid = str(uuid.uuid1())
    
    # start a new subprocess, store the process object in the session
    
    session['uid'] = uid

    #logging.info(" bg se g: {}".format(g.))

    return json.dumps({"result":"ok"})
    
@app.route("/check", methods = ['POST'])
def check():
    j = json.loads(request.data.decode("UTF-8"))
    logging.info("check: {}".format(j))    

    logging.info("  session uid: {}".format(session['uid']))
    return json.dumps({'result': 'stuff'})
       
    
@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    
    app.config.from_object('config.Config')
    app.secret_key = b'\x0cc\xeco#\xe7p\xde\xed\rJ\xa1\x99\x19\xc2\xac\x1f\xc0N\xab\xa7\x95b\xf7'
    app.run(debug=True)