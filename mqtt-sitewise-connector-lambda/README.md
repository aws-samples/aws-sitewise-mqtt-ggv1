## Create an AWS IoT Greengrass lambda function that collects the data stream from Greengrass core’s MQTT broker and sends to AWS IoT Sitewise

### Introduction
If your industrial devices only publish MQTT data, you can use this AWS Greengrass Lambda code/function to transmit the data from AWS Greengrass version 1 MQTT broker to AWS IoT SiteWise.

### Deployment process

Let’s setup and deploy the Greengrass lambda function that collects the messages from the Greengrass MQTT broker and sends to IoT Sitewise in the cloud.

We will setup the lambda function in your AWS account. The lambda function takes two arguments.

Download the git repo code on to your local mac/pc. Make sure you have AWS CLI is setup and configured with your AWS account credentials so that you can run the `aws cli` commands from the terminal/command prompt.

Run the below steps on your mac/pc. The `build.sh` script will create a package file with AWS lambda function code, creates the necessary AWS Greengrass lambda function definition, device definition, subscription definition, and Greengrass group version. Finally, it will deploy the Greengrass Group to your Greengrass core device.

This script takes three arguments.
1.	First argument is your AWS CLI profile name. If you are using `default` profile for your AWS CLI, the value will be either “default” or ‘’ (two single quotes with our any space).
2.	Second argument is your AWS Greengrass group name.
3.	Third argument is your Publisher device/thing name. The default name that was used is `Sitewise_MQTT_Publisher`.

```
cd ~
git clone <>
cd sitewise-mqtt/mqtt-sitewise-connector-lambda/
```

Run `build.sh` script.
```
bash ./build.sh <AWS_CLI_PROFILE_NAME> <GREENGRASS_GROUP_NAME> Sitewise_MQTT_Publisher
```

Once this script execution has completed, you can see the deployment should be successful in the AWS Console page like below.

![Alt text](Picture1.png?raw=true "lambda-deployment")


