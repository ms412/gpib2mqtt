
import time
from threading import Thread
from queue import Queue

from library.msgbus import msgbus
from library.libHP8157A import libHP8157A

from library.libdictitree import dictree

class libgpib(Thread,msgbus):

    def __init__(self,id,config,rmHandle, callback):
        Thread.__init__(self)

        self._id = id
        self._config = config
        self._callback = callback
        self._rmHandle = rmHandle

        self._deviceList = dictree()

        self._notifyQ = Queue(maxsize=1)

        log_msg = 'Create Object with config:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, self._config))

        self.setupWrapper()

       # if False in self.setup():
        #print('SETUP:',self.setup())

    def __del__(self):
      #  print('libgpib delet myself')
        log_msg = 'Kill myself:'
        self.msgbus_publish('LOG','%s %s: %s '%('DEBUG',self._whoami_(),log_msg))

    def _whoami_(self):
        return type(self).__name__

    def notify(self,msg):
     #   print('libgpib notification',msg)
        log_msg = 'Received Notification:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, msg))
        try:
            self._notifyQ.put_nowait(msg)
        except:
        #    print('queue overrun throw away')
            log_msg = 'Buffer Overrun through message away:'
            self.msgbus_publish('LOG','%s %s: %s'%('DEBUG',self._whoami_(),log_msg))
            pass

    def setupWrapper(self):
        print('gpib setup',self._config)

        for key,value in self._config.items():
            log_msg = 'Try to establish link to measurement set:'
            self.msgbus_publish('LOG','%s %s: %s %s :: %s'%('DEBUG',self._whoami_(),log_msg, self._id, key))

        #    print('libgpib list config:',key,value)
            self._deviceList[key]['config']=value
            self._deviceList[key]['state']=False
            self._deviceList[key]['handle']=None
            print('TEST',self._deviceList)
           # self._deviceList[key]

            if self._deviceList[key]['state'] == False:
                self.setup(key,value)

        return True

    def setup(self,key,value):

        if 'HP8158B' in value.get('TYPE'):
            _instrPath = (self._id + '::' + key + '::' + 'INSTR')
            #print('libgpib list instrument path',_instrPath )

               # _deviceHandle = _instrPath
            try:
                _deviceHandle = self._rmHandle.open_resource(_instrPath)
             #   print('connected')
                log_msg = 'Establish link to HP8158B:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg,_instrPath))
            except:
              #  print('connection failed')
                self._deviceList[key]['state']=False
                log_msg = 'Cannot establish link to HP8158B:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,_instrPath))

                return False
                   # break
                #value['DEV_HANDLE']=_deviceHandle
            self._deviceList[key]['handle']=libHP8157A(_deviceHandle, value)
            self._deviceList[key]['state']=True

        else:
         #   print('instrument unknown')
            self._deviceList[key]['state']=None
            log_msg = 'Unknown Instrument:'
            self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,value.get('TYPE')))

        return True

    def run(self):

        threadRun = True
        timeHandle = time.time()

        while threadRun:
            time.sleep(1)
     #       print('Thread')

            # update every 30sec
            if timeHandle + 30 < time.time():
                timeHandle = time.time()
                for key,value in self._deviceList.items():
                    # if no link to measurement set could get established so far
                    # we try again
                    if self._deviceList[key]['state'] == False:
                        log_msg = 'Retry to establish link to measurement set:'
                        self.msgbus_publish('LOG','%s %s: %s %s :: %s'%('DEBUG',self._whoami_(),log_msg, self._id, key))
                        #print('Retry with config',key,self._deviceList[key]['config'])
                        self.setup(key,self._deviceList[key]['config'])

                # send update periodically to host, form all measurement sets available
                for key, value in self._deviceList.items():
                    if self._deviceList[key]['state'] == True:
                        update_msg = value['handle'].UPDATE(['GET_ATT'])
                        update_msg['ADDRESS']=key
                        update_msg['BUS'] = self._id
                        self._callback(update_msg)

            # in case we received a notification
            while not self._notifyQ.empty():
                _notification = self._notifyQ.get()
              #  print('libgpib',_notification)
                _device = self._deviceList[(_notification.get('ADDRESS'))]
              #  print('Device Address',_device)
                # if measurement is available in the list
                if self._deviceList.get(_notification.get('ADDRESS',None),None) == None:
                    log_msg = 'No Measurement Set with this Address available:'
                    self.msgbus_publish('LOG','%s %s: %s %s :: %s'%('ERROR',self._whoami_(),log_msg, self._id, _notification.get('ADDRESS',None)))

                elif self._deviceList[(_notification.get('ADDRESS'))]['state'] == True:
                  #  print('Device online')
                    _instance = self._deviceList[(_notification.get('ADDRESS'))]['handle']
                #print('libgpib instance',_instance,self._deviceList)
                #if not _instance:
                 #   log_msg = 'Unknown Bus in Notification:'
                  #  self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,_notification.get('BUS')))
                #else:
                    _cmd = _notification.get('CMD',None)
                #    print('CMD',_instance,_cmd)
                  #  getattr(_instance,_cmd)()#send
                    getattr(_instance,_cmd)(_notification.get('VALUE',None))

                    # send update
                    update_msg = _instance.UPDATE(['GET_ATT'])
                    update_msg['ADDRESS']=_notification.get('ADDRESS')
                    update_msg['BUS'] = self._id
                #update_msg['VALUE']=value.update()
                    print("SEND UPDATGE TO OPENHAB,", update_msg)
                    self._callback(update_msg)

                else:
                   # print('device not online')
                    log_msg = 'Device not Online:'
                    self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,_notification.get('ADDRESS')))






