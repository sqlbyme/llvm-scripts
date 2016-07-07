#!/usr/bin/env python
################################################################################
# Author: Mike Edwards <medwards@apple.com>
################################################################################
# Description: A utility to fetch latest LLVM, Clang & LLD and build them.
################################################################################

from __future__ import print_function

import os
import shutil
import sys
import time

from subprocess import check_call, check_output


# TODO: Add in some argv processing
# TODO: Add some default args which cause us to build
# llvm, clang ad lld by default
# TODO: Add a docstring to provide help via the argv 
# processing thingy


# Setup Constants
BASE_DIR = '%s/pg' % os.environ['HOME']
WORK_DIR = '%s/llvm' % BASE_DIR
CLANG_SRC_DIR = '%s/clang.src' % WORK_DIR
COMPILER_RT_SRC_DIR = '%s/compiler-rt.src' % WORK_DIR
LLD_SRC_DIR = '%s/lld.src' % WORK_DIR
LLVM_SRC_DIR = '%s/llvm.src' % WORK_DIR
LLVM_OBJ_DIR = '%s/llvm.obj' % WORK_DIR
LLVM_BASE_URL = 'http://llvm.org/git'
LLVM_UPSTREAM_URL = '%s/llvm.git' % LLVM_BASE_URL
CLANG_UPSTREAM_URL = '%s/clang.git' % LLVM_BASE_URL
COMPILER_RT_UPSTREAM_URL = '%s/compiler-rt.git' % LLVM_BASE_URL
LLD_UPSTREAM_URL = '%s/lld.git' % LLVM_BASE_URL
NINJA_PATH = check_output(['which', 'ninja']).rstrip('\n')


def setup():
    print(">>>> Beginning LLVM & Clang Build. <<<<")
    print('---- Starting build timing test. ----')

    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)

    os.chdir(WORK_DIR)


def update_repos(repo_path, repo_url):
    if not os.path.exists(repo_path):
        shell_command = [
            'git',
            'clone',
            repo_url,
            repo_path
        ]
        result = check_call(shell_command)
        assert (result == 0), 'Git clone of %s failed.' % LLVM_UPSTREAM_URL
    else:
        os.chdir(repo_path)
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


def cmake_setup():
    os.chdir(WORK_DIR)
    if os.path.exists(LLVM_OBJ_DIR):
        shutil.rmtree(LLVM_OBJ_DIR, True)

    os.mkdir(LLVM_OBJ_DIR)
    os.chdir(LLVM_OBJ_DIR)

    # Setup and run cmake for building clang, lld & llvm
    cmake_command = [
	    'cmake',
        '-DCMAKE_MAKE_PROGRAM:STRING=%s' % NINJA_PATH,
        '-DCMAKE_BUILD_TYPE:STRING=Release',
        '-DLLVM_ENABLE_ASSERTIONS:BOOL=OFF',
        '-DLLVM_TARGETS_TO_BUILD:STRING=X86',
        '-DCMAKE_INSTALL_PREFIX:PATH=%s/Release' % LLVM_OBJ_DIR,
        '-DLLVM_EXTERNAL_CLANG_SOURCE_DIR:PATH=%s' % CLANG_SRC_DIR,
        '-DLLVM_EXTERNAL_COMPILER-RT_SOURCE_DIR:PATH=%s' % COMPILER_RT_SRC_DIR,
        '-DLLVM_EXTERNAL_LLD_SOURCE_DIR:PATH=%s' % LLD_SRC_DIR,
        '-GNinja',
        LLVM_SRC_DIR
	]
    print("Running CMAKE...")
    start_time = time.time()
    print(check_output(cmake_command))
    end_time = time.time()
    cmake_diff_time = end_time - start_time

    return cmake_diff_time


def ninja_build():
    ninja_command = ['ninja']
    print("---- Running NINJA ----")
    start_time = time.time()
    print(check_output(ninja_command))
    end_time = time.time()
    ninja_diff_time = end_time - start_time

    ninja_command = ['ninja', 'install']
    print("---- Installing binaries ----")
    print(check_output(ninja_command))
    
    return ninja_diff_time


def print_timing(cmake_time, ninja_time):
    print("---- Timing ----")
    print("Total Cmake Time: %f" % cmake_time)
    print("Total Ninja Time: %f" % ninja_time)


def main():
    setup()
    # Get latest LLVM
    update_repos(LLVM_SRC_DIR, LLVM_UPSTREAM_URL)
    # Get latest Clang
    update_repos(CLANG_SRC_DIR, CLANG_UPSTREAM_URL)
    # Get latest Compier-rt
    update_repos(COMPILER_RT_SRC_DIR, COMPILER_RT_UPSTREAM_URL)
    # Get latest LLD
    update_repos(LLD_SRC_DIR, LLD_UPSTREAM_URL)
    cmake_time = cmake_setup()
    ninja_time = ninja_build()
    print_timing(cmake_time, ninja_time)


if __name__ == '__main__':
    main()
    sys.exit(0)
