from library.msgbus import msgbus

class libHP8157A(msgbus):

    def __init__(self,handle,config):

        self._config = config
        self._instrHandle = handle

        log_msg = 'Create Object with config:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, self._config))

        self._setup()


    def __del__(self):
       # print('HP8157A kill myself', self._instrName)
        log_msg = 'Kill myself:'
        self.msgbus_publish('LOG','%s %s: %s '%('DEBUG',self._whoami_(),log_msg))

    def _whoami_(self):
        return type(self).__name__

    def _setup(self):
        self._instrName = self._getInventory()
     #   print('start hp8157A;,',self._config,self._instrName)
        log_msg = 'Preconfigure Measurement Inventory:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, self._instrName))

        _CAL = self._config.get('CALIBRATION','0')
        _WVL = str(self._config.get('WAVELENGTH','1550'))
        self._setWavelenght(_WVL)
        self._setCalibration(_CAL)
        self._enableOutput()
        return True


    def GET_ATT(self):
        log_msg = 'GET_ATT Function Called:'
        self.msgbus_publish('LOG','%s %s: %s'%('DEBUG',self._whoami_(),log_msg))

        return self._getattenuation()

    def SET_ATT(self, value):
        log_msg = 'SET_ATT Function Called:'
        self.msgbus_publish('LOG','%s %s: %s'%('DEBUG',self._whoami_(),log_msg))

        value = value.decode('ascii')
#        print ('SET ATTENUATIN',value,self._instrName)
        self._setAttenuation(value)
        return

    def UPDATE(self,cmd):
        log_msg = 'UPDATE Called with Functions:'
        self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg,cmd))
        update_msg = {}
        for item in cmd:
            print('test',item)
            update_msg['VALUE']=getattr(self,item)()
            update_msg['CMD'] = item
            update_msg['INSTRUMENT']= self._instrName

        return update_msg

    def _getattenuation(self):
        result = self._query('ATT?')
        result = "".join(result.split())

        return result

       # s = self._instrHandle.query('ATT?')
        #return "".join(s.split())
      #  return self._instrHandle.query('ATT?')

    def _getInventory(self):
        result = self._query('*IDN?')

        return result

      #  return self._instrHandle.query('*IDN?')

    def _setAttenuation(self,value):
        result = self._write('ATT',value)

        return result
     #   print('Sett Attenunation ', value)
      #  self._instrHandle.write('ATT ',value)
       # print('GETt Attenueation', self._getattenuation())
        #return True

    def _setWavelenght(self,value):
        result = self._write('WVL', value + 'nm')

        return result

    #    print('WVL ' + value + ' nm')
     #   self._instrHandle.write('WVL ' + value + ' nm')
      #  print('Set wAVELEnght', self._instrHandle.query('WVL?'))
       # return True

    def _getWavelength(self):
        result = self._query('WVL?')

        return result
      #  return self._instrHandle.read('WVL?')

    def _setCalibration(self,value):
        result = self._write('CAL %s dB', value)

        return result

     #   self._instrHandle.write('CAL %s dB', value)
      #  return True

    def _getCalibration(self):
        result = self._query('CAL?')

        return result

   #     return self._instrHandle.read('CAL?')

    def _enableOutput(self):
        result = self._write('D', '0')

        return result
     #   self._instrHandle.write('D 0')
      #  return True

    def _disableOutput(self):
        result = self._write('D', '1')

        return result
    #    self._instrHandle.write('D 1')
     #   return True

    def _query(self,cmd):

        try:
            result = self._instrHandle.query(cmd)
        except:
            result = None
            log_msg = 'GPIB Query failed for command:'
            self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, cmd))

        return result

    def _write(self,cmd, value):

        try:
            result = self._instrHandle.write(cmd, value)
        except:
            result = None
            log_msg = 'GPIB Write failed for command:'
            self.msgbus_publish('LOG','%s %s: %s %s'%('DEBUG',self._whoami_(),log_msg, cmd))

        return result
