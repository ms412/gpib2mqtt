__author__ = 'oper'

from configobj import ConfigObj

class cfghandler:

    def __init__(self):
        print('Create ConfigObj')
        self._config = None

    def __del__(self):
        print('Delete ConfigObj')

    def open(self, filename):
        try:
            self._config = ConfigObj(filename)
            print('openfile')
            return True
        except:
            print('ERROR open file:',filename)
        return False

    def keys(self):
        return self._config.keys()

    def value(self,key):
        print('key',key)
        return self._config[key]

    def tree(self):
        print('dic:',self._config)
        return self._config



if __name__ == '__main__':

    config = configfile()
    config.open('configfile.cfg')
    cfg = config.tree()
    section1 = cfg['BROKER']
    print('Broker',section1)
    print('Keys Layer1',config.keys())
    print('Value key1', config.value('key'))

