from chains.service import Service
from chains.common import log
import hashlib, time, urllib2, urllib, sys, json

class RuterService(Service):
    """Service implementing Ruter API"""

    def onInit(self):
        self.fromPlace = self.config.get('fromplace')
        self.toPlace = self.config.get('toplace')
        self.transportTypes = self.config.get('transporttypes')
        self.travelProposals = {}

    def onStart(self):
        log.info('Starting Ruter service')
        self.interval = 5 * 60
        self.apiUri = 'http://reisapi.ruter.no/Travel/GetTravels'

        while not self._shutdown:
            self.updateTravelProposals()
            time.sleep(self.interval)

    def updateTravelProposals(self):
        log.info('Updating travel props')
        headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36" }
        url = self.apiUri + '?fromplace=' + self.fromPlace + '&toplace=' + self.toPlace + '&isafter=true&transporttypes=' + self.transportTypes
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req)
            self.parseReponse(response.read())
        except urllib2.HTTPError as e:
            log.error('Error when updating TravelProposals %s: %s' % (e, e.read()))
            time.sleep(self.interval * 3)

    def parseReponse(self, response):
        jsonReponse = json.loads(response)

        for proposal in jsonReponse['TravelProposals']:
            self.addTravelProposal({
                'departureTime':   proposal['DepartureTime'],
                'arrivalTime':     proposal['ArrivalTime'],
                'travelTime':      proposal['TotalTravelTime'],
                'departure':       proposal['Stages'][0]['DepartureStop']['District'],
                'destination':     proposal['Stages'][0]['ArrivalStop']['District'],
                'lineNumber':      proposal['Stages'][0]['LineName']
            })

    def addTravelProposal(self, proposal):
        key = ' '.join(['%s' % value for (key, value) in proposal.items()])
        md5Key = hashlib.md5(key).hexdigest()

        if md5Key not in self.travelProposals:
            self.travelProposals[md5Key] = proposal
            eventName = "ruter-%s" % proposal['lineNumber'].lower()
            self.sendEvent(eventName, {
                'departureTime':   { 'value': proposal['departureTime'] },
                'arrivalTime':     { 'value': proposal['arrivalTime'] },
                'departure':       { 'value': proposal['departure'] },
                'destination':     { 'value': proposal['destination'] },
                'travelTime':      { 'value': proposal['travelTime'] },
                'lineNumber':      { 'value': proposal['lineNumber']}
            }, {
                'device': eventName,
                'location': proposal['departure']
            })
