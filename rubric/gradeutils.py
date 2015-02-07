import os
import os.path
import shlex
import subprocess
import tempfile
import uuid

def count_files (files, paths):
    """look in each of paths and count how many of the given
    files exist, return list sorted by number of matches

    """
    counts = {}
    
    for p in paths:    
        counts[p] = sum([i in files for i in os.listdir(p)])

    result = counts.items()
    result.sort(key=lambda x:x[1], reverse=True)

    #print "count_file", files, paths
    #print "result:", result
    return result

def missingfiles(base_path, files):    
    return [f for f in files if not os.path.exists(os.path.join(base_path, f))]

def compile(base_path, cmd):
    p = subprocess.Popen(shlex.split(cmd), cwd=base_path,
                         stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out,err = p.communicate()
    
    return p.returncode, out+err
def guard(filepath):
    # add ifndef guard around a c header
    
    with open(filepath, 'r') as f:
        o = f.read()
        
    g = "DEF" + str(uuid.uuid1()).replace("-", "")
    with open(filepath, 'w') as f:
        f.write("#ifndef {}\n".format(g))
        f.write("#define {}\n".format(g))
        f.write(o)
        f.write("#endif /* {} */\n".format(g))
def readscore(points):
        score = raw_input("score output: [%d]:"%(points))
        if score == '':
            score = points
            return points, "good"  
        else:
            x = None
            while not x:
                reason = raw_input('enter reason:')
                try:
                    x = int(score)
                except ValueError:
                    print "Could not convert to integer score, try again"
                    x = None
                
            return int(score), reason
def gradeoutput(text, path, cmd, points, input = None):            
    
    out = None
    err = None
    try:
        
        p = subprocess.Popen(shlex.split(cmd), cwd=path,
                             stdin = subprocess.PIPE,
                             stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out,err = p.communicate(input)
    except OSError as x:
        print x
        
    #limit output if very long
    print("-"*60)
    print 'output from', cmd
    if out:
        print out[:4000]
    if err:
        print err[:4000]
    print("-"*60)
    #if p.returncode == 0:
    print text
    return readscore(points)
    #else:        
        #return 0, '%s did not run:'%(cmd)+out+err

def showfiles(files):
    subprocess.Popen(shlex.split("gedit --standalone {}".format(" ".join(files))), stderr=0, stdout=0)
def gradetext(text, filename, points):
    with open(filename, 'r') as f:
        txt = f.read()
        for line in txt.splitlines():
            #if len(line)> 0:
            print line
        f.close()

    
    print 'contents of', filename
    print text
    #subprocess.call(shlex.split("gedit {}".format(filename)))
    score = raw_input("score output: [%d]:"%(points))
    print 'got input', score
    if score == '':
        score = points
        return points, ""  
    else:
        reason = raw_input('enter reason:')
        return int(score), reason            
    
def gettotal(feedback_file):
    #Total Score: 20 of 120
    #Total Score: 50/60
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r') as f:
            for line in f:
                if "total score" in line.lower():
                    if 'of' in line.lower():
                        line = line.split()
                        return line[2], line[4]
                    elif '/' in line.lower():
                        line = line.split()[2].split('/')
                        return line[0], line[1]
    else:
        return "Missing", "file"
    return None, None