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
    --zip-file fileb://${ZIP_FILE_NAME} --handler SubscribeFromGGBroker.lambda_handler --runtime python3.6 --role ${LAMBDA_ROLE_ARN} \
    --timeout ${LAMBDA_TIMEOUT} --memory-size ${LAMBDA_MEMORY_SIZE}`
  IP_FUNC=`aws lambda update-function-configuration --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} \
    --environment "Variables={wait_time=${WAIT_TIME},stream_name=${STREAM_NAME}}"`
  PUB_FUNC=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME}`
}

_update_lambda_function() {
  #aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb:///Users/skkodali/work/Blogs-And-Artifacts/MQTT-GG-SitewiseEdge/mqtt-sitewise-connector-lambda/mqtt-sitewise-connector-lambda.zip
  UP_FUNC=`aws lambda update-function-code --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --zip-file fileb://${ZIP_FILE_NAME}`
  UP_FUNC_CONFIG=`aws lambda update-function-configuration --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} \
    --environment "Variables={wait_time=${WAIT_TIME},stream_name=${STREAM_NAME}}"`
  sleep 5
  UP_PUB_VERSION=`aws lambda publish-version --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME}`
}

_create_lambda_versions_and_alias() {
  echo "sleeping for 5 seconds for the lambda function to be ready."
  sleep 5
  LIST_VERSIONS=`aws lambda list-versions-by-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"`
  LATEST_VERSION=`aws lambda list-versions-by-function --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"|sed '1d; $d' | sed  "s/ //g" | tr -d '"'`
  echo "sleeping for 10 seconds for the lambda function version to be ready."
  sleep 5
  AL_LAMBDA=`aws lambda create-alias --profile ${AWS_CLI_PROFILE} --function-name ${FUNCTION_NAME} --description "alias for live version of function" \
    --name mqtt-ggv1-lambda-alias$LATEST_VERSION --function-version $LATEST_VERSION`
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

#### MAIN ####

echo $#
if [ "$#" -ne 1 ]; then
  echo "usage: build.sh <AWS_PROFILE_NAME>"
  echo "If you do not want to use profile name, just pass an empty parameter with ''. "
  echo $#
  exit 1
fi

#echo $1
AWS_CLI_PROFILE=""

if [ -z "${1}" ]; then
  echo "AWS PROFILE variable is set to default."
else
  echo "AWS PROFILE variable is set to ${1}"
  AWS_CLI_PROFILE=${1}
fi
echo ${AWS_CLI_PROFILE}

_setEnv
_check_if_jq_exists
_check_if_zip_exists
_bundle_the_code
_check_if_lambda_exists_and_create


