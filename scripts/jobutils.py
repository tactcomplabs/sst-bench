#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# jobutils.py
#

# Currently coded for Python3.6 which is deprecated but still used

import os
import subprocess
import sys

class JobUtil():
    def __init__(self, id):
        self.id = id
        self.pfx = f"[jobutil.{id}]"
        self.rc = 0      # return code
        self.res1 = 0     # single result

    def exec(self, *, cmd:str, cwd:str = ".", log:str = ""):
        os.makedirs(cwd, exist_ok=True)
        cmdList=cmd.split()
        self.res1 = 0
        var_ok = len(log) == 0
        try:
            if len(log)==0:
                result = subprocess.run(cmdList, cwd=cwd, stdout=subprocess.PIPE, encoding='utf-8')
            else:
                logpath = f"{cwd}/{log}"
                with open(logpath, 'w') as outfile:
                    result = subprocess.run(cmdList, cwd=cwd, stdout=outfile, encoding='utf-8')
            if result.returncode != 0:
                print(f"{self.pfx} error: {cmd} : {result.stderr}")
            elif var_ok:
                self.res1 = result.stdout.rstrip()
        except subprocess.CalledProcessError as e:
            print(f"{self.pfx} error: {cmd} : {e.stderr}")
            return 1
        except FileNotFoundError as e:
            print(f"{self.pfx} error: {cmd} : {e.strerror}")
            return 1
        return result.returncode

if __name__ == '__main__':
    testdir = "test-jobutils"
    os.makedirs(testdir, exist_ok=True)
    jutil = JobUtil("test")

    rc = jutil.exec(cmd="echo test1 passed")
    if rc != 0:
        print("test1 failed")
        sys.exit(rc)
    print(jutil.res1)

    rc = jutil.exec(cmd="echo test2 passed", log=f"{testdir}/test2.log")
    if rc != 0:
        print("test2 failed")
        sys.exit(rc)
    print("test2 passed")

    rc = jutil.exec(cmd=f"cat test2.log", cwd=testdir)
    if rc != 0:
        print("test3 failed")
        sys.exit(rc)
    print("test3 passed")

    rc = jutil.exec(cmd="echo test4 passed", cwd=testdir, log=f"test4.log")
    if rc != 0:
        print("test4 failed")
        sys.exit(rc)
    print("test4 passed")

    rc = jutil.exec(cmd=f"cat test4.log", cwd=testdir)
    if rc != 0:
        print("test5 failed")
        sys.exit(rc)
    print("test5 passed")
