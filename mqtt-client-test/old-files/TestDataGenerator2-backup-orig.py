#!/usr/bin/env python3
import random
import json
import time
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import threading
import configparser
import pathlib

file = pathlib.Path('config/conf.cfg')

main_asset_model_properties = []
config = configparser.ConfigParser()
if file.exists ():
    config.read(file)
else:
    print("Config file does not exists.")
    exit(1)

CERTS_PATH = "/home/ubuntu/iot_certs"
host = "172.31.89.146"
port = 8883
root_ca_file = "root.ca.pem"
group_root_ca_file = "39408ebe-c8e4-4c9a-94d8-e180458a9881_CA_9d32335a-405d-4f90-bbbb-3ff892e27024.crt"
certificate_file = "7886c128ea.cert.pem"
privatekey_file = "7886c128ea.private.key"
clientId = "MQTT_Publisher_Thing"
thingName = "MQTT_Publisher_Thing"
topic = "/send/to/sitewise/edge"

# Configure logging
logger = logging.getLogger("device-mqtt-test.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(CERTS_PATH+"/"+group_root_ca_file, CERTS_PATH+"/"+privatekey_file, CERTS_PATH+"/"+certificate_file)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

try:
    myAWSIoTMQTTClient.connect()
except BaseException as e:
    print("Error in connect!")
    print("Type: %s" % str(type(e)))
    print("Error message: %s" % e.message)

class TestDataGenerator(object):
    @staticmethod
    def generate_measurement_for_an_asset(organization_name, asset_type, asset_unique_num, measurement_name, measurement_value, quality_value, recorded_time):
        equipment_tag_alias = "/" + str(organization_name) + "/" +  str(asset_type) + "/" + str(asset_unique_num) + "/" + str(measurement_name)
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
        #print("json payload message is :: {}".format(json.dumps(payload)))
        return json.dumps(payload)

    @staticmethod
    def wrapper_data_generator(asset_uniq_num, sleep_intervall):
        for k in range(100):
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
            timestamp_value = int(time.time() * 1000)
            corp_name = "DayOneEnergyCorp"
            asset_type = "Generator"
            measurements_list = ["Power", "Temperature", "Rpm"]
            measurement_values_list = [power, temperature, rpm]

            for measurement, measurement_value in zip(measurements_list, measurement_values_list):
                result_payload = TestDataGenerator.generate_measurement_for_an_asset(corp_name, asset_type, asset_uniq_num, measurement,  measurement_value, quality, timestamp_value)
                #print("send to mqtt broker....")
                print("resultant message is : {}".format(result_payload))
                myAWSIoTMQTTClient.publish(topic, result_payload, 0)
                time.sleep(0.1)
            print("sleeping for 1 min")
            time.sleep(sleep_intervall)
            k += 1
        #print("generator_num: {} power: {} temperature: {} rpm: {} quality: {}".format(generator_num, power, temperature, rpm, quality))

if __name__ == '__main__':
    for i in range(3):
        t = threading.Thread(target=TestDataGenerator.wrapper_data_generator, args=(i,1,))
        t.start()

