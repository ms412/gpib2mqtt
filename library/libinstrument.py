
import visa
from library.msgbus import msgbus
from library.libgpib import libgpib

class instrument(msgbus):

    def __init__(self,config,msgSink,msgSource):

        self._config = config
        self._msgSink = msgSink
        self._msgSource = msgSource

        self.msgbus_subscribe(self._msgSink,self.notify)

        self._deviceList ={}

    def __del__(self):
        print('libvisa Delte myself')
        log_msg = 'Delete myself'
        self.msgbus_publish('LOG','%s %s: %s'%('DEBUG',self._whoami_(),log_msg))

    def _whoami_(self):
        return type(self).__name__

    def callback(self,msg):
        msg['HOST']='VISA'
        print('libinstrumetn callback',msg,self._msgSource)
        self.msgbus_publish(self._msgSource,msg)
        #print('libvisa callback',msg)

    def notify(self,msg):
        print('libvisa notify',msg)
        if 'VISA' in msg.get('HOST',None):
            _device = self._deviceList.get(msg.get('BUS',None),None)
            if not _device:
                log_msg = 'Notivication sink not found in DeviceList:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,msg.get('BUS')))
            else:
                log_msg = 'Noteivication sink found in DeviceList:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg,msg.get('BUS')))
                _device.notify(msg)

    def setup(self):

        for key,value in self._config.items():
            if 'VISA' in key:
                print("Start VISA interface")
                self.visaIf(value)
            else:
                log_msg = 'Instrument API unknown:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,key))


        log_msg = 'Following VISA Devices Successfull started:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg,self._deviceList.keys()))


    def visaIf(self,config):

        print('visaif',config)
       # self._rmHandle = visa.ResourceManager('@py')
        self._rmHandle = visa.ResourceManager()
     #   print('create rm')
      #  print(self._rmHandle)
       # print(self._rmHandle.list_resources())
        log_msg = 'VISA Resource Manager Started at:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg,self._rmHandle))

        log_msg = 'VISA Resource Manager following devices found:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('INFO',self._whoami_(),log_msg,self._rmHandle.list_resources()))

      #  print('config',self._config)

        for key,value in config.items():
            print('libvisa keylist',key)
            if key.upper().startswith('GPIB'):
                print('Test',key)
                #value['BUS']=key
       #         value['RESOURCE'] = self._rmHandle
                self._deviceList[key] = libgpib(key,value,self._rmHandle,self.callback)
                self._deviceList[key].start()
            else:
                log_msg = 'Unknown Device:'
                self.msgbus_publish('LOG','%s %s: %s %s'%('ERROR',self._whoami_(),log_msg,key))

      #  print('following devices started',self._deviceList)


        return True




if __name__ == "__main__":

    a = 1
    b = 2
    c = 3
    d = {'GPIB1':{'A':11,'B':12},'gpIB2':{'A2':21,'B2':22}}

    x = libvisa(d,b,c)
    print(x._whoami_())
    x.setup()
