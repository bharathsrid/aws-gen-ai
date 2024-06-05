stack_name=""
aws_region=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --stack-name)
            stack_name="$2"
            shift 2
            ;;
        --aws-region)
            aws_region="$2"
            shift 2
            ;;
        *)
            echo "Invalid option: $1" >&2
            exit 1
            ;;
    esac
done

# Check if both parameters are provided
if [ -z "${stack_name}" ] || [ -z "${aws_region}" ]; then
    echo "Error: --stack-name and --aws-region are required." >&2
    exit 1
fi

export ARTIFACT_BUCKET_NAME="$stack_name-ta-agent-resources-$RANDOM"

aws s3 mb s3://${ARTIFACT_BUCKET_NAME} --region ${aws_region} --profile child
echo "Successfully created bucket $ARTIFACT_BUCKET_NAME"
aws s3 cp ../lambda/ s3://${ARTIFACT_BUCKET_NAME}/lambda/ --recursive --include "*.zip" --profile child



aws cloudformation create-stack \
--profile child \
--stack-name ${stack_name} \
--template-body file://../cfn/yfn-daily-fetch.yaml \
--parameters \
ParameterKey=S3Bucket,ParameterValue=${ARTIFACT_BUCKET_NAME} \
--capabilities CAPABILITY_NAMED_IAM \
--region ${aws_region}

# sleep 5
aws cloudformation describe-stacks --stack-name $stack_name --region ${aws_region} --query "Stacks[0].StackStatus" --profile child
aws cloudformation wait stack-create-complete --stack-name $stack_name --region ${aws_region} --profile child
aws cloudformation describe-stacks --stack-name $stack_name --region ${aws_region} --query "Stacks[0].StackStatus" --profile child

echo "Successfully created stack $stack_name"
echo "Successfully created bucket $ARTIFACT_BUCKET_NAME"
echo "These details would be needed while clean up"