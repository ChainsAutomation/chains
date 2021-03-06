from __future__ import absolute_import

from chains.service import Service
from chains.common import log, utils

import time
import numbers
import types
from .cinflux import Influx as IX


class InfluxService(Service):

    def onInit(self):
        self.known_tags = ['service', 'location', 'device', 'type', 'key', 'name', 'class']
        self.aggregated = {
            'total_messages': 0,
            'heartbeats': 0,
            'service_events': {},
            'class_events': {},
        }
        # interval between pushing aggregated stats
        self.interval = self.config.getInt('interval') or 60
        try:
            self.ignoreclasses = self.config.get('ignoreclasses').split(',')
        except:
            self.ignoreclasses = []
        self.host = self.config.get('influxhost') or 'localhost'
        self.database = self.config.get('database') or 'chains'
        self.user = self.config.get('username') or 'chains'
        self.passwd = self.config.get('password') or 'chains'
        self.queryport = self.config.getInt('queryport') or 8086
        self.writemethod = self.config.get('writemethod') or 'http'
        if not self.config.getInt('writeport'):
            if self.writemethod == 'http':
                self.writeport = 8086
            elif self.writemethod == 'udp':
                self.writeport = 8089
        else:
            self.writeport = self.config.getInt('writeport')
        self.ix = IX(host=self.host, port=self.queryport, user=self.user, password=self.passwd, database=self.database, method=self.writemethod, writeport=self.writeport)

    def onStart(self):
        while not self._shutdown:
            time.sleep(self.interval)
            self.write_aggregated()

    def onMessage(self, topic, data, correlationId):
        self.aggregated['total_messages'] += 1
        if topic.startswith('se.') and not topic.endswith('.online'):
            # aggregation: update the total number of events from this service and class
            cursrv = topic.split('.')[1]
            if cursrv in self.aggregated['service_events']:
                self.aggregated['service_events'][cursrv] += 1
            else:
                self.aggregated['service_events'][cursrv] = 1
            if 'class' in data:
                if data['class'] in self.aggregated['class_events']:
                    self.aggregated['class_events'][data['class']] += 1
                else:
                    self.aggregated['class_events'][data['class']] = 1
            # Ignore is in config ignoreclasses or ignore is set for the service
            if 'class' in data:
                if data['class'] in self.ignoreclasses:
                    return
            if 'ignore' in data:
                if data['ignore'] in [True, 'True', 'true', 'Yes', 'yes', 'y']:
                    return
            # start picking out data to report
            measures = []
            tags = {}
            for tag in data:
                if tag in self.known_tags:
                    if tag == 'key':
                        tags.update({'event': data[tag]})
                    else:
                        tagValue = data[tag]
                        if type(tagValue) == str:
                            tagValue = tagValue.encode('utf-8')
                        tags.update({tag: tagValue})
            for measure in data['data']:
                try:
                    if 'value' in data['data'][measure]:
                        curval = data['data'][measure]['value']
                        if isinstance(curval, numbers.Number):
                            measures.append(self.ix.data_template(measure, tags, {'value': curval}))
                            # log.info('field: %s: %s' % (measure, str(curval)))
                            # log.info('tags: %s' % str(tags))
                        elif curval in [True, 'True', 'true', 'On', 'on', 'Yes', 'yes']:
                            measures.append(self.ix.data_template(measure, tags, {'value': True}))
                        elif curval in [False, 'False', 'false', 'Off', 'off', 'No', 'no']:
                            measures.append(self.ix.data_template(measure, tags, {'value': False}))
                        else:
                            # log.info('Skipping because value is not a number:')
                            # log.info("topic: " + str(topic))
                            # log.info("data: " + str(data))
                            pass
                except Exception as e:
                    log.warn("unexpected event structure? %s : %s : %s" % (e, measure, data))
                    pass
            log.debug('insert measures: %s' % measures)
            try:
                self.ix.insert(measures)
            except Exception as e:
                log.error('Failed inserting measures in influxdb: %s\nAttempted insert was: %s' % (utils.e2str(e), measures))
        elif topic[1] == 'h':
            # heartbeat
            self.aggregated['heartbeats'] += 1
        else:
            log.debug('not yet handled:')
            log.debug("- topic: " + str(topic))
            log.debug("- data: " + str(data))

    def getConsumeKeys(self):
        return ['#']

    def write_aggregated(self):
        log.info('Writing aggregated data')
        try:
            total_events = 0
            measures = []
            measures.append(self.ix.data_template('total_messages', {'type': 'chains', 'service': 'chainscore'}, {'value': self.aggregated['total_messages']}))
            measures.append(self.ix.data_template('heartbeats', {'type': 'chains', 'service': 'chainscore'}, {'value': self.aggregated['heartbeats']}))
            for cls, cval in self.aggregated['class_events'].items():
                measures.append(self.ix.data_template('class_events', {'type': 'chains', 'class': cls}, {'value': cval}))
            for srv, val in self.aggregated['service_events'].items():
                measures.append(self.ix.data_template('events', {'type': 'chains', 'service': srv}, {'value': val}))
                total_events += val
            measures.append(self.ix.data_template('total_events', {'type': 'chains', 'service': 'chainscore'}, {'value': total_events}))
            self.ix.insert(measures)
            # reset dict
            self.aggregated = {
                'total_messages': 0,
                'heartbeats': 0,
                'service_events': {},
                'class_events': {},
            }
        except Exception as e:
            log.info('write_aggregated exception: %s' % repr(e))
