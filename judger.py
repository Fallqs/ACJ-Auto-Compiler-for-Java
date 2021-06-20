import numpy as np
from tqdm import tqdm


def check(output1, output2):
    len1 = len(output1)
    len2 = len(output2)
    if len1 != len2:
        return False
    for i in range(len1):
        if output1[i].strip() != output2[i].strip():
            return False
    return True

def judge(l, r, out):
    print(l)
    print(r)
    print("ready for judge")
    forPrint = []
    if len(out) <= 1:
        print("to few individuals")
        return

    for datas in tqdm(np.arange(l,r)):
        outputs = []
        for o in out:
            with open(o + "\\stdout_" + str(datas) + ".txt", "rb")as f:
                outputs.append(f.readlines())
        personNum = len(out)
        cnt = 1
        result = []
        mem = []
        for i in range(personNum):
            output = outputs[i]
            if i == 0:
                result.append((cnt, output))
                mem.append(cnt)
                cnt += 1
            else:
                point = 0
                for j in range(len(result)):
                    (text, output1) = result[j]
                    if check(output, output1):
                        result.append((text, output))
                        mem.append(text)
                        point = 1
                        break
                if not point:
                    result.append((cnt, output))
                    mem.append(cnt)
                    cnt += 1
        if cnt != 2:
            forPrint.append((datas, mem))

    for (num, re) in forPrint:
        print(str(num) + "wrong:", end = '')
        for x in re:
            print(str(x) + " ", end = '')
        print()
    print("done !!!")
