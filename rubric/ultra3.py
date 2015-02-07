
import os.path
import gradeutils

folder_name = "ultra"


required_files = ['ultra3.v',
                  'ultra3_sub.txt',
                  'ultra3_mul.txt',
                  'ultra3_branch.txt',
                  'ultra3_cpi.txt']

def check (path, folder, feedback_file):
    out = []
    
    prj_path = os.path.join(path, folder)
    
    if os.path.exists(os.path.join(prj_path, feedback_file)):
        print ("Skipping", path, "the file", feedback_file, "already exists.")
        return
    if not os.path.exists(prj_path):
        print (prj_path, "MISSING")
        return
    else:
        print (prj_path, "found")
    
    print ("showing required files")
    gradeutils.showfiles([os.path.join(prj_path, p) for p in required_files 
                          if os.path.exists(os.path.join(prj_path, p))])

    total = 0
    for text, points in [("subtract implemented", 10),
                         ("multiply implemented", 20),
                         ("branch implemented", 20),
                         ("CPI and MIPS computed", 10)]:
        score = raw_input("enter grade for {} [{}]:".format(text, points))
        reason = "Good"
        if score == "":
            score = points            
        else:
            reason = raw_input("enter reason:")
            score = int(score)
        if len(reason) > 0:
            out.append("{}/{}: {} ({})".format(score, points, text, reason))
        else:
            out.append("{}/{}: {}".format(score, points, text))
        total += score
    
    with open(os.path.join(prj_path, feedback_file), 'w') as outf:
        outf.write("Feedback for Ultra3 lab (60 points)\n")
        outf.write("\n".join(out))
        outf.write("\n")
        outf.write("-"*30)
        outf.write("\n")
        outf.write("Total Score: {}/{}\n".format(total, 60))
        outf.close()
        
if __name__ =="__main__":
    import sys
    #print (sys.path)
    import grader
    