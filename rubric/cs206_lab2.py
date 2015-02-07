import os.path
import gradeutils
import re
import tempfile
import shutil
"""
grading comments from Spring 2015

prelab cannot be compiled, the signature of snode_create has changed and they
overwrite their old file that matches snode-test2.c : snode_create(str, length)


snode-test2.c (prelab)
0 points if missing
-2 if they did it but got the wrong order

enter score for following good coding conventions:
5 = has name and a few comments and code looks OK
4 = missing one item
3 = missing two things (no name  or comments)
        no useful comments or name in music1/music2


music1/music2 output:
-5  close but minor errors had both add_front and add_back
-10 major flaws but ran, eg missing one of add_front or add_back
-15 failed to run (eg seg fault), but did have evidence of some work
-20 failed to compile, but had evidence of work


"""

folder_name = 'Labs/Lab2'
required_files = ['snode-test2.c',
                  'snode.c',
                  'snode.h',
                  'slist.c',
                  'slist.h',
                  'music1.c',
                  'music2.c',
                  'Makefile']

    
def check(path, folder, feedback_file):

    prj_path = os.path.join(path, folder)

    outpath = prj_path

    if os.path.exists(os.path.join(prj_path, feedback_file)):
        print "Skipping", path, "the file", feedback_file, "already exists."
        return

    # bug fix where i drop the output file in Lab2/Lab2 if the user has this.
    if os.path.exists(os.path.join(prj_path, 'Lab2', feedback_file)):
        print "copy feedback from Lab2/Lab2 to Lab2"
        shutil.copy(os.path.join(prj_path, 'Lab2', feedback_file),
                    os.path.join(prj_path, feedback_file))
        return
        
        
    total = 0
    out = []
    
    print("*"*50)
    
    print ("grading {}".format(prj_path))
    
    

    
    # grade prelab first...    
    # have to use their snode.c/h from lab1, becuase the call signature changes in Lab2
        
    if os.path.exists(os.path.join(prj_path, 'snode-test2.c')):
        gradeutils.showfiles([os.path.join(prj_path, 'snode-test2.c')])
        try:
            workdir = tempfile.mkdtemp()
            print('using temp dir: {}'.format(workdir))
            shutil.copy(os.path.join(prj_path,'snode-test2.c'), 
                        os.path.join(workdir, 'snode-test2.c'))    
            shutil.copy(os.path.join(prj_path,'slist.h'), 
                        os.path.join(workdir, 'slist.h'))
            shutil.copy(os.path.join(prj_path,'../Lab1/snode.c'), 
                        os.path.join(workdir, 'snode.c'))
            shutil.copy(os.path.join(prj_path,'../Lab1/snode.h'), 
                        os.path.join(workdir, 'snode.h'))
            
            gradeutils.guard(os.path.join(workdir, 'snode.h'))
            rslt,outtxt = gradeutils.compile(workdir, 'gcc -w -std=c99 snode-test2.c snode.c -o snode-test2')
            if rslt != 0:
                print("Compilation failed for snode-test2.c")
                print(outtxt)
            else:
                print (outtxt)
                
            score, reason = gradeutils.gradeoutput("""Correct Output:
node 1: Ashes to Ashes - 14

node 1: Ashes to Ashes - 14
node 2: Uptown Funk - 11

node 1: Antics - 6
node 2: Ashes to Ashes - 14
node 3: Uptown Funk - 11""", workdir, './snode-test2', 25)
            
            out += ["{}/{}: (prelab) snod-test2.c: {}".format(score, 25, reason)]
            total += score
            
        finally:
            print('removing temp dir: {}'.format(workdir))
            shutil.rmtree(workdir)
    
    else:
        
        out += ['0/25: (prelab) snode-test2.c missing']
        print (out[-1])
    
    
    # many students put Lab2/Lab2
    if os.path.exists(os.path.join(prj_path, 'Lab2')):
        prj_path = os.path.join(prj_path, 'Lab2')
    
    
    print ("showing required files in {}".format(prj_path))
    gradeutils.showfiles([os.path.join(prj_path, p) for p in required_files
                          if os.path.exists(os.path.join(prj_path, p))])
    print ("enter score for following good coding conventions.")
    score, reason = gradeutils.readscore(5)
    out += ['{}/5: follows good coding conventions ({})'.format(score, reason)]
    total += score    
    
        
    if os.path.exists(os.path.join(prj_path, 'music1.c')):    
        rslt,outtxt = gradeutils.compile(prj_path, 'gcc -w -std=c99 music1.c snode.c slist.c -o music1 -lreadline')
        if rslt != 0:
            print("Compilation failed for music1.c")
            print(outtxt)
        else:
            print (outtxt)

            
        score, reason = gradeutils.gradeoutput("""output should be similar to:
song title: Song number one
song title: Song number Two is better
song title: 
node 0: Song number one - length: 15
node 1: Song number Two is better - length: 25

Testing add_front
song title: LAST .. . 
song title: middle song
song title: FIRST! ! 
song title: 
node 0: FIRST! !  - length: 9
node 1: middle song - length: 11
node 2: LAST .. .  - length: 10        
""", 
                                                prj_path,
                                                './music1', 35,
                                                input = """Song number one
Song number Two is better
\x04LAST .. . 
middle song
FIRST! ! 
\x04""")
        
        out += ["{}/{}: music1.c: {}".format(score, 35, reason)]
        total += score

    else:        
        out += ['0/25: music1.c missing']
        print (out[-1])  


    if os.path.exists(os.path.join(prj_path, 'music2.c')):    
        rslt,outtxt = gradeutils.compile(prj_path, 'gcc -w -std=c99 music2.c snode.c slist.c -o music2 -lreadline')
        if rslt != 0:
            print("Compilation failed for music2.c")
            print(outtxt)
        else:
            print (outtxt)

            
        score, reason = gradeutils.gradeoutput("""output should be similar to:
enter song title: One
enter song title: One
song title One is a dupe!!!
enter song title: One
song title One is a dupe!!!
enter song title: Two
enter song title: 
node 1: One - 3
node 2: Two - 3

Testing add_front...
enter song title: Last 
enter song title: middle
enter song title: middle
song title middle is a dupe!!!
enter song title: first 
enter song title: 
node 1: first  - 6
node 2: middle - 6
node 3: Last  - 5    
""", 
                                                prj_path,
                                                './music2', 35,
                                                input = """One
One
One
Two
\x04Last 
middle
middle
first 
\x04""")
        
        out += ["{}/{}: music2.c: {}".format(score, 35, reason)]
        total += score

    else:        
        out += ['0/35: music2.c missing']
        print (out[-1])  
    
    
    with open(os.path.join(outpath, feedback_file), 'w') as outf:
        outf.write("Feedback for lab2 (100 points)\n")
        outf.write("\n".join(out))
        outf.write("\n")
        outf.write("-"*30)
        outf.write("\n")
        outf.write("Total Score: {}/{}\n".format(total, 100))
        outf.close()