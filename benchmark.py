#!/usr/bin/python

from common import run_cmake
from common import setup
from common import benchmark
from common import src
from common import obj


import subprocess
import os
import platform
import sys
import shutil

setup(internet=True)

def build_stage(n):
    inst_dir = obj + '/llvm-inst%s' % n

    optimize=True
    plugin = False
    static = platform.system() != 'Darwin'
    if n == 1:
        CC = '/usr/bin/gcc'
        CXX = '/usr/bin/g++'
        AR = 'ar'
        asserts = False
        lto = False
    else:
        prev_inst_dir = obj + '/llvm-inst%s' % (n-1)
        os.environ['DYLD_LIBRARY_PATH'] = prev_inst_dir + '/lib/'
        CC =  prev_inst_dir + '/bin/clang'
        CXX = CC + '++'
        if platform.system() == 'Darwin':
            AR = 'ar'
        else:
            AR =  prev_inst_dir + '/bin/llvm-ar'
        asserts = False
        lto = False

    build_dir = obj + '/bootstrap-stage%s' % n
    subprocess.check_call(['mkdir', build_dir])
    subprocess.check_call(['mkdir', inst_dir])

    os.chdir(build_dir)

    run_cmake(CC=CC, CXX=CXX, AR=AR, inst_dir=inst_dir, optimize=optimize,
              asserts=asserts, lto=lto, static=static, plugin=plugin)

    if n == 1:
        subprocess.check_call(['ninja'])
        subprocess.check_call(['ninja', 'install'])
    else:
        subprocess.check_call(['time', 'ninja'])
        subprocess.check_call(['time', 'ninja', 'check-all'])
    
    os.chdir('..')

assert os.path.exists(src + '/tools/clang')
assert os.path.exists(src + '/tools/lld')
if platform.system() == 'Darwin':
    assert not os.path.exists(src + '/projects/libcxx')
else:
    assert not os.path.exists(src + '/projects/libcxx')
assert not os.path.exists(src + '/tools/clang/tools/extra')
build_stage(1)
build_stage(2)
