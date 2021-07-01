# /*
# __author__ = "Srikanth Kodali - skkodali@"
# */

#!/usr/bin/env bash
# AWS_CLI_PROFILE="skkodali1"

_setEnv()
{
  AWS="aws"
  ZIP_FILE_NAME="mqtt-sitewise-connector-lambda.zip"
  FUNCTION_NAME="mqtt-ggv1-lambda-to-sitewise-edge"
  LAMBDA_ROLE_NAME="sitewise-mqtt-lambda-exe-role"
  WAIT_TIME=20
  STREAM_NAME="SiteWise_Stream"
  LAMBDA_TIMEOUT=300
  LAMBDA_MEMORY_SIZE=2048
  LAMBDA_RUNTIME="python3.7"
  AWS_REGION="us-east-1"
  LAMBDA_HANDLER="SubscribeFromGGBroker.lambda_handler"
}

_check_if_jq_exists() {
  JQ=`which jq`
  if [ $? -eq 0 ]; then
    echo "JQ exists."
  else
    echo "jq does not exists, please install it."
    echo "EXITING the program."
    exit 1;
  fi
}

_check_if_zip_exists() {
  JQ=`which zip`
  if [ $? -eq 0 ]; then
    echo "ZIP exists."
  else
    echo "zip does not exists, please install it."
    echo "EXITING the program."
    exit 1;
  fi
}

_bundle_the_code() {
  zip -r ${ZIP_FILE_NAME} conf _SendToStreamManager.py SubscribeFromGGBroker.py
}

_create_iam_role_and_lambda_function() {
  ROLE_SUCCESS=`aws iam create-role --role-name ${LAMBDA_ROLE_NAME} \
    --profile ${AWS_CLI_PROFILE} \
    --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'`

  if [ $? -eq 0 ]; then
    LAMBDA_ROLE_ARN=`echo ${ROLE_SUCCESS} | jq -r '.Role | .Arn'`
    echo "LAMBDA_ROLE_ARN is : ${LAMBDA_ROLE_ARN}"
    aws iam attach-role-policy --profile ${AWS_CLI_PROFILE} --role-name ${LAMBDA_ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
  fi

  echo "sleeping for 10 seconds for the role to be ready."
  sleep 10
  CR_FUNC=`aws lambda create-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} \
    --zip-file fileb://${ZIP_FILE_NAME} --handler ${LAMBDA_HANDLER} --runtime ${LAMBDA_RUNTIME} --role ${LAMBDA_ROLE_ARN} \
    --timeout ${LAMBDA_TIMEOUT} --memory-size ${LAMBDA_MEMORY_SIZE}`
  IP_FUNC=`aws lambda update-function-configuration --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} \
    --environment "Variables={wait_time=${WAIT_TIME},stream_name=${STREAM_NAME}}"`
  #PUB_FUNC=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME}`
  #echo ${PUB_FUNC}
  AWS_LAMBDA_ARN=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} | jq -r '.FunctionArn'`
  echo ${AWS_LAMBDA_ARN}
}

_update_lambda_function() {
  #aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb:///Users/skkodali/work/Blogs-And-Artifacts/MQTT-GG-SitewiseEdge/mqtt-sitewise-connector-lambda/mqtt-sitewise-connector-lambda.zip
  UP_FUNC=`aws lambda update-function-code --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --zip-file fileb://${ZIP_FILE_NAME}`
  UP_FUNC_CONFIG=`aws lambda update-function-configuration --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} \
    --environment "Variables={wait_time=${WAIT_TIME},stream_name=${STREAM_NAME}}"`
  sleep 5
  #UP_PUB_VERSION=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME}`
  #echo "UPDATE :::: ${UP_PUB_VERSION}"
  AWS_LAMBDA_ARN=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} | jq -r '.FunctionArn'`
  echo ${AWS_LAMBDA_ARN}
}

_create_lambda_versions_and_alias() {
  echo "sleeping for 5 seconds for the lambda function to be ready."
  sleep 5
  LIST_VERSIONS=`aws lambda list-versions-by-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"`
  LATEST_VERSION=`aws lambda list-versions-by-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"|sed '1d; $d' | sed  "s/ //g" | tr -d '"'`
  echo "Latest version is : ${LATEST_VERSION}"
  echo "sleeping for 10 seconds for the lambda function version to be ready."
  sleep 5
  AL_LAMBDA=`aws lambda create-alias --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --description "alias for live version of function" \
    --name mqtt-ggv1-lambda-alias-$LATEST_VERSION --function-version $LATEST_VERSION`
  ALIAS_ARN=`echo ${AL_LAMBDA} | jq -r '.AliasArn'`
  echo "Alias ARN is : ${ALIAS_ARN}"
}

