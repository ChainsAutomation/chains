from chains.service import Service
from chains.common import log
import sys
import time
import cec


class CECService(Service):

    def onInit(self):
        self.adapters = cec.list_adapters()
        if len(self.adapters) < 1:
            sys.exit('No CEC adapters found')
        else:
            self.adapter = self.adapters[0]
            log.info('Found adapter(s): %s' % str(self.adapters))
            log.info('Using adapter %s' % self.adapter)
            self.sendEvent('current_adapter', {'id': 0})
        cec.init(self.adapter)
        # Service config
        self.interval = self.config.get('interval') or 60
        self.location = self.config.get('location')
        self.cur_service = None

    def onStart(self):
        while not self._shutdown:
            self.services = cec.list_services()
            self.sendEvent('services', {'detected': self.services})
            # TODO: Implement the cec callbacks
            time.sleep(float(self.interval))

    def action_set_adapter(self, adapter):
        '''
        Set default CEC adapter
        @param  adapter  int  Default adapter ID
        '''
        cec.init(adapter)
        self.adapter = adapter
        meta = {'device': self.adapter}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('set_adapter', {'active_adapter': {'value': self.adapter}}, meta)

    def action_set_service(self, service):
        '''
        Set default CEC service
        @param  adapter  int  Default service ID
        '''
        self.cur_service = cec.Service(service)
        self.action_describe_service(service)
        meta = {'device': self.adapter}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('set_service', {'active_service': {'value': self.cur_service}}, meta)

    def action_list_adapters(self):
        '''
        Find connected CEC adapters
        '''
        self.adapters = cec.list_adapters()
        meta = {'device': self.adapter}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('adapters', {'adapters': {'value': self.adapters}}, meta)

    def action_list_services(self):
        '''
        Find connected CEC services
        '''
        self.services = cec.list_services()
        meta = {'device': self.adapter}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('services_list', {'services': {'value': self.services}}, meta)

    def action_describe_service(self, cecdev):
        '''
        Describe a connected CEC service
        '''
        dev = cec.Service(cecdev)
        meta = {'device': cecdev}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('service_describe', {'address': dev.address, 'phy': dev.physical_address,
                                'vendor': dev.vendor, 'OSD': dev.osd_string,
                                'cec_version': dev.cec_version,
                                'language': dev.language
                                }, meta)

    def action_power_on(self, cecdev=None):
        '''
        Turn CEC service power on
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if not dev.is_on:
            dev.power_on()

    def action_power_off(self, cecdev=None):
        '''
        Turn CEC service power off
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if dev.is_on:
            dev.power_off()

    def action_power_toggle(self, cecdev=None):
        '''
        Toggle CEC service power
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if dev.is_on:
            dev.power_off()
        elif not dev.is_on:
            dev.power_on()
        else:
            log.warn('powertoggle failed because power status could not be determined')

    # TODO: find correct cec code for volume commands
    def action_volume_mute(self, cecdev=None):
        '''
        Mute CEC service
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if dev.is_on:
            dev.mute()

    # TODO: find correct cec code for volume commands
    def action_volume_up(self, cecdev=None):
        '''
        Sound volume up on CEC service
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if dev.is_on:
            dev.volume_up()

    # TODO: find correct cec code for volume commands
    def action_volume_mute(self, cecdev=None):
        '''
        Sound volume down on CEC service
        @param  adapter  int  CEC service ID
        '''
        if not cecdev:
            cecdev = self.cur_service
        dev = cec.Service(cecdev)
        if dev.is_on:
            dev.volume_down()


