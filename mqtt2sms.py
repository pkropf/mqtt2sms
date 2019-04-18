#!/usr/bin/env python3.7

import paho.mqtt.client as mqtt
import json
import configparser
import gammu
import os
import time
import logging
import sys

class SMSGateway(object):
    def __init__(self):
        self.sm = gammu.StateMachine()
        self.sm.ReadConfig(Filename='/etc/gammurc')
        self.sm.Init()

    def send(self, text, number):
        message = {
            'Text': '%s' % text,
            'SMSC': {'Location': 1},
            'Number': '%s' % number,
        }

        try:
            self.sm.SendSMS(message)
            print("sending SMS to %s with text %s" % (number, text), file=sys.stdout)
            return True
        except Exception as e:
            print("SMS sending failed: %s" % e, file=sys.stderr)
            return False

class MQTTSMSListener(mqtt.Client):
    def on_message(self, mqttc, obj, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            message = data.get('message', None)
            if not message:
                print('no message body to send', file=sys.stderr)
                return False

            number = data.get('number', None)
            if not number:
                print('no number to send to', file=sys.stderr)
                return False
            self.sms.send(message, number)
        except Exception as e:
            print('failed to decode JSON, reason: %s, string: %s' % (e, msg.payload), file=sys.stderr)

    def run(self):
        self.sms = SMSGateway()
        mqttconf = configparser.ConfigParser()
        mqttconf.read('/etc/mqtt.ini')
        self.username_pw_set(
            mqttconf.get('mqtt', 'user'),
            mqttconf.get('mqtt', 'password')
        )

        self.connect(
            mqttconf.get('mqtt', 'host'),
            mqttconf.getint('mqtt', 'port'),
            60
        )
        self.subscribe("sms")

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


mqttc = MQTTSMSListener(clean_session=True)
rc = mqttc.run()
