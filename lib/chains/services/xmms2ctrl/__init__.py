#!/usr/bin/python

# gpl v2
# basic xmmsclient stuff ripped from jukx

import sys
import time
import os
import xmmsclient

from threading import Thread
from chains.service import Service
from chains.log import Log
#from chains.client import Client

class Xmms2CtrlService(Service):

    def init(self):
        self.reader = Xmms2Reader(self)
        self.reader.setDaemon(True)
        pass

    def open(self):
        print "open"
        self.reader.start()
        pass

    def close(self):
        self.reader.stop = True
        pass

    def onEvent(self, key, value, extra):
        event = {
            'key':    key,
            'service': self.config['id'],
            'value':  value,
            'extra':  extra
        }
        self.devDaemon.onEvent(event)
        # eventlistener is here a servicedaemon object
        # do not confuse with EventListener in server.py


    def onCommand(self, command, args):
        if command == 'play':
            self.reader.xmms2base.play()
        elif command == 'stop':
            self.reader.xmms2base.stop()
        elif command == 'pause':
            self.reader.xmms2base.pause()
        elif command == 'clear':
            self.reader.xmms2base.clear()
        elif command == 'next':
            self.reader.xmms2base.next()
        elif command == 'prev':
            self.reader.xmms2base.prev()
        elif command == 'get_current_id':
            curid = self.reader.xmms2base.get_current_id()
            print curid
            self.onEvent('current_id',curid,[])
        elif command == 'play_next':
            if len(args) != 1:
                raise Exception("Need 1 args")
            self.reader.xmms2base.play_next(args[0])
        else:
            Log.info("No such command: %s" % command)
            return False
        # setCustomCharacter
        return True



 

class Xmms2Reader(Thread):

    def __init__(self, service):
        Thread.__init__(self)
        self.stop = False
        #self.client = Client();
        self.service = service
        # xmms2 chains
        self.xmms2base = Xmms2Base()
        self.regeventhdl()

    def run(self):
        while not self.stop:
            self.reader()

    def reader(self):
        print "listener starting"
        while not self.stop:
            self.xmms2base.xmms.loop()
            time.sleep(delay)

    def regeventhdl(self):
        # Register callback functions:
        self.xmms2base.xmms.broadcast_playlist_current_pos(self.cb_playlist_current_pos)
        self.xmms2base.xmms.broadcast_playlist_loaded(self.cb_playlist_loaded)
        self.xmms2base.xmms.broadcast_configval_changed(self.cb_configval_changed)
        self.xmms2base.xmms.broadcast_medialib_entry_added(self.cb_medialib_entry_added)
        self.xmms2base.xmms.broadcast_medialib_entry_changed(self.cb_medialib_entry_changed)
        self.xmms2base.xmms.broadcast_playback_current_id(self.cb_playback_current_id)
        self.xmms2base.xmms.broadcast_playback_status(self.cb_playback_status)
        self.xmms2base.xmms.broadcast_playback_volume_changed(self.cb_playback_volume_changed)



## All defined callback functions from above.
#     def onEvent(self, key, value, extra):

