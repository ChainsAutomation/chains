import threading
import sys
import traceback
import time
# chains
from chains.device import Device
from chains.log import log
from chains import utils
from chains import config
from chains.com.client import Client
###################
# spotify
# Using pyspotify
# depends on libspotify
import spotify
try:
    from spotify.alsahelper import AlsaController
except ImportError:
    from spotify.osshelper import OssController as AlsaController
from spotify import Link

##### Spotify lib:
# spotify:
##  ['Album', 'Artist', 'Link', 'Playlist', 'PlaylistContainer', 'Results', 'Session', 'SpotifyError', 'Track', '_spotify', 'alsahelper', 'api_version', 'connect']

## spotify.Album: 
###  ['ALBUM', 'COMPILATION', 'SINGLE', 'UNKNOWN', 'artist', 'cover', 'is_available', 'is_loaded', 'name', 'type', 'year']

## spotify.Artist: 
###  ['is_loaded', 'name']

## spotify.Link: 
###  ['LINK_ALBUM', 'LINK_ARTIST', 'LINK_INVALID', 'LINK_PLAYLIST', 'LINK_SEARCH', 'LINK_TRACK', 'as_album', 'as_artist', 'as_track', 'from_album', 'from_artist', 'from_playlist', 'from_search', 'from_string', 'from_track', 'type']

## spotify.Playlist: 
###  ['add_tracks_added_callback', 'add_tracks_moved_callback', 'add_tracks_removed_callback', 'is_collaborative', 'is_loaded', 'name', 'remove_tracks']

## spotify.Track:  
###  ['album', 'artists', 'disc', 'duration', 'error', 'index', 'is_loaded', 'name', 'popularity']

# session object:
## dir(session):[ 
##    'display_name', 'image_create', 'is_available', 'load', 'logout', 'play', 'playlist_container',
#    'process_events', 'search', 'seek', 'set_preferred_bitrate', 'user_is_loaded', 'username']


class SpotCtrlDevice(Device):

### chains stuff
 
    def open(self):
        print "def open(self):"

        self.api_version = spotify.api_version
        self.cache_location = '/tmp'
        self.settings_location = '/tmp'
        self.application_key = None
        self.appkey_file = 'spotify_appkey.key'
        self.user_agent = 'chains'

        if self.application_key is None:
            self.classdata= config.getDeviceSharePath(self.config['main']['class']) + '/'
            self.application_key = open(self.classdata + self.appkey_file).read()
        self.awoken = threading.Event() # used to block until awoken
        self.timer = None
        self.finished = False
        self.session = None

        self.username = 'anonymous'
        try: self.username = self.config['main']['username']
        except KeyError:
            log.warn('No "username" in %s device config, using %s' % (self.config['id'], self.username))
        self.password = 'password'
        try: self.password = self.config['main']['password']
        except KeyError:
            log.warn('No "password" in %s device config, using %s' % (self.config['id'], self.password))
        self.audio = AlsaController()
        self.ctr = None
        self.playing = False
        self._queue = []
        print "Logging in, please wait..."
        self.connect()
        print "Finished connecting?"

    def onDescribe(self):
        return {
            'info': '',
            'commands': [
                ('quit', [], 'Quit spotify'),
                ('lists', [], 'List playlists'),
                ('list', [('listnr','int',None,'Playlist number')], 'List contents of playlist'),
                ('play', [], 'Play'),
                ('stop', [], 'Stop'),
                ('next', [], 'Next track'),
                ('load', [('listnr','int',None,'Playlist number'),('track','int',None,'Track number')], 'Load track from playlist'),
                ('load_track', [('track','str',None,'spotify url or playlist id')], 'Load spotify url or playlist id'),
                ('queue', [], 'List queue'),
                ('queue_track', [('listnr','int',None,'Playlist number'),('tracknr','int',None,'Track number')], 'Add track to queue'),
                ('set_bitrate', [('bitrate','str',['normal','high'])], 'Set bitrate to normal or high'),
                #   Simple: ('mycommand', [('arg1','str'), ('arg2','int')])
                # Advanced: ('mycommand', [('arg1','str',None,'Arg1 - a string'), ('arg2','int',[3,4],'Arg2 - an int, either 3 or 4')], 'My command description')
            ],
            'events': [
                # ('myevent', ('key','str',['mykey1','mykey2'],'event.key = mykey1 or mykey2'), ('value','bool') ),
            ],
        }

    def onEvent(self, key, value, extra):
        evt = {
            'device': self.config['id'],
            'key': key,
            'value': value,
            'extra': extra
        }
        self.devDaemon.onEvent(evt)
 
    def cmd_quit(self, line):
        print "Goodbye!"
        self.terminate()
        return True

    def cmd_lists(self):
        """ List the playlists """
        extra = {}
        for i, p in enumerate(self.ctr):
            if p.is_loaded():
                print "%3d %s" % (i, p.name())
                extra.update({i: p.name()})
            else:
                print "%3d %s" % (i, "loading...")
                extra.update({i: "loading..."})
        self.onEvent('playlists',len(extra),extra)
