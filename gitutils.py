
import git
#see https://github.com/gitpython-developers/GitPython

def getUser(u):
    "removes @bucknell.edu if present"
    if '@' in u:
        return u.split('@')[0]
    else:
        return u
    
def getStudent(line):
    x = line.split()    
    return (" ".join(x[:-1]), getUser(x[-1])) # tuple of (name, login)

# list of students comes from banner web course roster

import os
import pwd

#these are globals the get overridden in students()
course_name = None
course_path = None

def students(section = None):
    global course_name
    global course_path
    # get username in somewhat safe way
    # other users can add their student lists here
    if pwd.getpwuid(os.getuid()).pw_name in ['alan', 'amm042']:
            
        Lab_62_8am = """Yash    Bhutwala    ymb002
Courtney    Bolivar    clb057
Andrew    Caple    awc015
Stefano    Cobelli    sjc032
Haley    Derrod    hyd001
Dan Bee    Kim    dbk012
Matthew    McNally    mbm032
Kenneth    Rader    klr020
Elliot    Radsliff    efr004
JB    Ring    jbr024
Alexander    Searer    ams067
John    Simmons    jas124
Ryan    Stecher    rgs030
Elias    Strizower    ebs021
Sune    Swart    sms061
Keyi    Zhang    kz005"""
        
        Lab_60_10am = """Aleksandar    Antonov    ala021@bucknell.edu
Bobby    Athanasidy    rca014@bucknell.edu
Duncan    Botti    dmb060@bucknell.edu
Justin    Eyster    jde012@bucknell.edu
Zhengri    Fan    zf002@bucknell.edu
Alex    Godziela    aag005@bucknell.edu
Michael    Hammer    mph009@bucknell.edu
Jiayu    Huang    jh054@bucknell.edu
Henry    Kwan    hbk001@bucknell.edu
AC    Li    yl015@bucknell.edu
Ken    Li    kkdl001@bucknell.edu
Ravi    Lonberg    rl031@bucknell.edu
Joel    Mabey    jwm037@bucknell.edu
Terence    McHugh    tjm044@bucknell.edu
Matthew    Rogge    mdrr001@bucknell.edu
Colby    Rome    cdr013@bucknell.edu
Kenneth    Stephon    kjs026@bucknell.edu
Peter    Unrein    pvu001@bucknell.edu
Patrick    Wales    pmw011@bucknell.edu"""
        student_list_by_section = {62: Lab_62_8am,
                                   60: Lab_60_10am}
            
        if section and section in student_list_by_section:
            s = student_list_by_section[section]
        else:
            s = '\n'.join(student_list_by_section.values())
        
        s = [getStudent(line) for line in s.splitlines()]
    
        course_name = "csci206"
        course_path = "/home/alan/Courses/csci206-S15-62"
    else:
        raise Exception("Define student list, course_name, course_pat here for your username and section")
    
    s.sort(key = lambda x: x[0].split()[1])
    return s



def main():
        
    debug = False
    checkin = True
    update = True
    
    complete = []
    
    for name, login in students():

        if login in complete:
            continue

        local_path = os.path.join(course_path, "{}_{}".format(login, course_name))
        remote_url = "git@gitlab.bucknell.edu:%s/%s.git"%(login, course_name)
        
        print ("-"*20+"BEGIN", name, login, local_path, remote_url,"-"*20)
        
        if not os.path.exists(local_path):
            if debug:
                print 'clone', name, '-->', local_path
            repo = git.Repo.clone_from(remote_url, local_path)
        else:        
            if debug:
                print 'pull existing repo', local_path
                            
            repo = git.Repo(local_path)
            if update:                
                repo.remotes.origin.fetch('--tags')
                repo.remotes.origin.pull('master')
                                    
                if debug:
                    print 'remotes:', repo.remotes
                    print 'branches:', repo.branches
        
        if debug:
            print 'tags:', repo.tags
            print 'heads:', repo.heads
            
        # you can search for a specific tag like this else it will use master
        #match = [tag for tag in repo.tags if ('ultra3' in tag.name and 'submit' ) ]
        match = None
        
        if not match:
            print '--> using master'
            checkout = repo.heads.master
        else:
            # if multiple matches, take the latest
            if len(match) > 1:
                match = [(x.commit.committed_date, x) for x in match]
                match.sort(key=lambda x: x[0])
                print len(match), 'submission found:', match
                checkout = match[-1][1]           
            else:        
                checkout = match[0]
            
            print 'checkout is:', checkout
                        
            repo.heads.master.checkout()
            
            if update:            
                # not sure this is necessary, but won't hurt
                repo.remotes.origin.pull(checkout.name)

        if checkin:
            # checkin grade.txt files
            if debug:
                print 'looking for files to checkin'
                
      
            for f in repo.untracked_files:
                #print 'untracked:', f
                if f.endswith('feedback.txt'):
                    print 'adding', f
                            
                    repo.index.add([f])
                    repo.index.commit("lab 2 graded")
                    repo.remotes.origin.push()
            if repo.is_dirty():
                repo.git.commit('-a', '-m "Lab 2 graded"')
                repo.git.push()
            else:
                print "--> skip push repo is clean"
                
        print ("-"*20+"END", name, login, "-"*20)

        
if __name__ == "__main__":
    main()