# {('server', 'id'): 2, ('plugin/mad', 'album'): u'State Of The Arts', ('server', 'status'): 1, ('plugin/mad', 'samplerate'): 44100, ('plugin/mad', 'comment'): u'\xa0', ('server', 'added'): 1222780286, ('plugin/mad', 'date'): u'2005', ('plugin/mad', 'sample_format'): u'S16', ('plugin/file', 'lmod'): 1113922582, ('plugin/mad', 'artist'): u'Afu Ra', ('server', 'chain'): u'file:magic:mad', ('plugin/mad', 'channels'): 2, ('server', 'url'): u'file:///stash/Afu_Ra-State_Of_The_Arts-2005-CMS_iNT/14-deal_wit_it_ft._kardinal_offishall.mp3', ('plugin/mad', 'title'): u'Deal Wit It ft. Kardinal Offis', ('plugin/magic', 'mime'): u'audio/mpeg', ('server', 'timesplayed'): 18, ('server', 'laststarted'): 1223152493, ('plugin/mad', 'duration'): 289288, ('plugin/file', 'size'): 6942926, ('plugin/mad', 'genre'): u'Rap', ('plugin/mad', 'bitrate'): 192000}

    def cb_playlist_current_pos(self, val):
        # val.value() contains the playlist ID
        self.service.onEvent("PlaylistCurrentPos", val.value(),"")


    def cb_playlist_loaded(self, val):
        # val.value() contains the playlist name (string)
        print val.value()
        self.service.onEvent("PlaylistLoaded", val.value(),"")

    def cb_configval_changed(self, val):
        # unknown what this actually returns
        self.service.onEvent("ConfigvalChanged", val.value(),"")

    def cb_medialib_entry_added(self, val):
        self.service.onEvent("MedialibEntryAdded", val.value(),"")

    def cb_medialib_entry_changed(self, val):
        # val.value() contains medialib ID of song
        sid = val.get_uint()
        res = self.xmms2base.xmms.medialib_get_info(sid)
        res.wait()
        n = res.get_propdict()
        extra = {
            'artist':   n['plugin/mad', 'artist'],
            'album':    n['plugin/mad', 'album'],
            'url':  n['server', 'url']
        }
        self.service.onEvent("MedialibEntryChanged", n['plugin/mad', 'title'], extra)


    def cb_playback_current_id(self, val):
        # Ignored, cb_medialib_entry_changed used for song changes.
        # val is an int, which is the new songs medialib ID
        self.service.onEvent("PlaybackCurrentID", val.value(),"")

    def cb_playback_status(self, val):
        if val.value() == xmmsclient.PLAYBACK_STATUS_PAUSE:
            status = 'pause'
        if val.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
            status = 'play'
        if val.value() == xmmsclient.PLAYBACK_STATUS_STOP:
            status = 'stop'
        self.service.onEvent("PlaybackStatus", status,"")

    def cb_playback_volume_changed(self, val):
        # val.value(): {'right': 78L, 'left': 78L}
        vol = val.value()
        if vol['right'] == vol['left']:
            evol = vol['right']
        else:
            evol = ( vol['left'] + vol['left'] ) / 2
        self.service.onEvent("PlaybackVolume", evol,vol)
        

#class Xmms2Base(Service):
class Xmms2Base():

    def __init__(self):
        self.xmms = xmmsclient.XMMS("Xmms2Base")
        try:
            self.xmms.connect(os.getenv("XMMS_PATH"))
        except IOError,  detail:
            print "connection to xmms2d failed, restarting" 
            os.system("xmms2-launcher")
            try:
                self.xmms.connect(os.getenv("XMMS_PATH"))
            except:
                print "Restart of xmms2d failed"
                sys.exit(1)



    def regeventhdl(self):
        # Register callback functions:
        self.xmms.broadcast_playlist_current_pos(self.cb_playlist_current_pos)
        self.xmms.broadcast_playlist_loaded(self.cb_playlist_loaded)
        self.xmms.broadcast_configval_changed(self.cb_configval_changed)
        self.xmms.broadcast_medialib_entry_added(self.cb_medialib_entry_added)
        self.xmms.broadcast_medialib_entry_changed(self.cb_medialib_entry_changed)
        self.xmms.broadcast_playback_current_id(self.cb_playback_current_id)
        self.xmms.broadcast_playback_status(self.cb_playback_status)
        self.xmms.broadcast_playback_volume_changed(self.cb_playback_volume_changed)

