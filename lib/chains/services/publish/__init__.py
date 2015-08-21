from chains.service import Service
from chains.common import log
import socket
from zeroconf import ServiceInfo, Zeroconf


class PublishService(Service):
    """Service implementing zeroconf publishing service for chains master servers"""

    def onInit(self):
        log.info('Zeroconf publish init')
        self.ip_addr = self._get_ip()
        self.hostname = socket.gethostname()
        self.services = []
        self.desc = {'Description': 'Chains Home Automation service on rabbitmq'}
        self.amqp_info = ServiceInfo("_amqp._tcp.local.",
                                     "Chains Master AMQP %s._amqp._tcp.local." % self.hostname,
                                     socket.inet_aton(self.ip_addr), 5672, 0, 0,
                                     self.desc, "%s.local." % self.hostname)
        self.service.append(self.amqp_info)
        self.zeroconf = Zeroconf()

    def onStart(self):
        log.info('Starting zeroconf publishing service')
        for info in self.services:
            self.zeroconf.registerService(info)

    def _get_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('google.com', 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
