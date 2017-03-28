import os

os.system("cython --embed bayes.py")
os.system("gcc -Os -I /usr/include/python2.7 -o bayes bayes.c -lpython2.7 -lpthread -lm -lutil -ldl")
os.system("./bayes")
