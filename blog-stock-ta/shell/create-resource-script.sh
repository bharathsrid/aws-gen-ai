export ARTIFACT_BUCKET_NAME="$STACK_NAME-ta-agent-resources-$RANDOM"

aws s3 mb s3://${ARTIFACT_BUCKET_NAME} --region ${AWS_REGION} --profile child
echo "Successfully created bucket $ARTIFACT_BUCKET_NAME"
aws s3 cp ../lambda/ s3://${ARTIFACT_BUCKET_NAME}/lambda/ --recursive --include "*.zip" --profile child



aws cloudformation create-stack \
--profile child \
--stack-name ${STACK_NAME} \
--template-body file://../cfn/yfn-daily-fetch.yaml \
--parameters \
ParameterKey=S3Bucket,ParameterValue=${ARTIFACT_BUCKET_NAME} \
--capabilities CAPABILITY_NAMED_IAM \
--region ${AWS_REGION}