_check_if_lambda_exists_and_create() {
  aws lambda get-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "Function ${FUNCTION_NAME} exists, Updaing the configuration."
    _update_lambda_function
    _create_lambda_versions_and_alias
  else
    echo "Function ${FUNCTION_NAME} does not exists, creating the lambda function."
    _create_iam_role_and_lambda_function
    _create_lambda_versions_and_alias
  fi
}

_get_aws_account_number() {
  IDENTITY=`aws sts get-caller-identity`
  echo ${IDENTITY}
  AWS_ACCOUNT_NUMBER=`echo ${IDENTITY} | jq -r '.Account'`
  echo "AWS_ACCOUNT_NUMBER is : ${AWS_ACCOUNT_NUMBER}"
}

_get_lambda_function_arn() {
  #AWS_LAMBDA_ARN="arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_NUMBER}:function:${FUNCTION_NAME}:5"
  AWS_LAMBDA_ARN="arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_NUMBER}:function:${FUNCTION_NAME}"
  echo ${AWS_LAMBDA_ARN}
}

_create_a_lambda_function_definition() {
  res=`aws greengrass create-function-definition --profile ${AWS_CLI_PROFILE} \
    --name "gg-${FUNCTION_NAME}" \
    --initial-version '{"Functions": [{"Id": "'"${FUNCTION_NAME}-vers-id"'", "FunctionArn": "'"${ALIAS_ARN}"'", "FunctionConfiguration": {"Executable": "'"${LAMBDA_HANDLER}"'", "Pinned": true, "Timeout": 5,"Environment": {"Execution": {"IsolationMode": "NoContainer"}}}}]}'`
  #echo $res
  LAMBDA_FUNCTION_LATEST_VERSION_ARN=`echo $res | jq -r '.LatestVersionArn'`
  LAMBDA_FUNCTION_ID=`echo $res | jq -r '.Id'`
  echo "LAMBDA_FUNCTION_LATEST_VERSION_ARN - ${LAMBDA_FUNCTION_LATEST_VERSION_ARN}"
  echo "LAMBDA_FUNCTION_ID - ${LAMBDA_FUNCTION_ID}"
}

_create_function_definition_version() {
  cat << EOF > cr_function_def_version.json
  [{
   "Id": "${FUNCTION_NAME}-vers-id",
   "FunctionArn": "${ALIAS_ARN}",
   "FunctionConfiguration": {
   "Executable": "${LAMBDA_HANDLER}",
   "MemorySize": 2048000,
   "Pinned": true,
   "Timeout": 3
   }
  }]
EOF
 cat cr_function_def_version.json
 cr_func_def_res=`aws greengrass create-function-definition-version --profile ${AWS_CLI_PROFILE} --function-definition-id "${LAMBDA_FUNCTION_ID}" --functions file://cr_function_def_version.json`
 echo ${cr_func_def_res}
 GGC_FUNC_DEF_VER_ARN=`echo ${cr_func_def_res} | jq -r '.Arn'`
 echo "GGC_FUNC_DEF_VER_ARN is : ${GGC_FUNC_DEF_VER_ARN}"
}

_get_publisher_device_thing_arn() {
  SOURCE_PUBLISHER_DEVICE_ARN=`aws iot list-things --profile ${AWS_CLI_PROFILE} | jq -c '.things[] | select( .thingName == "'"${SOURCE_PUBLISHER_THING_NAME}"'" )' | jq -r '.thingArn'`
  echo "SOURCE_PUBLISHER_DEVICE_ARN is - ${SOURCE_PUBLISHER_DEVICE_ARN}"
}