## All defined callback functions from above.
    def cb_playlist_current_pos(self, val):
        # Ignored, cb_medialib_entry_changed used for song changes.
        # val.value() contains the playlist ID
        #print "cb_playlist_current_pos"
        #print val.value()
        self.print_event("playlist current pos", val.value())
        pass

    def cb_playlist_loaded(self, val):
        # val.value() contains the playlist name (string)
        print "cb_playlist_loaded"
        print val.value()
        self.print_event("playlist loaded", val.value())

    def cb_configval_changed(self, val):
        print "cb_configval_changed"
        print val.value()
        self.print_event("configval changed", val.value())

    def cb_medialib_entry_added(self, val):
        print "cb_medialib_entry_added"
        print val.value()
        self.print_event("medialib entry added", val.value())

    def cb_medialib_entry_changed(self, val):
        # the callback to use for song-change events.
        # val.value() contains medialib ID of song
        #print "cb_medialib_entry_changed"
        # print val.value()
        sid = val.get_uint()
        res = self.xmms.medialib_get_info(sid)
        res.wait()
        n = res.get_propdict()
        # print n
        # print res.get_propdict()
        # print "Artist: %s\nSong: %s\nAlbum: %s\nURL: %s\n" % (n['artist'],n['plugin/mad', 'title'],n['album'],n['url'])
