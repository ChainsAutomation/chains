from chains.service import Service
from chains.common import log
from datetime import datetime, timedelta
import re, hashlib, time, urllib2, urllib, sys, json

class RuterService(Service):
    """
    Service implementing Ruter API
    Needs fromplace, toplace and transporttypes in config to work.

    How to get fromplace and toplace:
    1) Find your line number: http://reisapi.ruter.no/Line/GetLines
    2) Find your stopids: http://reisapi.ruter.no/Line/GetStopsByLineID/9110 9110 = R10 (train)
    3) Put it in your config:
    Example (from Asker to Drammen):
    fromplace = 2200500
    toplace = 6021000
    transporttypes = bus,tram,train
    """

    def onInit(self):
        self.fromPlace = self.config.get('fromplace')
        self.toPlace = self.config.get('toplace')
        self.transportTypes = self.config.get('transporttypes')
        self.walkTime = self.config.get('walktime') or 10
        self.transportMapping = {
            'trikk': 'tram',
            'buss': 'bus',
            't-bane': 'metro',
            'tog': 'train'
        }

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
        timestamp = datetime.strftime(datetime.now() + timedelta(minutes=self.walkTime), '%d%m%Y%H%M00')
        url = self.apiUri + '?time=' + timestamp + '&fromplace=' + self.fromPlace + '&toplace=' + self.toPlace + '&isafter=true&transporttypes=' + self.transportTypes
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req)
            self.parseReponse(response.read())
        except urllib2.HTTPError as e:
            log.error('Error when updating TravelProposals %s: %s' % (e, e.read()))
            time.sleep(self.interval * 3)

    def parseReponse(self, response):
        jsonReponse = json.loads(response)

        for proposal in reversed(jsonReponse['TravelProposals']):
            departureTime = proposal['DepartureTime'].split('T')
            arrivalTime = proposal['ArrivalTime'].split('T')
            departureStop = re.search('(.*) \[(.*)\]', proposal['Stages'][0]['DepartureStop']['Name'])
            destinationStop = re.search('(.*) \[(.*)\]', proposal['Stages'][0]['ArrivalStop']['Name'])
            transportation = departureStop.group(2)
            self.addTravelProposal({
                'departureTime':   departureTime[1],
                'arrivalTime':     arrivalTime[1],
                'travelTime':      proposal['TotalTravelTime'],
                'departure':       departureStop.group(1),
                'destination':     destinationStop.group(1),
                'lineNumber':      proposal['Stages'][0]['LineName'],
                'transportation':  transportation
            })

    def addTravelProposal(self, proposal):
        eventName = "%s-%s" % (self.config.get('name'), proposal['lineNumber'].lower())
        self.sendEvent(eventName, {
            'departureTime':   { 'value': proposal['departureTime'] },
            'arrivalTime':     { 'value': proposal['arrivalTime'] },
            'departure':       { 'value': proposal['departure'] },
            'destination':     { 'value': proposal['destination'] },
            'travelTime':      { 'value': proposal['travelTime'] },
            'lineNumber':      { 'value': proposal['lineNumber']},
            'transportation':  { 'value': proposal['transportation']}
        }, {
            'device': eventName,
            'type': self.transportMapping[proposal['transportation'].lower()],
            'location': proposal['departure']
        })
