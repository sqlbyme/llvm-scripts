import subprocess
import platform
import os
import shutil

HOME = os.environ['HOME']
benchmark = '/tmp/benchmark_llvm' % HOME
LLVM_SRC = '%s/llvm.src' % benchmark
CLANG_SRC = '%s/clang.src' % benchmark
LLD_SRC = '%s/lld.src' % benchmark
obj = '%s/llvm.obj' % benchmark

def which(x):
  return subprocess.check_output(['which', x]).strip()

def git(*args):
  return subprocess.check_call([which('git')] + list(args))

def svn(*args):
  return subprocess.check_call([which('svn')] + list(args))

def setup(internet=True, use_git=True):
  if not os.path.exists(benchmark):
    os.makedirs(benchmark)
    os.makedirs(obj)
    os.chdir(benchmark)
    if use_git:
      clone_url_prefix = 'git://assets.llvm.scea.com/'
      if internet:
        clone_url_prefix = 'http://llvm.org/git/'
      git('clone', '%sllvm.git' % clone_url_prefix, LLVM_SRC)
      git('clone', '%sclang.git' % clone_url_prefix, CLANG_SRC)
      git('clone', '%slld.git' % clone_url_prefix, LLD_SRC)
    else:
      clone_url_prefix = 'http://llvm.org/svn/llvm-project/'
      svn('checkout', '%sllvm/trunk' % clone_url_prefix, LLVM_SRC)
      svn('checkout', '%scfe/trunk' % clone_url_prefix, CLANG_SRC)
      svn('checkout', '%slld/trunk' % clone_url_prefix, LLD_SRC)
  else:
    shutil.rmtree(obj, True)
    os.makedirs(obj)
    #os.chdir(src)
    #git('pull', 'origin', 'master')
    #os.chdir(src + '/tools/clang')
    #git('pull', 'origin', 'master')
    #os.chdir(src + '/tools/lld')
    #git('pull', 'origin', 'master')

  os.chdir(obj)

  print('Setup complete...\n')
 
def run_cmake(CC='clang', CXX='clang++', AR='ar',
              inst_dir='%s/llvm/test-install' % HOME, optimize=True, asserts=True,
              debug=False, lto=False, stats=False, asan=False, msan=False,
              static=False, shared=False, plugin=False, profile=False):
  if CC == 'clang':
    CC = which(CC)
  if CXX == 'clang++':
    CXX = which(CXX)
  if AR == 'ar':
    AR = which(AR)
  RANLIB = which('true')

  CFLAGS=[]

  if not 'gcc' in CC:
    CFLAGS += ['-fcolor-diagnostics']

  if stats:
    CFLAGS += ['-DLLVM_ENABLE_STATS']

  if optimize:
    if debug:
      buildtype = 'RelWithDebInfo'
    else:
      buildtype = 'Release'
  else:
    if debug:
      buildtype = 'Debug'
    else:
      buildtype = 'None'

  CMAKE_ARGS  = ['-DCLANG_BUILD_EXAMPLES=OFF', '-DLLVM_BUILD_EXAMPLES=OFF',
                 '-G', 'Ninja',
                 '-DCMAKE_INSTALL_PREFIX=%s' % inst_dir,
                 '-DCMAKE_BUILD_TYPE=%s' % buildtype,
                 '-DLLVM_ENABLE_SPHINX=OFF',
                 '-DCOMPILER_RT_BUILD_SHARED_ASAN=OFF',
                 '-DLLVM_TARGETS_TO_BUILD=X86',
                 '-DLLVM_EXTERNAL_CLANG_SOURCE_DIR=%s' % CLANG_SRC,
                 '-DLLVM_EXTERNAL_LLD_SOURCE_SIR=%s' % LLD_SRC,
                ]

  # FIXME: Talk with espindola about linker flag usage 
  #linker_flags=[]
  #if lto:
  #  linker_flags += ['-flto']
  #if optimize and platform.system() != 'Darwin':
  #  if not profile:
  #    linker_flags += ['-Wl,--strip-all']

  if asan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Address']
  elif msan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Memory']

  #if linker_flags:
  #  CMAKE_ARGS +=  ['-DCMAKE_EXE_LINKER_FLAGS=' + ' '.join(linker_flags)]

  if static:
    CMAKE_ARGS += ['-DLIBCLANG_BUILD_STATIC=OFF']
    CMAKE_ARGS += ['-DLLVM_BUILD_STATIC=OFF']

  if shared:
    CMAKE_ARGS += ['-DBUILD_SHARED_LIBS=ON']

  if asserts:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=ON']
  else:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=OFF']

  if plugin:
    CMAKE_ARGS += ['-DCLANG_PLUGIN_SUPPORT=ON']
  else:
    CMAKE_ARGS += ['-DCLANG_PLUGIN_SUPPORT=OFF']

  if lto:
    CFLAGS += ['-flto']

  CXXFLAGS=CFLAGS

  CMAKE_ARGS += ['-DCMAKE_C_FLAGS=%s' % ' '.join(CFLAGS)]
  CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS=%s' % ' '.join(CXXFLAGS)]

  os.environ['CC'] = CC
  os.environ['CXX'] = CXX
  cmd = ['cmake', LLVM_SRC ] + CMAKE_ARGS
  subprocess.check_call(cmd)
