#!/usr/bin/python

import sys
import time
# import smtplib, poplib, re
import poplib
import email
from email.mime.text import MIMEText

from chains.service import Service
from chains.common import log

# Events:
# * new mail


class MailService(Service):

    def onInit(self):
        self.from_addr = self.config.get('from_addr')
        self.to_addr = self.config.get('to_addr')
        if not self.to_addr:
            self.to_addr = self.from_addr
        self.username = self.config.get('username')
        self.password = self.config.get('password')
        self.polldelay = self.config.get('polldelay')
        if not self.polldelay:
            self.polldelay = 600
        self.mailserver = self.config.get('mailserver')
        if not self.mailserver:
            self.mailserver = '127.0.0.1'
        self.smtpserver = self.config.get('smtpserver')
        self.deletemail = self.config.get('deletemail')
        if not self.deletemail or not self.deletemail.lower() == 'yes' or not self.deletemail.lower() == 'true':
            self.deletemail = False
        self.maxheaders = self.config.get('maxheader')
        if not self.maxheaders:
            self.maxheaders = 10
        self.maxsize = self.config.get('maxsize')
        if not self.maxsize:
            self.maxsize = 12000
        if not self.smtpserver:
            self.smtpserver = '127.0.0.1'
        if not self.from_addr:
            log.warn('Service needs senders email address to work.')
            sys.exit(1)

    def onStart(self):
        while not self._shutdown:
            if self.username and self.password and self.mailserver:
                self._check_mail()
            time.sleep(float(self.polldelay))

    def _check_mail(self):
        # Add support for IMAP
        try:
            pop = poplib.POP3(self.mailserver)
            pop.user(self.username)
            pop.pass_(self.password)
            stat = pop.stat()
            # log.info('Hande %s mails' % stat[0])
            # print stat
            for n in range(stat[0]):
                msgnum = n + 1
                hresponse, hlines, bytes = pop.top(msgnum, self.maxheader)
                # print "response: " + hresponse
                # print "lines: " + str(hlines)
                # print lines[len(lines)-1]
                # print "bytes: " + str(bytes)
                mailto = mailfrom = subject = 'unknown'
                if bytes < self.maxsize:
                    mresponse, mlines, bytes = pop.retr(msgnum)
                    mailstring = ''
                    for i in mlines:
                        mailstring += i
                        mailstring += '\n'
                    msg = email.message_from_string(mailstring)
                    # print msg
                    if 'To' in msg:
                        mailto = msg['To']
                    if 'From' in msg:
                        mailfrom = msg['From']
                    if 'Subject' in msg:
                        subject = msg['Subject']
                    log.info('Handle msg with proper size: %s | %s | %s' % (mailfrom, mailto, subject))
                    # heads = msg.keys()
                    # for head in heads:
                    #    print head + '\n'
                    parts = 0
                    multipart = ''
                    for part in msg.walk():
                        # print "type", repr(part.get_content_type())
                        multipart += 'Part ' + str(parts + 1) + ":" + repr(part.get_content_type())
                        multipart += '\n'
                        # print "body", repr(part.get_payload())
                        body = repr(part.get_payload())
                        parts += 1
                    if parts > 1:
                        body = multipart
                    self.sendEvent(mailfrom, {'to': mailto, 'subject': subject, 'message': body})
                else:
                    mailstring = ''
                    for i in hlines:
                        mailstring += i
                        mailstring += '\n'
                    msg = email.message_from_string(mailstring)
                    # print msg
                    if 'To' in msg:
                        mailto = msg['To']
                    if 'From' in msg:
                        mailfrom = msg['From']
                    if 'Subject' in msg:
                        subject = msg['Subject']
                    log.info('Ignore body for mail with size above mailbase.maxsize: %s | %s | %s' % (mailfrom, mailto, subject))
                    self.sendEvent(mailfrom, {'to': mailto, 'subject': subject, 'message': 'LARGE_MAIL_BODY_IGNORED'})
                if self.deletemail:
                    pop.dele(msgnum)
            pop.quit()
        except poplib.error_proto, detail:
            log.error("POP3 Protocol Error:", detail)

    def action_sendmail(self, from_addr=None, to_addr=None, subject=None, message=None):
        '''
        Send an email
        @param  from_addr     string   Address to send from
        @param  to_addr     string   Address to send to
        @param  subject     string   Subject of the message
        @param  message     string   Text message you want to send
        '''
        msg = MIMEText(str(message))
        msg['To'] = email.utils.formataddr(('Recipient', self.to_addr))
        msg['From'] = email.utils.formataddr(('Chains', self.from_addr))
        msg['Subject'] = self.subject
        log.info('Send msg: %s' % msg)
        server = smtplib.SMTP(self.smtpserver)
        # TODO: Implement authenticated smtp
        try:
            server.sendmail(from_addr, [to_addr], msg.as_string())
        except:
            log.error("Sending mail failed")

    def action_checkmail(self):
        '''
        Check email account
        '''
        self._check_mail()
