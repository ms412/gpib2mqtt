#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "gpib2mqtt Adapter"
__VERSION__ = "0.8"
__DATE__ = "16.03.2016"
__author__ = "Markus Schiesser"
__contact__ = "Markus.Schiesser@swisscom.com"
__copyright__ = "Copyright (C) 2015 Markus Schiesser"
__license__ = 'GPL v3'


import sys
import time
from library.cfghandler import cfghandler
from library.mqttclient import mqttbroker
from library.msgbus import msgbus
from library.logging import log_adapter
from library.libinstrument import instrument
from library.libmsgAdapter import msgAdapter

class manager(msgbus):

    def __init__(self,cfgfile):
        self._cfgfile = cfgfile

        self._cfg_broker = None
        self._cfg_gerneral = None
        self._cfg_visa = None

    def readcfg(self):
        cfg = cfghandler()
     #   cfg = ConfigObj(self._cfgfile)
        cfg.open(self._cfgfile)

        self._cfg_broker = cfg.value('BROKER')
        self._cfg_general = cfg.value('GENERAL')
        self._cfg_visa = cfg.value('INSTRUMENTS')

        print('GENERAL',self._cfg_general)
        print('BROKER',self._cfg_broker)
        print('INSTRUMENTS',self._cfg_visa)

    def start_logging(self):
        self._log_thread = log_adapter(self._cfg_general)
        self._log_thread.start()
     #   self.msgbus_publish('LOG','%s Start Logging Adapter')

        return True

    def start_mqttbroker(self):
        self._mqttbroker = mqttbroker(self._cfg_broker,'MQTT-SNK','MQTT-SRC')
        self._mqttbroker.start()

        return True

    def start_instruments(self):
        self._visa = instrument(self._cfg_visa,'GPIB-SNK','GPIB-SRC')
        self._visa.setup()
        return True

    def start_msgAdapter(self):
        self._msgAdapter = msgAdapter('MQTT-SNK','MQTT-SRC','GPIB-SNK','GPIB-SRC')


    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
      #  print('Class Name',self.__class__.__name__)
    #    self.start_logging()
     #   self.msgbus_publish('LOG','%s Start mqtt2gpio adapter; Version: %s, %s '%('INFO', __VERSION__ ,__DATE__))
        self.readcfg()
        self.start_logging()
        log_msg = 'Start gpib2mqtt Adater'
        self.msgbus_publish('LOG','%s %s; Version: %s, Date: %s '%('INFO', log_msg, __VERSION__ ,__DATE__))


        self.start_mqttbroker()
        self.start_instruments()
        self.start_msgAdapter()
        time.sleep(5)
        #self.start_test()
        while True:
            time.sleep(10)
            print('has subscriber',self.has_subscriber('GPIB-SRC'))
           # self.test_msg()

      #  self.msgbus_publish('MQTT_TX','123456')
       # self.msgbus_subscribe('MQTT_RX',self.mqttif)
        #self.msgbus_subscribe('CAN_RX',self.canif)



if __name__ == "__main__":

    print ('main')
    if len(sys.argv) == 2:
        print('no commandline ')
        cfgfile = sys.argv[1]
    else:
        print('read default file')
        cfgfile = 'c:/gpib2mqtt/gpib2mqtt.cfg'

    mgr_handle = manager(cfgfile)
    mgr_handle.run()