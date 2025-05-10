

## Request

Write code in your language of choice to gather information about all of the instances in
the current region. It should group them by the AMI’s that are in use, with information
about the AMI's and how many EC2 Instances are using them. Format the output as a
JSON object as below.

- Assume that AWS Credentials are available in the environment.
- If AMI’s are no longer available, null is an acceptable value for AMI
specific items. Do not assume that all AMI’s are owned by the
current account.
- Assume the environment being queried is a large account with lots of
instances and AMIs. Output results to stdout.

## Plan

- Fetch EC2 Instances
    - Boto3, `describe_instances` should work, it includes `ImageId` (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html) 
    - What does "current" region infer? I'll default to using env vars (ex: `export AWS_DEFAULT_REGION=us-east-1`) and refactor if nessisary.
    - It will be large, the `describe_instance` documentation includes "We strongly recommend using only paginated requests. Unpaginated requests are susceptible to throttling and timeouts."
        - Example of how to use paginator with Boto3: https://www.learnaws.org/2023/02/14/aws-boto3-paginator/
    - Should I filter EC2 data, ex tags, type, or recently reminated instances? The `describe_instance` documentation includes "Recently terminated instances might appear in the returned results. This interval is usually less than one hour."

- Format JSON output.
    - We will need the following 
        - `ami_id`
            - `ImageDescription`
            - `ImageName`
            - `ImageLocation`
            - `OwnerId`
            - `InstanceIds` (list)

Example output:

```
{
  "ami-0d5f069b7a75be450": {
    "ImageDescription": "ubuntu-1804-encrypted-amd64-20190403",
    "ImageName": "ubuntu-1804-encrypted-amd64-20190403",
    "ImageLocation": "12345678901/ubuntu-1804-encrypted-amd64-20190403",
    "OwnerId": "12345678901",
    "InstanceIds": [
      "i-04f241953cfe0066d",
      "i-02439968b22cb6b8d"
    ]
  },
  "ami-c0464db9": {
    "ImageDescription": "Canonical, Ubuntu, 16.10, amd64 yakkety image build",
    "ImageName": "ubuntu/images/hvm-ssd/ubuntu-yakkety-16.10-amd64-server-20161020",
    "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-yakkety-16.10-amd64-server-20161020",
    "OwnerId": "099720109477",
    "InstanceIds": [
      "i-063e73a673eda7892"
    ]
  },
  "ami-1df0ac78": {
    "ImageDescription": null,
    "ImageName": null,
    "ImageLocation": null,
    "OwnerId": null,
    "InstanceIds": [
      "i-19be2ba7",
      "i-6a7a49dd"
    ]
  }
}
```