
from library.msgbus import msgbus

class msgAdapter(msgbus):

    def __init__(self,mqttSink,mqttSource,gpibSink,gpibSource):

        self._mqttSink = mqttSink
        self._mqttSource = mqttSource
        self._gpibSink = gpibSink
        self._gpibSource = gpibSource

        self.setup()

    def __del__(self):
        print('Delte myself')
        log_msg = 'Delete myself'
        self.msgbus_publish('LOG','%s %s: %s'%('DEBUG',self._whoami_(),log_msg))

    def _whoami_(self):
        return type(self).__name__


    def setup(self):

        self.msgbus_subscribe(self._mqttSource,self.mqtt2gpib)
        self.msgbus_subscribe(self._gpibSource,self.gpib2mqtt)


        return

    def mqtt2gpib(self,msg):

        _gpibmsg = {}

        _message = msg.get('VALUE',None)
        _channel = msg.get('CHANNEL',None)

        _chList = _channel.split('/')
      #  print('Channellsit',_chList)

        _gpibmsg['HOST']=_chList.pop(1)
        _gpibmsg['BUS']=_chList.pop(1)
        _gpibmsg['ADDRESS']=_chList.pop(1)
        _gpibmsg['CMD']=_chList.pop(1)
        _gpibmsg['VALUE']=_message

        print('dict',self._gpibSink,_gpibmsg)
        self.msgbus_publish(self._gpibSink,_gpibmsg)

        return



    def gpib2mqtt(self,msg):
        print('gpib2mqtt',msg)

        _mqttmsg = {}

        _message = msg['VALUE']
        _channel = ('/' + 'OPENHAB' + '/' + msg['BUS'] + '/' + msg['ADDRESS'] + '/' + msg['CMD'])

        _mqttmsg['VALUE'] = _message
        _mqttmsg['CHANNEL'] = _channel
        print('gpib2mqtt',_mqttmsg)

        self.msgbus_publish(self._mqttSink,_mqttmsg)

        return