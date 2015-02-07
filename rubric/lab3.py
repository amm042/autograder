import os
import subprocess
import shlex
import gradeutils
import sys

def p1(p, text, points):
    missing = gradeutils.missingfiles(p, ['ultra_design.txt'])
    if len(missing) > 0:
        return 0, "%s is missing"%(missing)
    
    return gradeutils.gradetext(text, os.path.join(p, 'ultra_design.txt'), points)

def p2(p, text, points):
    missing = gradeutils.missingfiles(p, ['ultra2.v'])
    if len(missing) > 0:
        return 0, "%s is missing"%(missing)
    
    if os.path.exists('./ultra2'):
        os.remove('./ultra2')
    code, msg = gradeutils.compile(p, 'iverilog -o ultra2 %s'%(os.path.join(p, 'ultra2.v')))
    
    if code == 0:
        return gradeutils.gradeoutput(text, './ultra2', points)
    else:
        return 0, "ultra2.v failed to compile:"+ msg


def p3(p, text, points):
    missing = gradeutils.missingfiles(p, ['ultra_design.txt', 'ultra2_indirect.v'])
    if len(missing) > 0:
        return 0, "%s is missing"%(missing)
    
    return gradeutils.gradetext(text, os.path.join(p, 'ultra2_indirect.v'), 40)

def p4(p, text, points):
    missing = gradeutils.missingfiles(p, ['sign_test.v'])
    if len(missing) > 0:
        return 0, "%s is missing"%(missing)
    
    if os.path.exists('./sign_test'):
        os.remove('./sign_test')
    code, msg = gradeutils.compile(p, 'iverilog -o sign_test %s'%(os.path.join(p, 'sign_test.v')))
    
    if code == 0:
        return gradeutils.gradeoutput(text, './sign_test', points)
    else:
        return 0, "sign_test failed to compile:"+ msg

def p5(p, text, points):
    # check design file 
    return p1(p, text, points)

parts = [
         ("ultra2.v updated (16 bit ISA, 4 GP reg, 256 word memory), ultra_design.txt created to reflect design.", 40, p1),
         ("ultra2.v works, output looks good, explain what is happening.", 10, p2),
         ("Indirect load/store/jump, R0 always zero.", 40, p3),
         ("sign_test.v correctly modified.", 10, p4),
         ("immediate load and relative jump implemented and documented.", 20, p5)
         ]

def check(full_path, folder, feedback_file):
    #if not os.path.exists(p):
        #os.mkdir(p)
    search_path = [x for x in os.listdir(full_path) if x.lower() == folder.lower()]
    
    if search_path == []:
        full_path = os.path.join(full_path, folder)
        
        os.mkdir(full_path)
    else: 
        full_path = os.path.join(full_path,
                                 [x for x in os.listdir(full_path) if x.lower() == folder.lower()][0])
    
    feedback_file = os.path.join(full_path, feedback_file)
    if not os.path.exists(feedback_file):
        print 'begin grading to', feedback_file
        scores = [0]*len(parts)
        feedback = [""]*len(parts)
        for idx, data in enumerate(parts):
            text, total_points, f = data
            scores[idx], feedback[idx] = f(full_path, text, total_points)
        
        t = []
        t.append("-"*80)
        t.append('Total Score: ' + str(sum(scores)) + ' of ' + str(sum([p[1] for p in parts]))) 
        for idx, data in enumerate(parts):
            text, total_points, f = data
            t.append( text)
            if len(feedback[idx]) > 0:
                t.append( feedback[idx])
            t.append( 'score ' + str(scores[idx]) + ' of ' + str(total_points))
            t.append(os.linesep)
        t.append( "-"*80)
        with open(feedback_file, 'w') as outf:
            outf.write(os.linesep.join(t))
            outf.close()    
    else:
        print feedback_file, 'already exists'
    