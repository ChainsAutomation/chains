from chains.service import Service
from chains.common import log
from netaddr import *
import socket
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
                props = {'source-ip': {'value': pkt[ARP].psrc}, 'target-ip': {'value': pkt[ARP].pdst}}
                props.update(self._chainsify(self._ip_info(pkt[ARP].psrc, 'source')))
                props.update(self._chainsify(self._ip_info(pkt[ARP].pdst, 'target')))
                meta = {'device': pkt[ARP].psrc.replace('.', '-'), 'type': 'proximity'}
                if self.location:
                    meta.update({'location': self.location})
                self.sendEvent("arp_request", props, meta)
                # return pkt.psrc
            if pkt[ARP].op == 2:  # is-at (response)
                log.info("ARP Response: " + pkt[ARP].hwsrc + " has address " + pkt[ARP].psrc)
                # self.sendEvent(pkt[ARP].hwsrc, {'device': 'ARP', 'address': pkt[ARP].psrc, 'type': 'arp_response'})
                # TODO: Lookup to see if MAC is in friends dictionary and replace MAC with name
                props = {'ip_address': {'value': pkt[ARP].psrc}, 'mac_address': {'value': pkt[ARP].hwsrc}}
                props.update(self._chainsify(self._mac_info(pkt[ARP].hwsrc)))
                meta = {'device': pkt[ARP].hwsrc, 'type': 'proximity'}
                if self.location:
                    meta.update({'location': self.location})
                self.sendEvent('arp_response', props, meta)

    def _ip_info(self, ipaddr, prefix):
        # TODO: the socket method only returns a single item in forward/reverse lookups
        ip = IPAddress(ipaddr)
        info = {'%s-type' % prefix: 'unknown'}
        # rfc1918 addresses
        if ip.is_private():
            info['%s-type' % prefix] = 'rfc1918'
            info.update({'%s-reverse' % prefix: ip.reverse_dns})
        elif ip.is_unicast() and not ip.is_private():
            info['%s-type' % prefix] = 'public'
            try:
                dns = socket.gethostbyaddr(ipaddr)[0]
            except socket.error, e:
                if len(e.args) > 0:
                    dns = "%s" % e.args[0]
                else:
                    dns = 'Lookup failed'
            info.update({'%s-type' % prefix: '%s-public' % prefix, '%s-reverse' % prefix: dns})
        else:
            info.update({'%s-reverse' % prefix: ip.reverse_dns})
        return info

    def _mac_info(self, macaddr):
        info = {}
        fields = ['address', 'idx', 'offset', 'org', 'oui', 'size']
        try:
            mac = EUI(macaddr)
            oui = mac.oui
            for item in oui.registration():
                if item == 'address':
                    addr = ','.join(oui.registration()[item])
                    info.update({'address': addr})
                else:
                    info.update({item: oui.registration()[item]})
        except NotRegisteredError, e:
            if len(e.args) > 0:
                info.update({'org': str(e.args[0])})
            else:
                info.update({'org': 'OUI not registered'})
        for item in fields:
            if item not in info:
                info.update({item: 'unknown'})
        return info

    def _chainsify(self, mdict):
        for item in mdict:
            mdict[item] = {'value': mdict[item]}
        return mdict