# {('server', 'id'): 2, ('plugin/mad', 'album'): u'State Of The Arts', ('server', 'status'): 1, ('plugin/mad', 'samplerate'): 44100, ('plugin/mad', 'comment'): u'\xa0', ('server', 'added'): 1222780286, ('plugin/mad', 'date'): u'2005', ('plugin/mad', 'sample_format'): u'S16', ('plugin/file', 'lmod'): 1113922582, ('plugin/mad', 'artist'): u'Afu Ra', ('server', 'chain'): u'file:magic:mad', ('plugin/mad', 'channels'): 2, ('server', 'url'): u'file:///stash/Afu_Ra-State_Of_The_Arts-2005-CMS_iNT/14-deal_wit_it_ft._kardinal_offishall.mp3', ('plugin/mad', 'title'): u'Deal Wit It ft. Kardinal Offis', ('plugin/magic', 'mime'): u'audio/mpeg', ('server', 'timesplayed'): 18, ('server', 'laststarted'): 1223152493, ('plugin/mad', 'duration'): 289288, ('plugin/file', 'size'): 6942926, ('plugin/mad', 'genre'): u'Rap', ('plugin/mad', 'bitrate'): 192000}

        self.print_event("New song", n['plugin/mad', 'title'])


    def cb_playback_current_id(self, val):
        # Ignored, cb_medialib_entry_changed used for song changes.
        # val is an int, which is the new songs medialib ID
        #print "cb_playback_current_id"
        #print val.value()
        self.print_event("playback_current_id", val.value())
        pass

    def cb_playback_status(self, val):
        #print "cb_playback_status"
        if val.value() == xmmsclient.PLAYBACK_STATUS_PAUSE:
            status = 'pause'
        if val.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
            status = 'play'
        if val.value() == xmmsclient.PLAYBACK_STATUS_STOP:
            status = 'stop'
        self.print_event("playback status changed", status)

    def cb_playback_volume_changed(self, val):
        # val.value(): {'right': 78L, 'left': 78L}
        # print "cb_playback_volume_changed"
        vol = val.value()
        right = "right: %d" % (vol['right'])
        left = "left: %d" % (vol['left'])
        both = right + ' - ' + left
        self.print_event("volume changed", both)



    # jukx basic functions below

    def check_err(self, res):
        if res.iserror():
            print res.get_error()

    def play(self):
        res = self.xmms.playback_start()
        res.wait()
        self.check_err(res)

    def stop(self):
        res = self.xmms.playback_stop()
        res.wait()
        self.check_err(res)

    def pause(self):
        res = self.xmms.playback_pause()
        res.wait()
        self.check_err(res)

    def clear(self):
        res = self.xmms.playlist_clear()
        res.wait()
        self.check_err(res)

    def next(self):
        res = self.xmms.playlist_set_next_rel(+1)
        res.wait()
        self.check_err(res)
        self.tickle()

    def play_next(self, id):
        res = self.xmms.playlist_set_next(id)
        res.wait()
        self.check_err(res)
        self.tickle()

    def prev(self):
        res = self.xmms.playlist_set_next_rel(-1)
        res.wait()
        self.check_err(res)
        self.tickle()

    def get_volume(self):
        res = self.xmms.playback_volume_get()
        res.wait()
        self.check_err(res)
        res = res.value()
        (l, r)=res['left'], res['right']
        return (l, r)

    def set_volume(self, left, right):
        res = self.xmms.playback_volume_set('left',  left)
        res2 = self.xmms.playback_volume_set('right',  right)
        res.wait()
        res2.wait()
        self.check_err(res)
        self.check_err(res2)

    def voldown(self):
        left, right = self.get_volume()
        if left-self.volstep <= 0 or right-self.volstep <= 0:
            self.set_volume(5, 5)
            return
        self.set_volume(left-self.volstep, right-self.volstep)


    def volup(self, widget):
        left, right = self.get_volume()
        if left+self.volstep >= 100 or right+self.volstep >= 100:
            self.set_volume(100, 100)
            return
        self.set_volume(left+self.volstep, right+self.volstep)

    def add_idtopls(self,id):
        res = self.xmms.playlist_add_id(id)
        res.wait()
        self.check_err(res)

    def tickle(self):
        res = self.xmms.playback_tickle()
        res.wait()
        self.check_err(res)

    def set_chghdl(self, status_handler, pos_handler):
        self.xmms.broadcast_playback_status(status_handler)
        self.xmms.broadcast_playlist_current_pos(pos_handler)

    def get_current_id(self):
        res =  self.xmms.playback_current_id()
        res.wait()
        self.check_err(res)
        id = res.get_uint()
        return id

    def get_current_pos(self):
        res = self.xmms.playlist_current_pos()
        res.wait()
        self.check_err(res)
        return res.value()

    def get_current_value(self):
        return self.get_value(self.xmms.playback_current_id())

    def get_value(self, id):
        curInfo = self.xmms.medialib_get_info(id)
        curInfo.wait()
        if not curInfo.iserror():
            return curInfo.value()
        else:
            return None

    def get_current_list(self):
        res = self.xmms.playlist_list_entries()
        res.wait()
        self.check_err(res)
        return res.get_list()

    def get_current_mode(self):
        res = self.xmms.playback_status()
        res.wait()
        self.check_err(res)
        return res

    def get_coll_ids(self, collection):
        res = self.xmms.coll_query_ids(collection)
        res.wait()
        self.check_err(res)
        return res.value()

    def get_coll_values(self, collection, fields):
        res = self.xmms.coll_query_infos(collection, fields)
        res.wait()
        self.check_err(res)
        return res.value()

    def get_bindata(self, hash):
        res = self.xmms.bindata_retrive(hash)
        res.wait()
        self.check_err(res)
        return res.get_bin()

    def create_aa_coll(self, artist, album):
        artistmatch = xmmsclient.xmmsapi.Match(field='artist', value=artist)
        albummatch = xmmsclient.xmmsapi.Match(field='album', value=album)
        coll = xmmsclient.xmmsapi.Collection.__and__(artistmatch, albummatch)
        return coll

    def listener(self,delay):
        print "listener starting"
        while True:
            self.xmms.loop()
            time.sleep(delay)
            #btdevs = self.getservices()
            # print btdevs
            #if len(btdevs) > 0:
            #    for mac in btdevs:
            #time.sleep(delay)

    def print_event(self, type, value):
        print "|%20s|%20s|%25s|" % ("XMMS", type, value)
        line = "|%20s|%20s|%25s|" % ("--------------------", "--------------------", "-------------------------")
        print line


def main():
    import getopt, sys
    # print "I was not imported"
    def usage():
        print sys.argv[0] + ' [--help | --verbose | --scan | --listen <scan-frequency>]'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvl:", ["help","verbose","listen"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
           usage()
           sys.exit(0)
        elif o in ("-l", "--listen"):
            test = Xmms2Base()
            test.regeventhdl()
            test.listener(float(a))
        elif o in ("-v", "--verbose"):
            print 'verbose'


if __name__ == "__main__":
    main()
else:
    print "I was imported"
    print __name__

