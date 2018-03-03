from __future__ import absolute_import
from __future__ import print_function
from chains.common import log
import threading

# RuleRunner
#
# Helper that handles running the rule generator
#
# Checks if incoming event matches next event in rule,
# and if so iterates to next in the generator, causing
# it to run its next action(s) and yield the next event.
#
# The iterate-to-next step is run in a thread to ensure
# long running actions do not block handling of events
# that occur in the meantime.
#


class RuleRunner:

    def __init__(self, id, context, rule, parentOnComplete):

        self.id = id
        self.isComplete = False
        self.context = context

        self.debug('Init RuleRunner')

        self.event = None                     # The event(s) we're waiting for to proceed, or None when running actions
        self.matchedEvent = None              # The last event we matched
        self.thread = None                    # Thread to run actions (ie. non-event) steps in
        self.rule = rule.rule(self.context)   # The rule itself (ie. the generator function)
        self.onComplete = []                  # List of callbacks to run when rule is done

        try:
            self.onComplete.append((rule.onComplete, [self.context]))
        except AttributeError:
            pass

        if parentOnComplete:
            self.onComplete.append((parentOnComplete, [self]))

        self.getNext()

    # Handle occurring events
    def onEvent(self, event):

        # If we're not waiting for an event, we're running actions or we're done
        if not self.event:
            self.debug('Event ignored since not waiting for event: %s' % event)
            return

        # If event matches what we're waiting for, iterate to next step in rule
        self.debug('Event match attempt:', event)
        if event.match(self.event):
            self.info('Event matched:', event)
            self.matchedEvent = event                            # Need this in getNext to pass it to rule
            self.event = None                                    # While running actions, we're not waiting for events
            self.thread = threading.Thread(target=self.getNext)  # Don't block when running actions
            self.thread.daemon = True
            self.thread.start()

    # Called once the rule is complete
    def complete(self):
        self.info('Rule completed')
        self.event = None
        self.isComplete = True
        if self.onComplete:
            for callback, args in self.onComplete:
                callback(*args)

    # Go to next event in rule
    def getNext(self):
        try:
            # Iterate to next step in rule, running any actions in between
            if self.matchedEvent:
                self.event = self.rule.send(self.matchedEvent)
            else:
                self.event = next(self.rule)
            # Rule is done running actions, and we're waiting for an event again
            self.debug('Wait for event(s):', self.event)
        # No more events? Then we're done.
        except StopIteration:
            self.complete()
        # Hm, unsure if this works.
        # There are definitively at least some cases where thread can die
        # without us noticing. So make sure code in Action() is ok.
        except Exception as e:
            log.error("Rule crashed: %s :" % self.id, e)
            self.complete()

    # Wait for action-thread to complete (used for tests)
    def wait(self):
        if self.thread:
            self.thread.join()

    def debug(self, msg, data=None):
        log.debug("RuleRunner: #%s: %s" % (self.id, msg), data)

    def info(self, msg, data=None):
        log.info("RuleRunner: #%s: %s" % (self.id, msg), data)
