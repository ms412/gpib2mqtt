import logging
import time
import datetime

import datetime

from queue import Queue
from threading import Thread, Lock

from library.msgbus import msgbus


class log_adapter(Thread, msgbus):
    '''
    classdocs
    '''

    def __init__(self,config):
        Thread.__init__(self)
        print('init logging')

        self._config = config

        self._logFile = self._config['LOGFILE']

        self.log_queue = Queue()

        self._logFileHandle = None



    def run(self):
        print('run logging adapter')

        self.setup()
        self.openfile()


        threadRun = True

        while threadRun:
            time.sleep(5)
            while not self.log_queue.empty():
                self.openfile()
                    # self.on_log(self.log_queue.get())

                self.write(self.log_queue.get())
                self.closefile()



        return True

    def setup(self):
        self.msgbus_subscribe('LOG', self._on_log)
        return True

    def _on_log(self, log_msg):
       # print('LOG:',log_msg)
        msg = (str(self.timestamp()) + '\t' + log_msg + '\n')
        self.log_queue.put(msg)
      #  print('LOG:',msg)
        return True

    def openfile(self):
      #  print('LOG: Openlogfile', self._logFileName)
        self._logFileHandle = open(self._logFile, "a")
        return True

    def closefile(self):
     #   print('LOG: Closelogfile', self._logFileHandle)
        self._logFileHandle.closed
        return True

    def write(self, logdata):
        print('LOG timestamp:', logdata)
        #self._logFileHandle.write(str(self.timestamp()) + '\t' + logdata + '\n')
        self._logFileHandle.write(logdata)
        return True

    def timestamp(self):
        #print('Datetime', datetime.datetime.now())
        return datetime.datetime.now()
       # return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S').format
