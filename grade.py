"""Client program for autograder-server
https://github.com/amm042/autograder/

Copyright (C) 2015 Alan Marchiori

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import logging
import argparse
import os
import pwd
import requests
import urllib.parse
import json

DEFAULT_SERVER_URL = 'http://localhost:5000'

def init():
    parser = argparse.ArgumentParser(description = "An automated grading client utility.",
                                     epilog = "Copyright (C) 2015 Alan Marchiori")
    parser.add_argument('-g', '--git', 
                        help = 'The git repo name to clone for grading')
    parser.add_argument('--CFLAGS', 
                        help = 'CFLAGS to pass to gcc',
                        default = None)
    parser.add_argument('--URL',
                         help = 'Server URL (default: {})'.format(DEFAULT_SERVER_URL),
                         default = DEFAULT_SERVER_URL)
    parser.add_argument('-b', '--branch', 
                        help = 'The branch in the git repo to checkout (default: master)', 
                        default = 'master')
    parser.add_argument('-u', '--uid', 
                        help = 'The user id to grade (default: the current logged in user)')
    parser.add_argument('-c', '--course',
                        help = 'The course name to grade (ex: -c csci206)',
                        required= True)
    parser.add_argument('-a', '--activity', 
                        help = 'The activity ID to grade against (ex: -a Lab1)',
                        required = True)
    parser.add_argument('-d', '--debug',
                        help = 'Debugging level: DEBUG, INFO, WARN, ERROR, CRITIAL',
                        default = 'INFO')
    args = parser.parse_args()
    levels =  ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
    assert args.debug in levels, "Debugging level not valid. Use one of: {}".format(levels)
    
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt = '%I:%M:%S %p')    
    logging.getLogger().setLevel(args.debug)
        
    if not args.uid:
        args.uid = pwd.getpwuid(os.getuid()).pw_name
    
    if not args.git:
        args.git = 'git@gitlab.bucknell.edu:{}/{}.git'.format(args.uid, args.course)
        logging.warning("Assuming git repo at: {}, use -g to override".format(args.git))
    return args

def post(session = None, URL=None, path=None, **kwargs):
    url = urllib.parse.urljoin(URL, path)    
    data = json.dumps(kwargs)
    
    logging.debug("{} at {}".format(path, url))
    logging.debug("  data --> {}".format(data))
    
    return json.loads(session.post(url, data).text)

def beginSession(URL=None, **kwargs):    
    s = requests.Session()
    
    r = post(s, URL=URL, path='begin', **kwargs)
    
    return s

def checkSession(session=None, URL=None, **kwargs):
    
    r = post(session, URL=URL, path='check')
    
    logging.info("status is: {}".format(r))
    
def run():
    args = init()
    
    logging.info("Hello {}".format(args.uid))
        
    try:
        s = beginSession(**vars(args))
                    
        for i in range(2):
            checkSession(session=s, URL=args.URL)
        
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to server, is it up?")
    
if __name__ == "__main__":        
    run()