#!/usr/bin/env python

import os
import shutil
from subprocess import check_call, check_output
import sys
import time

# TODO: Add in some argv processing
# TODO: Add some default args which cause us to build
# llvm, clang ad lld by default
# TODO: Add a docstring to provide help via the argv 
# processing thingy
# TODO: Add a function for printing a report header 
# and a section header



def build_clang_lld_llvm():

    # TODO: Remove this clear statement and just print a report header instead.
    os.system('clear')
    # TODO: this is a good example of a place to use a section header
    print 'Starting build timing test.'

    BASE_DIR = '%s/pg' % os.environ['HOME']
    WORK_DIR = '%s/llvm' % BASE_DIR
    CLANG_SRC_DIR = '%s/clang.src' % WORK_DIR
    LLD_SRC_DIR = '%s/lld.src' % WORK_DIR
    LLVM_SRC_DIR = '%s/llvm.src' % WORK_DIR
    LLVM_OBJ_DIR = '%s/llvm.obj' % WORK_DIR
    LLVM_BASE_URL = 'http://llvm.org/git'
    LLVM_UPSTREAM_URL = '%s/llvm.git' % LLVM_BASE_URL
    CLANG_UPSTREAM_URL = '%s/clang.git' % LLVM_BASE_URL
    LLD_UPSTREAM_URL = '%s/lld.git' % LLVM_BASE_URL

    if not os.path.exists(BASE_DIR):
        print """This script expects a playground directory named 'pg' 
            to be located in the users home directory.  Please ensure
            this has been created prior to continuing."""
        sys.exit(1)

    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)

    os.chdir(WORK_DIR)

    if not os.path.exists(LLVM_SRC_DIR):
        shell_command = [
            'git',
            'clone',
            LLVM_UPSTREAM_URL,
            LLVM_SRC_DIR
        ]
        result = check_call(shell_command)
        assert (result == 0), 'Git clone of %s failed.' % LLVM_UPSTREAM_URL
    else:
        os.chdir(LLVM_SRC_DIR)
        shell_command = [
            'git',
            'fetch'
        ]
        check_call(shell_command)
        shell_command = [
            'git',
            'reset',
            'FETCH_HEAD'
        ]
        result = check_call(shell_command)
        assert (result == 0), 'Git fetch of llvm failed.'


    os.chdir(WORK_DIR)
    if os.path.exists(LLVM_OBJ_DIR):
        shutil.rmtree(LLVM_OBJ_DIR, True)

    os.mkdir(LLVM_OBJ_DIR)
    os.chdir(LLVM_OBJ_DIR)

    # Setup and run cmake for building clang, lld & llvm
    cmake_command = [
	    'cmake',
                '-DCMAKE_MAKE_PROGRAM:STRING=/usr/bin/ninja',
		'-DCMAKE_BUILD_TYPE:STRING=Release',
		'-DLLVM_ENABLE_ASSERTIONS:BOOL=OFF',
		'-DLLVM_TARGETS_TO_BUILD:STRING=X86',
		'-DCMAKE_INSTALL_PREFIX:PATH=%s/Release' % LLVM_OBJ_DIR,
		#'-DLLVM_EXTERNAL_CLANG_SOURCE_DIR:PATH=%s' % CLANG_SRC_DIR,
		#'-DLLVM_EXTERNAL_LLD_SOURCE_DIR:PATH=%s' % LLD_SRC_DIR,
		'-GNinja',
		LLVM_SRC_DIR
	]
    print 'Running CMAKE...'
    start_time = time.time()
    print check_output(cmake_command)
    end_time = time.time()
    diff_time = end_time - start_time
    print "Start Time: %f" % start_time
    print "End Time: %f" % end_time
    print "Total Cmake Time: %f" % diff_time

    ninja_command = ['ninja']
    print 'Running NINJA...'
    start_time = time.time()
    print check_output(ninja_command)
    end_time = time.time()
    diff_time = end_time - start_time
    print "Start Time: %f" % start_time
    print "End Time: %f" % end_time
    print "Total Ninja Time: %f" % diff_time

    ninja_command = ['ninja', 'install']
    print 'Installing binaries...'
    print check_output(ninja_command)

    print 'Done for now...'

    print "Total Ninja Time: %f" % diff_time

def main():
    build_clang_lld_llvm()

if __name__ == '__main__':
    main()
