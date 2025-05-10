

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

## Plan

I’ll begin by discovering all EC2 instances in whatever region is active (I’ll rely on `AWS_DEFAULT_REGION`, e.g. `export AWS_DEFAULT_REGION=us-east-1`).  For each instance, I’ll pull its `ImageId` using Boto3’s [`describe_instances`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html) call with a paginator (see this [paginator example](https://www.learnaws.org/2023/02/14/aws-boto3-paginator/), it helps avoid throttling when the account is large).  I’ll group instance IDs by AMI.

Next, I’ll fetch details for the unique set of AMI IDs in one go via `describe_images(ImageIds=[…])`.  From each image I’ll grab `Description`, `Name`, `ImageLocation`, and `OwnerId`, and default to `null` if any of those fields aren’t present (for example, when an AMI has been deleted or belongs to another account).

I’m aware that recently terminated instances can still show up in `describe_instances` for about an hour, if needed I can filter those out later, but for now I’ll accept that minor noise. 

Finally, I’ll assemble a JSON object keyed by each AMI ID, with something like:

```json
{
  "ami-0123456789abcdef0": {
    "ImageDescription": "...",
    "ImageName":        "...",
    "ImageLocation":    "...",
    "OwnerId":          "...",
    "InstanceIds":      ["i-0123...", "i-0456..."]
  },

}
```

