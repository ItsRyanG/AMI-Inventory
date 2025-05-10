#!/usr/bin/env python3
import boto3
import json
from botocore.exceptions import ClientError

def fetch_ami_inventory(ec2_client):
    amis = {}  # Dictionary to store AMI inventory
    try:
        paginator = ec2_client.get_paginator('describe_instances')
        for page in paginator.paginate():
            # call .get(...) not use square brackets
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    ami_id = instance.get('ImageId')
                    instance_id = instance.get('InstanceId')
                    if ami_id and instance_id:
                        amis.setdefault(ami_id, []).append(instance_id)
        return amis

    except ClientError as e:
        print(f"Error fetching AMI inventory: {e}")

def fetch_ami_details(ec2_client, ami_id):
    ami_details = { # Create dictionary with default values for AMI details
        "ImageDescription": None,
        "ImageName": None,
        "ImageLocation": None,
        "OwnerId": None,
        "InstanceIds": [] # Initialize empty list for instance IDs
    }
    
    try:
        response = ec2_client.describe_images(ImageIds=[ami_id]) # Query AWS for details about this AMI
        images = response.get('Images', []) # Get images from response, empty list if not found
        
        if images: # If we got image details back
            image = images[0] # Get the first (should be only) image
            ami_details.update({ # Update our details dictionary with actual values
                "ImageDescription": image.get('Description'),
                "ImageName": image.get('Name'),
                "ImageLocation": image.get('ImageLocation'),
                "OwnerId": image.get('OwnerId')
            })
    except ClientError  as e: # If we can't get details for this AMI
        print(f"Error fetching AMI details for {ami_id}: {str(e)}") # Print error message
    
    return ami_details # Return the AMI details dictionary

def main():
    ec2_client = boto3.client('ec2') # Initialize EC2 client using default credentials
    ami_inventory = fetch_ami_inventory(ec2_client)
    image_ids = list(ami_inventory.keys())

    # One describe_images call:
    response = ec2_client.describe_images(ImageIds=image_ids)
    output = {}
    for img in response.get("Images", []):
        ami_id = img["ImageId"]
        output[ami_id] = {
            "ImageDescription": img.get("Description"),
            "ImageName":        img.get("Name"),
            "ImageLocation":    img.get("ImageLocation"),
            "OwnerId":          img.get("OwnerId"),
            "InstanceIds":      ami_inventory.get(ami_id, [])
        }

    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()