_get_thing_cert_arn() {
  #Assuming this publisher device/thing has only one certificate attached, and it always gets the 1st certificate from the list.
  THING_CERT_ARN=`aws iot list-thing-principals --thing-name ${SOURCE_PUBLISHER_THING_NAME} --profile ${AWS_CLI_PROFILE} | jq -r '.principals[0]'`
  echo ${THING_CERT_ARN}

  DESC_THING=`aws iot describe-thing --profile ${AWS_CLI_PROFILE} --thing-name ${SOURCE_PUBLISHER_THING_NAME} | jq`
  PUBLISHER_DEVICE_ARN=`echo ${DESC_THING} | jq -r .thingArn`
  echo "PUBLISHER_DEVICE_ARN is - ${PUBLISHER_DEVICE_ARN}"
}

_create_device_definition() {
  res_dev_def=`aws greengrass list-device-definitions --profile ${AWS_CLI_PROFILE} | jq -r '.Definitions[] | select(.Name == "'"${SOURCE_PUBLISHER_THING_NAME}-Device"'").Name'`
  if [ ${res_dev_def} == "${SOURCE_PUBLISHER_THING_NAME}-Device" ]; then
    echo "Device definition already exists - Not recreating it and getting the latest version arn."
    DEVICE_LATEST_VERSION_ARN=`aws greengrass list-device-definitions --profile skkodali1 | jq -r '.Definitions[] | select(.Name == "'"Sitewise_MQTT_Publisher-Device"'").LatestVersionArn'`
    echo "DEVICE_LATEST_VERSION_ARN is - ${DEVICE_LATEST_VERSION_ARN}"
  else
    DEVICE_DEFINITION=`aws greengrass create-device-definition --name "${SOURCE_PUBLISHER_THING_NAME}-Device" --profile ${AWS_CLI_PROFILE} \
      --initial-version '{"Devices":[{ "Id":"'"${SOURCE_PUBLISHER_THING_NAME}"'", "ThingArn":"'"${PUBLISHER_DEVICE_ARN}"'","CertificateArn":"'"${THING_CERT_ARN}"'","SyncShadow":true}]}'`
    echo "DEVICE_DEFINITION is - ${DEVICE_DEFINITION}"
    DEVICE_LATEST_VERSION_ARN=`echo ${DEVICE_DEFINITION} | jq -r '.LatestVersionArn'`
    echo "DEVICE_LATEST_VERSION_ARN is - ${DEVICE_LATEST_VERSION_ARN}"
  fi
}

_create_subscription_definition_and_version() {
  sub_res=`aws greengrass create-subscription-definition --profile ${AWS_CLI_PROFILE} \
    --initial-version '{"Subscriptions": [{"Id": "'"${FUNCTION_NAME}-subscription-id"'", "Source": "'"${SOURCE_PUBLISHER_DEVICE_ARN}"'", "Subject": "devpub/to/lambda", "Target": "'"${ALIAS_ARN}"'"}]}'`
  echo "SUBSCRIPTION_DEFINITION is - ${sub_res}"
  SUBSCRIPTION_DEFINITION_ARN=`echo $sub_res | jq -r '.LatestVersionArn'`
  echo "SUBSCRIPTION_DEFINITION_ARN is : ${SUBSCRIPTION_DEFINITION_ARN}"
}

