import boto3
import json
from p001.tests import test_modules
from moto import mock_route53, mock_s3, mock_ec2
from p001.modules.devco_aws import route53,S3,EC2
import logging

import sure  # noqa
import botocore
from nose.tools import assert_raises

import sys

import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@mock_route53
def test_route53():
      
    conn = boto3.client("route53", region_name="us-east-1")
    
    firstzone = conn.create_hosted_zone(
        Name="r53testdns.aws.com",
        CallerReference=str(hash("foo")),
        HostedZoneConfig=dict(PrivateZone=True, Comment="Test"),
    )

    logger.info(firstzone)

    nametest="test100"
    iptest="10.1.0.1"
    
    zone_id = firstzone["HostedZone"]["Id"].split("/")[-1]
    domaintest = firstzone["HostedZone"]["Name"]

    hosted_zone = conn.get_hosted_zone(Id=zone_id)
    hosted_zone["HostedZone"]["Config"]["PrivateZone"].should.equal(True)

    responseMoto = conn.list_resource_record_sets(HostedZoneId=zone_id)
    len(responseMoto["ResourceRecordSets"]).should.equal(0)  

    logger.info(responseMoto)  
    
    r53 = route53('us-east-1',zone_id,domaintest)
    responseClass=r53.listAllEntries() 

    len(responseClass).shouldnt.equal(0)

    responseClass.should.equal( json.dumps(responseMoto))

    responseClass=r53.getHostedZone()
    responseClass.should.equal(domaintest)

@mock_s3
def test_S3():
    

    s3_resource = boto3.resource('s3')
    s3_resource.create_bucket(Bucket='s3devcotest')

    with open('/tmp/data', 'rb') as f:
        binary = f.read()

    s3_resource.Bucket('s3devcotest').put_object(
            Key='data',
            Body=binary
        )

    s3_object = s3_resource.Object(
                's3devcotest',
                'data'
            )

    keys = s3_object.get().keys()
    len(keys).shouldnt.equal(0)

    s3=S3('s3devcotest')
    
    #####AQUI PRUEBA DE MOTO UPLOAD
    
    s3.downloadFile('data','./test10001.txt')

    os.path.isfile('./test10001.txt').should.equal(True)

    os.remove("./test10001.txt")
    
    logger.info("result")  

@mock_ec2   
def test_EC2():
    
    ec2 = boto3.resource('ec2',region_name="us-east-1")
    ssh_server = ec2.create_instances(ImageId='ami-xxxxx', MinCount=1, MaxCount=4)

    for s in ssh_server:
        ec2.create_tags(
            Resources=[s.id],
            Tags=[{'Key': 'typesrv', 'Value': 'ssh_server'}])

    for s in ssh_server:
        ec2instance = s.id
        for tags in s.tags:            
                instancetags = tags

    logger.info(ec2instance)

    result=ec2.Instance(ec2instance)
    logger.info(result.tags)

    ec2devco = EC2("us-east-1")
    resultdevco=ec2devco.describeTags(ec2instance)
    result.tags.should.be.equal(resultdevco)

    logger.info(resultdevco)
      

    
