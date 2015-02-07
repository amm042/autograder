import gradeutils
import subprocess

import shlex
import os.path

required_files= ['brtrace.out',
                 'brtrace.cpp']
folder_name = 'pin_branch'


student_info = {
            ## Git path: ( PATH, EXEC CMD, EXEC args, Source files)
             'clr023_csci320': ('pin_branch', 'java', 'Predict', '*.java'),
             'dag027_csci320': ('pin_branch', './predict', '', 'predict-compete'),
             'ls052_csci320': ('predictor', 'java', 'Predict', '*.java README.txt'),
             'jrh056_csci320': ('pin_branch/pin_branch_predict/src', 'java', 'predict', '*.java'),
             'aet006_csci320': ('pin_branch_final', 'java', 'Predict', '*.java'),
             'srw011_csci320': ('pin_branch', 'predict', '', 'predict.c' ),
             'ead020_csci320': ('BranchPrediction/src', 'java', 'predict', '*.java'),
             'lrb013_csci320': ('pin_branch', 'python3', 'predict.py', 'predicty.py'),
             'tft003_csci320': ('pin_branch', 'predict', '', 'predict.c'),
             'dae013_csci320': ('pin_branch', 'python3', 'predict.py', 'predict.py'),
             'mja024_csci320': ('pin_branch', 'java', 'Predict', '*.java'),
             'bamj001_csci320': ('pin_branch/predictor/src', 'java', 'Predict', '*.java'),
             'pek008_csci320': ('pin_branch/Predictor/src', 'java', 'Predictor', '*.java'),
             'dem030_csci320': ('pin_branch', 'predict', '', '*.cpp')
             }
tests = [         
         ## parameter, outfile, (result tuple), points for correct
         ('static', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test1.out', (48022, 45788, 93810), 12.5),
         ('local 4', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test1.out', (83847, 9963, 93810), 12.5),
         ('two_level 8 2 4', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test1.out', (83987, 9823, 93810), 10),
                           
         ('static', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test2.out', (21367, 20742, 42109), 12.5),
         ('local 16', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test2.out', (36906, 5203, 42109), 12.5),
         ('two_level 8 2 4', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test2.out', (36306, 5803, 42109), 10),
         ('two_level 16 4 128', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test2.out', (32053, 10056, 42109), 10),
         
         ('compete 32', '/home/alan/Courses/csci320-F13/amm042_csci320/pin_branch/test2.out', (35000,0,0), 20)
         ]
         
         

def check(path, folder, feedback_file):
    
    prj_path = os.path.join(path, folder)

    p = prj_path.split('/')
    if p[5] in student_info:
        prj_path = '/home/alan/Courses/csci320-F13/' + p[5] + '/' + student_info[p[5]][0]

    if os.path.exists(os.path.join(prj_path, feedback_file)):
        print "Skipping", prj_path, "the file", feedback_file, "already exists."
        return
    
    
    if not os.path.exists(prj_path):
        print prj_path, "MISSING"
        return
        
            
    git_folder = os.path.split(path)[1]
    if git_folder in student_info:
        
        print "-"*60
        print "Grading", git_folder, 'in', prj_path
        
        feedback = []
        total = 0
        for test in tests:
            
            if git_folder == 'dae013_csci320' and test[0].startswith('compete'):
                test = (test[0].replace('compete', 'tournament'),) +  test[1:]
                
            cmd = " ".join([student_info[git_folder][1],
                            student_info[git_folder][2],
                            test[0], 
                            test[1]])
            
            s = "  running: " + " ".join([student_info[git_folder][2],
                                          test[0], 
                                          os.path.split(test[1])[-1]])
            try:
                print cmd
                sp = subprocess.check_output(shlex.split(cmd), cwd = prj_path, env = {}, 
                                             stderr = subprocess.STDOUT).strip()
                lines = sp.splitlines()
                
                if git_folder == 'ead020_csci320' and test[0].startswith('compete'): 
                    result = tuple([int(i) for i in lines[-1].split()[1:4]])
                else:
                    if len(lines)> 0:
                        result = tuple([int(i) for i in lines[-1].split()])
                    else:
                        result = (0,0,0)
                #print miss, correct, total
                
                if test[0].startswith('compete') or test[0].startswith("tournament"):
                    if result[0] > test[2][0]:
                        s += " -> Passed {}/{} points for you".format(test[3], test[3])
                        total += test[3] 
                    else:
                        s += " -> Poor result: got " + str(result) + " wanted at least " + str(test[2]) + \
                                " correct, giving you {}/{} points".format(test[3]/2.0, test[3])
                        total += test[3]/2.0
                else:
                    if result == test[2]:
                        s += " -> Passed {}/{} points for you".format(test[3], test[3])
                        total += test[3] 
                    else:
                        print "  running: ", " ".join([student_info[git_folder][2],
                                                       test[0], 
                                                       os.path.split(test[1])[-1]]),\
                                          " -> Failed: got " + str(result) + " wanted "+  str(test[2])
                        score = raw_input("enter grade [{}/{}]:".format(test[3]/2.0, test[3]))
                        
                        if score == "":
                            score = test[3]/2.0            
                        else:                            
                            score = float(score)
                                                                                    
                        s += " -> Failed: got " + str(result) + " wanted "+  str(test[2]) + \
                                " giving you {}/{} points".format(score, test[3])
                        total += score            
                feedback.append(s)
            except ValueError:
                # failed to parse output
                print "  running: ", " ".join([student_info[git_folder][2],
                                               test[0], 
                                               os.path.split(test[1])[-1]]),\
                                  " -> Failed: got " + sp
                score = raw_input("enter grade [{}/{}]:".format(test[3]/2.0, test[3]))
                
                if score == "":
                    score = test[3]/2.0            
                else:                            
                    score = float(score)
                                                                            
                s += " -> Failed: got " + sp + " wanted "+  str(test[2]) + \
                        " giving you {}/{} points".format(score, test[3])
                feedback.append(s)              
                total += score        
            except subprocess.CalledProcessError, cpe:
                s += " -> Failed\n"
                
                
                print "  running: ", " ".join([student_info[git_folder][2],
                                               test[0], 
                                               os.path.split(test[1])[-1]]),\
                                  " -> Failed: got " + cpe.output
                score = raw_input("enter grade [{}/{}]:".format(test[3]/2.0, test[3]))
                
                if score == "":
                    score = test[3]/2.0            
                else:                            
                    score = float(score)
                                                                            
                #s += " -> Failed: got " + sp + " wanted "+  str(test[2]) + \
                #        " giving you {}/{} points".format(score, test[3])
                       
                total += score        
                                
                feedback.append(s)
                feedback.append( "error:"+ cpe.output)
                feedback.append( "{}/{} points".format(score, test[3]))
        
        feedback.append("Total Score: {}/{}\n".format(int(total), 100))
        
        
        print "\n".join(feedback)
        
        with open(os.path.join(prj_path, feedback_file), 'w') as outf:
            outf.write("\n".join(feedback))
            outf.close()  
            
        exit()
    
    
if __name__ =="__main__":
    import sys    
    import grader
    