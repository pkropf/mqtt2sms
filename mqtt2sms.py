#! /usr/bin/env python3.7

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
            logging.info(f"sending SMS to {number} with text {text}")
            return True
        except Exception as e:
            logging.error(f"SMS sending failed: {e}")
            return False


class MQTTSMSListener(mqtt.Client):
    def on_message(self, mqttc, obj, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"), strict=False)
            message = data.get('message', None)
            if not message:
                logging.error('no message body to send')
                return False

            number = data.get('number', None)
            if not number:
                logging.error('no number to send to')
                return False
            self.sms.send(message, number)
            logging.info(f'message sent')
        except Exception as e:
            logging.error(f'failed to decode JSON, reason: {e}, string: {msg.payload}')

    def run(self):
        self.sms = SMSGateway()
        mqttconf = configparser.ConfigParser()
        ini_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mqtt2sms.ini')
        mqttconf.read(ini_file)

        logging.basicConfig(filename=mqttconf.get('general', 'logfile'), level=logging.DEBUG)

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

        logging.info('MQTTSMSListener running')
        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


mqttc = MQTTSMSListener(clean_session=True)
rc = mqttc.run()
