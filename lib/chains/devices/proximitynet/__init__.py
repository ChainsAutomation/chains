import chains.device
from chains.common import log
import datetime
from scapy.all import *

class ProximitynetDevice(chains.device.Device):

    def onStart(self):
        last = {}
        while not self._shutdown:
            sniff(prn=self.arp_monitor_callback, filter="arp", store=0)

    def arp_monitor_callback(self, pkt):
        # pkt.show()
        if pkt.haslayer(ARP):  # This is needed since the filter some times lets through non-arp frames
            if pkt[ARP].op == 1:  # who-has (request)
                t = datetime.datetime.now()
                log.info("ARP Request: " + pkt[ARP].psrc + " is asking about " + pkt[ARP].pdst)
                self.sendEvent(pkt.psrc, {'time': t})
                return pkt.psrc
            if pkt[ARP].op == 2:  # is-at (response)
                log.info("ARP Response: " + pkt[ARP].hwsrc + " has address " + pkt[ARP].psrc)
