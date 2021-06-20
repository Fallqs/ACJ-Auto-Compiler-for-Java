import os
# import creating.datacreater as dc
from tqdm import trange


def data(L, R):
    print("creating: [%d,%d)" % (L, R))
    for i in trange(L, R):
        os.system("gen >" + "stdin\\stdin_" + str(i) + ".txt")

    print()


if __name__ == '__main__':
    with open("datarnk.txt", "r")as f:
        L, R = [int(x) for x in f.readline().split()]
    print("creating: [%d,%d)" % (L, R))
    for j in trange(L, R):
        os.system("gen >" + "stdin\\stdin_" + str(j) + ".txt")

    print()
    with open("datarnk.txt", "w")as f:
        f.write("%d %d\n" % (R, R + 200))
