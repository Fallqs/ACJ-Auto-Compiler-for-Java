import multiprocessing
import os
import re
import sys
import subprocess
import signal
import datacreater as data
from tqdm import tqdm
import time

import judger

timeout = 2
need_cpl = True
jarcmd = "java -cp .;.\\lib\\U4T1.jar;" #reliance
# "^[^/*]+public static void main"
mc = ["grep -r -t .java \"^\\s+public\\s+static\\s+void\\s+main\"  -d '", r"' -w 'main_class.txt' >ignore.txt"]
sf = [r"grep -r -k .java -d '", r"' -w 'src.txt' >ignore.txt"]
cf = [r"grep -r -k .class -d '", r"' -w 'cls.txt' >ignore.txt"]
# MainClass & SourceFiles & .classFiles
cpl = "javac @src.txt -encoding UTF-8 -Djava.ext.dirs=./lib -d "  # +" >ignore.txt"

gt, en, lg, out = [], [], [], []


def ansdir(pth):
    pth = pth.split(".\\submits")[1]
    os.system("mkdir subouts" + pth + " >ignore.txt 2>&1")
    # os.system("echo.>>src.txt")
    # os.system("echo -d subruntimes" + pth + " >>src.txt")
    # os.system("type src.txt")


def clsdir(pth):
    pth = "class" + pth.split(".\\submits")[1]
    os.system("mkdir " + pth + " >ignore.txt 2>&1")
    return pth


def pkg(mcs):
    gate, entry = None, None
    os.system(mcs)
    with open("main_class.txt", "r", encoding='utf-8')as f:
        s = f.readline().split()
        gate = s[0]
    with open(gate, "r", encoding='utf-8')as f:
        s = f.readlines()
        for l in s:
            mt = re.match(r'package\s+(\S+);', l)
            if mt is None: continue
            entry = mt.group(1)
            if entry is not None: return gate, entry
    return gate, entry


def wk(mcs, sfs):
    gate, entry = pkg(mcs)
    print(entry, end=",")
    sec = [r'([\S]+)(', r'\\', r')([\S]+).java']
    if entry is not None: sec[1] = '\\\\' + entry + '\\\\'

    mtch = re.match(sec[0] + sec[1] + sec[2], gate)

    if mtch is None:
        sec[1] = r'\\'
        mtch = re.match(sec[0] + sec[1] + sec[2], gate)

    gate = mtch.group(1)

    global cpl
    os.system(sfs)
    # redir(gate)
    print("collected", end=",")
    gate = clsdir(gate)
    os.system(cpl + gate)
    print("compiled")

    if entry is not None:
        entry = entry + '.' + mtch.group(3)
    else:
        entry = mtch.group(3)

    return gate, entry


def hack(gate, entry, outp, j):
    # print(">>>>>hacking", gate, entry, j, "<<<<<<<<")
    cin = " < stdin\\stdin_" + str(j) + ".txt"
    # print(cin)
    cout = " >" + outp + "\\stdout_" + str(j) + ".txt"
    # print(cout)
    cmd = jarcmd + gate + " " + entry + cin + cout
    # print(cmd)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         universal_newlines=True, shell=True, close_fds=True)

    try:
        rtv = p.wait(timeout)
        if rtv != 0:
            os.kill(p.pid, signal.SIGINT)
            print("RE: " + gate + "@" + str(j))
    except subprocess.TimeoutExpired:
        os.kill(p.pid, signal.SIGINT)
        # p.send_signal(signal.CTRL_BREAK_EVENT)
        print("TLE @" + str(j))

    print(end='.')
    if j % 100 == 99: print()
    # tq.update(1)


def Cpl():
    global mc, sf, gt, en
    os.system("dir .\\submits /a:d /B >submits.txt")
    gt, en = [], []
    with open("submits.txt", "r")as f:
        s = f.readlines()
        for l in s:
            opath = ".\\subouts\\" + l.strip()
            os.system("mkdir " + opath + " 1,2>ignore.txt")
            out.append(opath)
            path = ".\\submits\\" + l.strip()
            print(path)
            g, e = wk(mc[0] + path + mc[1], sf[0] + path + sf[1])
            # print(jarcmd + g + " " + e)
            # os.system(jarcmd + g + " " + e)
            gt.append(g)
            en.append(e)
    with open("pth.txt", "w")as f:
        for i in range(len(gt)):
            f.write(gt[i] + " " + en[i] + " " + out[i] + "\n")


def rd():
    global gt, en, out
    gt, en, out = [], [], []
    with open("pth.txt", "r")as f:
        s = f.readlines()
        for i in range(len(s)):
            # if i == 2: continue
            l = s[i]
            l = l.split()
            gt.append(l[0])
            en.append(l[1])
            out.append(l[2])


def run(l, r):
    global gt, en, out
    for i in range(len(gt)):
        starttime = time.time()
        p = multiprocessing.Pool(3)
        print("on %s: [%d,%d)" % (gt[i], l, r))
        # tq = tqdm(total=r - l)
        for j in range(l, r):
            p.apply_async(hack, args=(gt[i], en[i], out[i], j))
            # if j % 8 == 7: time.sleep(3)
            # hack(gt[i], en[i], out[i], j)
        p.close()
        p.join()
        endtime = time.time()
        print(endtime - starttime)
        print()


if __name__ == '__main__':
    # need_cpl = False  # [是否需要重新解包编译], 默认True, 这里设置为 False
    if need_cpl and (len(sys.argv) == 1 or sys.argv[1] == '-c'):
        Cpl()
    else:
        rd()

    l, r = 0, 200
    while True:
        data.data(l, r)
        run(l, r)
        judger.judge(l, r, out)
        r, l = r + 200, r
