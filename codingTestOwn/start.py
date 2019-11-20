# -*- coding: utf-8 -*-
import time
import sys
from creditcardsystem.core import Core
from creditcardsystem.logger import loggers

loggings = loggers("Hansangyoon")

def main():

    t = time.process_time()
    core = Core()
    loggings.info("start: {0}".format(t))

    with open(sys.argv[1], 'r') if len(sys.argv) > 1 else sys.stdin as f:
        for line in f:
            core.parse_event(line)

    loggings.info("프로세스 종료: {0:.3f} 초 걸림".format(time.process_time() - t))
    totalInfo = core.generate_totalInfo()
    core.write_outputStringVal(totalInfo)

if __name__ == '__main__':
    main()




