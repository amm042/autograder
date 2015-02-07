import gitutils
import os
from rubric import gradeutils
#from rubric import lab3 as lab
#from rubric import pin_branch as lab
#from rubric import ultra3 as lab
#from rubric import cs206_lab1 as lab
from rubric import cs206_lab2 as lab
import pwd

if pwd.getpwuid(os.getuid()).pw_name in ['alan', 'amm042']:
    section = 62
else:
    #you can make this user specific to pull the correct users only
    section = None
    
def get_paths(root):
    """get all directories under root as a flat list"""

    r = []
    for dirpath, dirnames, filenames in os.walk(root):
        r += [os.path.join(dirpath, x) for x in dirnames]

    return r

# correct grades
if 0:
    for idx, data in enumerate(gitutils.students(section)):
        name, login = data

        local_path = os.path.join(gitutils.course_path, "%s_%s"%(login, gitutils.course_name))
        project_path = os.path.join(local_path, lab.folder_name)  
        
        if not os.path.exists(project_path):
            project_path, count = gradeutils.count_files(lab.required_files, 
                                                         get_paths(local_path))[0]          
        lab.correct(local_path,
                  project_path,
                  'feedback.txt')
# this does the grading
if 1:
    for idx, data in enumerate(gitutils.students(section)):
        name, login = data

        local_path = os.path.join(gitutils.course_path, "%s_%s"%(login, gitutils.course_name))

        project_path = os.path.join(local_path, lab.folder_name)  
        
        if not os.path.exists(project_path):
            project_path, count = gradeutils.count_files(lab.required_files, 
                                                         get_paths(local_path))[0]  

        lab.check(local_path,
                  project_path,
                  'feedback.txt')

# this prints the summary
if 1:
    print ('---summary---')
    for idx, data in enumerate(gitutils.students(section)):

        name, login = data

        local_path = os.path.join(gitutils.course_path, "%s_%s"%(login, gitutils.course_name))
        project_path = os.path.join(local_path, lab.folder_name)  
        
        if not os.path.exists(project_path):
            project_path, count = gradeutils.count_files(lab.required_files, 
                                                         get_paths(local_path))[0]         
                  
        score, total = gradeutils.gettotal(os.path.join(project_path, 'feedback.txt'))

        print "{:80s} {:30s} {:10s} score = {}/{}".format(project_path, name, login, score, total)
