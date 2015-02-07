import os.path
import gradeutils
import re
"""
grading comments from Spring 2015

full deduction
no declaration of snode_create in snode.h.
Should be in Labs/Lab1 (you have it in just Lab1) see your TA/instructor for help on moving the files.

5 points
Did not set new_node->next = NULL in snode_create

2 points
Memory for str allocated with malloc, should be declared char str[100] in snode.h


 (no deduction)

Please put your name in all of your source files in the future.
"""

folder_name = 'Labs/Lab1'
required_files = ['prelab.txt',
                  'snode.c',
                  'snode.h',
                  'snode-test.c']
def correct(path, folder, feedback_file):
    # warning this will double correct if run multiple times
    fb_path = os.path.join(path, folder, feedback_file)
    
    if os.path.exists(fb_path):
        with open (fb_path, 'r') as f:
            old = f.read()
        
        lines = old.split('\n')
        new = []
        for l in lines:
            if l.startswith("----"):
                new += ['5/0: correction for prelab path']
                new += [l]
            elif l.startswith("Total Score"):
                ts = re.split(":|/", l)
                new += ["Total Score: {}/{}".format(
                            int(ts[1])+5,
                            ts[2])]
            else:
                new += [l]
        print (old)
        print ("="*40)
        print ("\n".join(new))
        
        with open(fb_path, 'w') as f:
            f.write("\n".join(new))
    
    
def check(path, folder, feedback_file):

    prj_path = os.path.join(path, folder)

    if os.path.exists(os.path.join(prj_path, feedback_file)):
        print "Skipping", path, "the file", feedback_file, "already exists."
        return

    print ("showing required files in {}".format(prj_path))
    gradeutils.showfiles([os.path.join(prj_path, p) for p in required_files
                          if os.path.exists(os.path.join(prj_path, p))])
    total = 0
    out = []
    for text, points in [("(prelab)one line mkdir -p ~csci206/Labs/Lab1", 5),
        ("(prelab)One sentence description of each of the following commands do: cat,  more,  less, head, and tail",5),
        ("(prelab)The complete command line to start up emacs without a GUI (emacs -nw)", 5),
        ("(prelab)Then complete this sentence in your file: After careful consideration, I will use <vim/gvim or emacs> in csci206 as my text editor.", 5),
        ("(prelab)Files submitted in the correct path (Labs/Lab1)", 5),
        ("snode.h has a working definition of struct snode", 20),
        ("snode.h has a correct declaration for snode_create", 10),
        ("snode.c has a correct snode_create that uses malloc and strcpy; deduct if it does not set length, str, or next", 25),
        ("Code follows good coding conventions", 20)]:


        v = False
        prompt = False
        while not v:

            try:
                score = raw_input("enter grade for {} [{}]:".format(text, points))
                reason = "Good"
                if score == "":
                    prompt = False
                    score = points
                else:
                    prompt = True
                    score = int(score)
                v = True
            except ValueError:
                print ("Enter a valid integer grade!")
                v = False

        if prompt:
            reason = raw_input("enter reason:")
        if len(reason) > 0:
            out.append("{}/{}: {} ({})".format(score, points, text, reason))
        else:
            out.append("{}/{}: {}".format(score, points, text))
        total += score

    with open(os.path.join(prj_path, feedback_file), 'w') as outf:
        outf.write("Feedback for lab1 (100 points)\n")
        outf.write("\n".join(out))
        outf.write("\n")
        outf.write("-"*30)
        outf.write("\n")
        outf.write("Total Score: {}/{}\n".format(total, 100))
        outf.close()