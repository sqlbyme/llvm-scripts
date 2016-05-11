#!/usr/bin/env python

import os
import shutil
from subprocess import check_call, check_output
import time

def build_clang_lld_llvm():

    os.system('clear')
    print 'Starting build timing test.'

    WORKDIR = '/Users/medwards/apps/scea/llvm'
    CLANG_SRC_DIR = '%s/clang.src' % WORKDIR
    LLD_SRC_DIR = '%s/lld.src' % WORKDIR
    LLVM_SRC_DIR = '%s/llvm.src' % WORKDIR
    SRC_PATHS = [CLANG_SRC_DIR, LLD_SRC_DIR, LLVM_SRC_DIR]
    LLVM_OBJ_DIR = '%s/llvm.obj' % WORKDIR

    # STEP - Update local repositories
    for path in SRC_PATHS:
        os.chdir(path)
        shell_command = [
            'git',
	        'pull',
	        'origin',
	        'master'
	    ]
        check_output(shell_command)
        shell_command = [
		    'git',
			'rev-parse',
			'HEAD'
		]
        git_rev = check_output(shell_command)
        print '%s was updated to rev:%s' % (path,git_rev)

    if os.path.exists(LLVM_OBJ_DIR):
	    shutil.rmtree(LLVM_OBJ_DIR)
	    os.mkdir(LLVM_OBJ_DIR)
	    os.chdir(LLVM_OBJ_DIR)
	    print 'Removed and re-created llvm.obj dir.'
    else:
	    os.mkdir(LLVM_OBJ_DIR)
	    os.chdir(LLVM_OBJ_DIR)
	    print 'Created llvm.obj dir.'

    print 'Currently working in %s' % os.getcwd()

    # Setup and run cmake for building clang, lld & llvm
    cmake_command = [
	    'cmake',
		'-DCMAKE_BUILD_TYPE:STRING=Release',
		'-DLLVM_ENABLE_ASSERTIONS:BOOL=OFF',
		'-DLLVM_TARGETS_TO_BUILD:STRING=X86',
		'-DCMAKE_INSTALL_PREFIX:PATH=%s/Release' % LLVM_OBJ_DIR,
		'-DLLVM_EXTERNAL_CLANG_SOURCE_DIR:PATH=%s' % CLANG_SRC_DIR,
		'-DLLVM_EXTERNAL_LLD_SOURCE_DIR:PATH=%s' % LLD_SRC_DIR,
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

def build_game7():

    print 'Fetching latest game7 updates.'
    os.chdir(WORKDIR)

def main():
    build_clang_lld_llvm()

if __name__ == '__main__':
    main()
