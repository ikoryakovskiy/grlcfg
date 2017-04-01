import os

r = os.system("g++ -c -fPIC repc.c -o repc.o")
if r == 0:
	os.system("g++ -shared -Wl,-soname,librepc.so -o librepc.so  repc.o")
	os.system("cython --embed bayes.py")
	os.system("gcc -Os -I /usr/include/python2.7 -o bayes bayes.c -lpython2.7 -lpthread -lm -lutil -ldl")
	os.system("./bayes")