#        return extra

    def cmd_list(self, listid):
        """ List the contents of a playlist """
        extra = {}
        try:
            p = int(listid)
        except ValueError:
            print "that's not a number!"
            return False
        if p < 0 or p > len(self.ctr):
            print "That's out of range!"
            return False
        print "Listing playlist #%d" % p
        for i, t in enumerate(self.ctr[p]):
            if t.is_loaded():
                print "%3d %s" % (i, t.name())
                extra.update({i: t.name()})
            else:
                print "%3d %s" % (i, "loading...")
                extra.update({i: 'loading...'})
        self.onEvent('playlist',listid,extra)
#        return extra

    def cmd_play(self):
        self.play()
        self.onEvent('status','playing',{})
        return True

    def cmd_load_track(self, track, playlist=None):
        extra = {}
        if track.startswith("spotify:"):
            # spotify url
            l = Link.from_string(track)
            if not l.type() == Link.LINK_TRACK:
                print "You can only play tracks!"
                return False
            self.load_track(l.as_track())
            extra.update({'type':'link', 'playlist':'link'})
        elif playlist != None:
            #print "Usage: play [track_link] | [playlist] [track]"
            self.load(playlist, track)
            extra.update({'type':'playlistmember', 'playlist':playlist})
        self.play()
        self.onEvent('playing',track,extra)

    def cmd_search(self, line):
        if not line:
            if self.results is False:
                print "No search is in progress"
                return False
            elif self.results is None:
                print "Searching is in progress"
            else:
                print "Artists:"
                for a in self.results.artists():
                    print "    ", Link.from_artist(a), a.name()
                print "Albums:"
                for a in self.results.albums():
                    print "    ", Link.from_album(a), a.name()
                print "Tracks:"
                for a in self.results.tracks():
                    print "    ", Link.from_track(a, 0), a.name()
                print self.results.total_tracks() - len(self.results.tracks()), "Tracks not shown"
                self.results = False
        else:
            self.results = None
            def _(results, userdata):
                print "\nSearch results received"
                self.results = results
            self.search(line, _)

    def cmd_queue(self):
        extra = {}
        for playlist, track in self._queue:
            print playlist, track
            extra.update({'playlist':playlist, 'trackid':track})
        self.onEvent('list','queue',extra)
        return

    def cmd_queue_track(self, playlist, track):
        try:
            playlist, track = map(int, line.split(' ', 1))
        except ValueError:
            print "Usage: play playlist track"
            return
        self.queue(int(playlist), int(track))

    def cmd_stop(self):
        self.stop()

    def cmd_next(self):
        self.next()

    def cmd_set_bitrate(self, bitrate):
        self.bitrate(bitrate)

    def cmd_load(self,playlist,track):
        self.load(int(playlist),int(track))

    def cmd_load_tack(self,track):
        self.load(int(track))


