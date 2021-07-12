#!/usr/bin/env python3
import json
import time
import logging.config
import random as rand
from random import *
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import threading
import configparser
import pathlib
import traceback

logging.config.fileConfig(fname='config/log.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

file = pathlib.Path('config/conf.cfg')
config = configparser.ConfigParser()

if file.exists ():
    config.read(file)
else:
    logger.error("Config file: {} does not exists, please check if the file exists or not.".format(file))
    exit(1)

CERTS_PATH = config.get('mqtt-settings', 'CERTS_PATH')
host = config.get('mqtt-settings', 'host')
port = config.getint('mqtt-settings', 'port')
group_root_ca_file = config.get('mqtt-settings', 'group_root_ca_file')
certificate_file = config.get('mqtt-settings', 'certificate_file')
privatekey_file = config.get('mqtt-settings', 'privatekey_file')
clientId = config.get('mqtt-settings', 'clientId')
topic = config.get('mqtt-settings', 'topic')

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(CERTS_PATH+"/"+group_root_ca_file, CERTS_PATH+"/"+privatekey_file, CERTS_PATH+"/"+certificate_file)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

try:
    myAWSIoTMQTTClient.connect()
except BaseException as e:
    logger.error(e, exc_info=True)
except:
    logger.error("Exception while establishing the client connection: %s", traceback.format_exc())

class TestDataGenerator(object):
    @staticmethod
    def generate_measurement_for_an_asset(organization_name, location, asset_type, asset_unique_num, measurement_name, measurement_value, quality_value, recorded_time):
        equipment_tag_alias = "/" + str(organization_name) + "/" +  str(location) + "/" + str(asset_type) + "/" + str(asset_unique_num) + "/" + str(measurement_name)
        #print("tag is ::: {}".format(equipment_tag_alias))
        messages = []
        measurements = {
            'name': equipment_tag_alias,
            'value': measurement_value,
            'timestamp': recorded_time,
            'quality': quality_value
        }
        messages.append(measurements)

        payload = {
            'alias': equipment_tag_alias,
            'messages': messages
        }
        logger.debug("Json payload message is :: {}".format(json.dumps(payload)))
        return json.dumps(payload)

    @staticmethod
    def wrapper_data_generator(sleep_interval):
        global config
        for k in range(5000):
            #for k in range(50):
            power = rand.randint(17, 27)
            temperature = rand.randint(20, 25)
            rpm = rand.randint(90, 130)
            quality = 'GOOD'
            seed = rand.randint(1,10)
            #logger.info("seed: {}".format(seed))
            if seed == 3 or seed == 6:
                power = rand.randint(0, 10)
                temperature = rand.randint(35, 45)
                rpm = rand.randint(50, 70)
                quality = 'BAD'
            elif seed == 7:
                power = rand.randint(10, 15)
                temperature = rand.randint(25, 35)
                rpm = rand.randint(190, 210)
                quality = 'UNCERTAIN'
            power = float(power)
            temperature = float(temperature)
            rpm = float(rpm)
            timestamp_value = int(time.time() * 1000)
            corp_name = config.get('organization', 'name')
            location_value = config.get('organization', 'plant-location')

            prop = config.items("equipments")
            equipment_type_values = list(dict(prop).values())
            equipment_type = rand.choice(tuple(equipment_type_values))
            logger.debug("Selected equipment type is: {}".format(equipment_type))

            model_asset_alias_mappings = dict(config.items(equipment_type+"-asset-alias-mappings"))
            measurements_list = list(model_asset_alias_mappings.values())

            # Todo: in future we need to generate these values based on the equipment type that we selected.
            # Todo: For gernerator, we might have 3 attributes and for hvac, we might have different values and attributes.
            # Todo: For simiplicity, we will assume both equipments has the same number of properties.
            measurement_values_list = [power, temperature, rpm]

            asset_uniq_num = randint(0, 99)
            for measurement, measurement_value in zip(measurements_list, measurement_values_list):
                result_payload = TestDataGenerator.generate_measurement_for_an_asset(corp_name, location_value, equipment_type, asset_uniq_num, measurement,  measurement_value, quality, timestamp_value)
                logger.info("Resultant message is : {}".format(result_payload))
                myAWSIoTMQTTClient.publish(topic, result_payload, 0)
                time.sleep(0.1)
            logger.debug("sleeping for 1 second")
            time.sleep(sleep_interval)
            k += 1

if __name__ == '__main__':
    #for i in range(4):
    for i in range(2):
        t = threading.Thread(target=TestDataGenerator.wrapper_data_generator, args=(1,))
        t.start()