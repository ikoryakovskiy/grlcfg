import os

#os.chdir("../")
os.system("cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ../src/grl")
os.system("make -j32")
