import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os, sys, time




class Win32Service(win32serviceutil.ServiceFramework):
    _svc_name_ = "GPIB2MQTT"
    _svc_display_name_ = "GPIB2MQTT Service"
    _svc_description_ = "GPIB2MQTT interface"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.stop_event = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False
        self.execScript = "c:/gpib2mqtt/gpib2mqtt.py"

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
      #  logging.info('Stopping service ...')
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        self.StartAppl(self.execScript)

    def StartAppl(self,filepath):

        global_namespace = {
            "__file__": filepath,
            "__name__": "__main__",
        }
        try:
            with open(filepath, 'rb') as file:
                exec(compile(file.read(), filepath, 'exec'), global_namespace)
        except SystemExit:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, 'Failed to start')
            )
        return

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(Win32Service)