_check_ggc_group_and_get_core_definition() {
  res_bool=`aws greengrass list-groups --profile ${AWS_CLI_PROFILE} | jq '.Groups[].Name == "'"$GGC_GROUP_NAME"'"'`
  if [ res_bool ]; then
    echo "GGC group ${GGC_GROUP_NAME} exists, proceeding with the next steps"
    GGC_GROUP_ID=`aws greengrass list-groups --profile ${AWS_CLI_PROFILE} | jq -c '.Groups[] | select( .Name == "'"$GGC_GROUP_NAME"'" )' | jq -r .Id`
    echo "GGC_GROUP_ID IS - ${GGC_GROUP_ID}"
    GGC_GROUP_LATEST_VERSION=`aws greengrass list-groups --profile ${AWS_CLI_PROFILE} | jq -c '.Groups[] | select( .Name == "'"$GGC_GROUP_NAME"'" )' | jq -r .LatestVersion`
    echo "GGC_GROUP_LATEST_VERSION is - ${GGC_GROUP_LATEST_VERSION}"
    RES_CORE_DEFINITION_VERSION=`aws greengrass get-group-version --profile ${AWS_CLI_PROFILE} --group-id ${GGC_GROUP_ID} --group-version-id ${GGC_GROUP_LATEST_VERSION}`
    echo "RES_CORE_DEFINITION_VERSION is - ${RES_CORE_DEFINITION_VERSION}"
    GGC_CORE_DEFINITION_VERSION_ARN=`echo ${RES_CORE_DEFINITION_VERSION} | jq -c '.Definition' | jq -r '.CoreDefinitionVersionArn'`
    echo "GGC_CORE_DEFINITION_VERSION_ARN is - ${GGC_CORE_DEFINITION_VERSION_ARN}"
  else
    echo "GGC group ${GGC_GROUP_NAME} does not exists, exiting"
    exit -1
  fi
}

_create_group_version() {
  RES_GGC_GROUP_VERSION=`aws greengrass create-group-version --profile ${AWS_CLI_PROFILE} --group-id ${GGC_GROUP_ID} \
                        --core-definition-version-arn ${GGC_CORE_DEFINITION_VERSION_ARN} \
                        --function-definition-version-arn ${LAMBDA_FUNCTION_LATEST_VERSION_ARN} \
                        --subscription-definition-version-arn ${SUBSCRIPTION_DEFINITION_ARN} \
                        --device-definition-version-arn ${DEVICE_LATEST_VERSION_ARN} \
                        `
  echo ${RES_GGC_GROUP_VERSION}
  GGC_GROUP_VERSION=`echo ${RES_GGC_GROUP_VERSION} | jq -r '.Version'`
  echo ${GGC_GROUP_VERSION}
}

_create_deployment() {
  GGC_DEPLOYMENT_RES=`aws greengrass create-deployment --profile ${AWS_CLI_PROFILE} --deployment-type NewDeployment --group-id "${GGC_GROUP_ID}" --group-version-id "${GGC_GROUP_VERSION}"`
  echo "GGC_DEPLOYMENT_RES - ${GGC_DEPLOYMENT_RES}"
  GGC_DEPLOY_ID=`echo ${GGC_DEPLOYMENT_RES} | jq -r ".DeploymentId"`
  echo ${GGC_DEPLOY_ID}
}

#### MAIN ####

echo $#
if [ "$#" -ne 3 ]; then
  echo "usage: build.sh <AWS_PROFILE_NAME> <GREENGRASS_GROUP_NAME> <SOURCE_PUBLISHER_THING_NAME>"
  echo "If you do not want to use profile name, Greengrass group name and publisher thing name, just pass an empty parameter with '' if you do not want to use the profile name. "
  echo $#
  exit 1
fi

#echo $1
AWS_CLI_PROFILE="default"
GGC_GROUP_NAME=${2}
SOURCE_PUBLISHER_THING_NAME=${3}

if [ -z "${1}" ]; then
  echo "AWS PROFILE variable is set to default."
else
  echo "AWS PROFILE variable is set to ${1}"
  AWS_CLI_PROFILE=${1}
fi
echo "AWS Profile name is : ${AWS_CLI_PROFILE}"
echo "Provided Greengrass group name is : ${GGC_GROUP_NAME}"

_setEnv
_check_if_jq_exists
_check_if_zip_exists
_bundle_the_code
_check_if_lambda_exists_and_create
_get_aws_account_number
#_get_lambda_function_arn # not needed
_create_a_lambda_function_definition
_get_thing_cert_arn
_create_device_definition
#_create_function_definition_version # not needed
_get_publisher_device_thing_arn
_create_subscription_definition_and_version
_check_ggc_group_and_get_core_definition
_create_group_version
_create_deployment


