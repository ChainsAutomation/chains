from chains.service import Service
from chains.common import log
from scapy.all import *

class ProximitynetService(Service):

    def onInit(self):
        self.location = self.config.get('location')
        # TODO:
        # Add 'friends' section or similar to config to do lookups against in requests

    def onStart(self):
        while not self._shutdown:
            sniff(prn=self.arp_monitor_callback, filter="arp", store=0)

    def arp_monitor_callback(self, pkt):
        # pkt.show()
        if pkt.haslayer(ARP):  # This is needed since the filter some times lets through non-arp frames
            if pkt[ARP].op == 1:  # who-has (request)
                log.info("ARP Request: " + pkt[ARP].psrc + " is asking about " + pkt[ARP].pdst)
                # self.sendEvent(pkt.psrc, {'type': 'arp_query'})
                props = {'ip_address': {'value': pkt[ARP].pdst}}
                meta = {'device': pkt[ARP].psrc, 'type': 'proximity'}
                if self.location:
                    meta.update({'location': self.location})
                self.sendEvent("arp_request", props, meta)
                # return pkt.psrc
            if pkt[ARP].op == 2:  # is-at (response)
                log.info("ARP Response: " + pkt[ARP].hwsrc + " has address " + pkt[ARP].psrc)
                # self.sendEvent(pkt[ARP].hwsrc, {'device': 'ARP', 'address': pkt[ARP].psrc, 'type': 'arp_response'})
                # TODO: Lookup to see if MAC is in friends dictionary and replace MAC with name
                props = {'ip_address': {'value': pkt[ARP].psrc}, 'mac_address': pkt[ARP].hwsrc}
                meta = {'device': pkt[ARP].hwsrc, 'type': 'proximity'}
                if self.location:
                    meta.update({'location': self.location})
                self.sendEvent('arp_response', props, meta)
