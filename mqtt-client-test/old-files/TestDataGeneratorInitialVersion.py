#!/usr/bin/env python3
import datetime
import json
import logging
import random
import sys
import threading
import time
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
#c_sw = boto3.client('iotsitewise')

class TestDataGenerator(object):
    @staticmethod
    def generate_json_data(generator_num, powerValue, temperature, rpm, qualityValue):
        tag_alias = '/DayOneEnergyCorp/{}/Generator/Power'.format(generator_num)
        messages = []
        measurements = {}
        measurements['name'] = tag_alias
        measurements['value'] = powerValue
        measurements['timestamp'] = int(time.time() * 1000)
        measurements['quality'] = qualityValue
        messages.append(measurements)

        finaldataset = {}
        finaldataset['alias'] = tag_alias
        finaldataset['messages'] = messages

        return json.dumps(finaldataset)

    @staticmethod
    def gen_generator_data(generator_num, sleep_intervall):
            power = random.randint(17, 27)
            temperature = random.randint(20, 25)
            rpm = random.randint(90, 130)
            quality = 'GOOD'
            seed = random.randint(1,10)
            logger.info("seed: {}".format(seed))
            if seed == 3 or seed == 6:
                power = random.randint(0, 10)
                temperature = random.randint(35, 45)
                rpm = random.randint(50, 70)
                quality = 'BAD'
            elif seed == 7:
                power = random.randint(10, 15)
                temperature = random.randint(25, 35)
                rpm = random.randint(190, 210)
                quality = 'UNCERTAIN'
            power = float(power)
            temperature = float(temperature)
            rpm = float(rpm)

            #print("generator_num: {} power: {} temperature: {} rpm: {} quality: {}".format(generator_num, power, temperature, rpm, quality))

            return TestDataGenerator.generate_json_data(generator_num, power, temperature, rpm, quality)

if __name__ == '__main__':
    print(TestDataGenerator.gen_generator_data(2,30))