## spotify main loop etc
############

    def connect(self):
        print "def connect(self)"
        sess = spotify.connect(self)
        print str(sess)
        self.sesson = sess
        self.loop(sess) # returns on disconnect

    def loop(self, sess):
        """ The main loop. This processes events and then either waits for an
        event. The event is either triggered by a timer expiring, or by a
        notification from within the spotify subsystem (it calls the wake
        method below). """
        print "def loop(self, sess)"
        while not self.finished:
            print "Main loop"
            self.awoken.clear()
            timeout = sess.process_events()
            print "timeout: %s" % str(timeout)
            self.timer = threading.Timer(timeout/1000.0, self.awoken.set)
            self.timer.start()
            self.awoken.wait()

    def terminate(self):
        self.finished = True
        self.wake()

    disconnect = terminate

    def wake(self, sess=None):
        """ This is called by the spotify subsystem to wake up the main loop. """
        print "def wake(self, sess=None):"
        if self.timer is not None:
            self.timer.cancel()
        self.awoken.set()

# spotify callbacks
    def logged_in(self, session, error):
        print "CALLBACK: logged_in(self, session, error): (%s,%s)" % (str(session), str(error))
        self.session = session
        """
        try:
            print "session.username:" + str(self.session.username())
        except Exception, e:
            print "FAILED: session.username(): " + str(e)
        try:
            print "session.user_is_loaded:" + str(self.session.user_is_loaded())
        except Exception, e:
            print "FAILED: session.user_is_loaded(): " + str(e)
        try:
            print "session.display_name:" + str(self.session.display_name())
        except Exception, e:
            print "FAILED: session.display_name(): " + str(e)
        """
        if error > 1:
            return
        try:
            self.ctr = self.session.playlist_container()
        except:
            print "FAIL: self.ctr = session.playlist_container()"
            traceback.print_exc()

#    def logged_in(self, session, error):
#        """ Called when the user has successfully logged in. You almost
#        certainly want to do something with session.playlist_container() at
#        this point. """
#        pass

    def logged_out(self, sess):
        print "CALLBACK: def logged_out(self, sess):"
        pass

    def metadata_updated(self, sess):
        print "CALLBACK: def metadata_updated(self, sess): CallBack"
        pass

    def connection_error(self, sess, error):
        print "CALLBACK: def connection_error(self, sess, error): %s" % str(error)
        pass

    def message_to_user(self, sess, message):
        print "CALLBACK: def message_to_user(self, sess, message): %s" % str(message)
        pass

    def notify_main_thread(self, sess):
        print "CALLBACK: def notify_main_thread(self, sess):"
        pass

    def music_delivery(self, sess, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        print "CALLBACK: def music_delivery(self, sess, frames, frame_size, num_frames, sample_type, sample_rate, channels):"
        pass

    def play_token_lost(self, sess):
        print "CALLBACK: def play_token_lost(self, sess):"
        pass

    def log_message(self, sess, data):
        print "CALLBACK: def log_message(self, sess, data): %s" % str(data)
        pass

    def end_of_track(self, sess):
        print "CALLBACK: def end_of_track(self, sess):"
        pass


# spotify functions
    def load(self, playlist, track):
        if self.playing:
            self.stop()
        self.session.load(self.ctr[playlist][track])
        print "Loading %s from %s" % (self.ctr[playlist][track].name(), self.ctr[playlist].name())

    def load_track(self, track):
        if self.playing:
            self.stop()
        self.session.load(track)
        print "Loading %s" % track.name()

    def queue(self, playlist, track):
        if self.playing:
            self._queue.append((playlist, track))
        else:
            self.load(playlist, track)
            self.play()

    def play(self):
        self.session.play(1)
        print "Playing"
        self.playing = True

    def stop(self):
        self.session.play(0)
        print "Stopping"
        self.playing = False

    def music_delivery(self, *a, **kw):
        return self.audio.music_delivery(*a, **kw)

    def next(self):
        self.stop()
        if self._queue:
            t = self._queue.pop()
            self.load(*t)
            self.play()
        else:
            self.stop()

    def end_of_track(self, sess):
        print "track ends."
        self.next()

    def search(self, query, callback):
        self.session.search(query, callback)

    def bitrate(self, bitrate):
        if bitrate == 'normal':
            self.session.set_preferred_bitrate(0)
        elif bitrate == 'high':
            self.session.set_preferred_bitrate(1)


#if __name__ == '__main__':
#    print "main"
#    t = SpotTest('chrisaq','various1')
#    print "connecting"
#    t.connect()
#    print "connected"



