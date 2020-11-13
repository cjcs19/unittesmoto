import json
import boto3
import logging
from botocore.exceptions import ClientError

class route53:
    def __init__ (self,region,hostedZone,dnsname,**kwargs):
        
        if "rolearn" in kwargs:
            sts = boto3.client('sts')
            try:
                assumed_role_object=sts.assume_role(
                    RoleArn=kwargs.get('rolearn'),
                    RoleSessionName='AssumeRoleSession1'
                )
            except Exception as e:
                print('Cant assume role %s'% e)
                
            credentials=assumed_role_object['Credentials']  
            
            self.client = boto3.client(
                    'route53',
                    region_name=region,
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
            )
        else:            
            self.client = boto3.client(
                'route53',
                region_name=region
                )
                
        self.hostedZone = hostedZone
        self.dnsname = dnsname
        self.hostedZoneName = self.client.list_hosted_zones_by_name(
                HostedZoneId=self.hostedZone,
                DNSName=self.dnsname,
                MaxItems='1'
            )['HostedZones'][0]['Name']
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
    def listAllEntries(self):
        try:
            
            currentRecordSet = self.client.list_resource_record_sets(
                HostedZoneId=self.hostedZone
                )
            self.logger.info(currentRecordSet)
            return json.dumps(currentRecordSet)
            
        except ClientError as e:
            raise e

    def getEntries(self,entryName):
        try:
            currentRecordSet = self.client.list_resource_record_sets(
                HostedZoneId=self.hostedZone,
                StartRecordName=entryName+'.'+self.hostedZoneName
                )
                
            ips=[]
            for entry in currentRecordSet['ResourceRecordSets']:
                if entry['Name'] == entryName:
                    for subRecord in entry['ResourceRecords']:
                        ips.append(subRecord['Value'])
            return currentRecordSet['ResourceRecordSets']
        except ClientError as e:
            raise e

    def getIpEntries(self,entryName):
        try:
            currentRecordSet = self.client.list_resource_record_sets(
                HostedZoneId=self.hostedZone,
                StartRecordName=entryName+'.'+self.hostedZoneName
                )
                
            ips=[]
            for entry in currentRecordSet['ResourceRecordSets']:                
                    for subRecord in entry['ResourceRecords']:
                        ips.append(subRecord['Value'])

            return ips
        except ClientError as e:
            raise e

    def getHostedZone(self):
        try:            
            return self.hostedZoneName
        except ClientError as e:
            raise e

    def createEntry(self, entryName, ip, dnsType, TTL):
        ipList=[]
        #for ip in ips:
        ipList.append({'Value': ip})
        jsonChangeBatch={
            'Changes':[
                {
                    'Action': "UPSERT",
                    'ResourceRecordSet' : {
                        'Name': entryName+'.'+self.hostedZoneName,
                        'Type': dnsType,
                        'TTL' : TTL,
                        'ResourceRecords' : ipList
                    }
                }
            ]
        }
        try:
            self.client.change_resource_record_sets(
                HostedZoneId=self.hostedZone,
                ChangeBatch=jsonChangeBatch
            )
        except ClientError as e:
            raise e
    
    def deleteEntry(self, entryName, ip, dnsType, TTL):
        try:
            self.client.change_resource_record_sets(
                HostedZoneId=self.hostedZone,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'DELETE',                         
                            'ResourceRecordSet': {
                                'Name': entryName+'.'+self.hostedZoneName,
                                'Type': dnsType,
                                "TTL": TTL,
                                'ResourceRecords': [
                                    {'Value': ip}
                                ]
                            }
                        }
                    ]
                }
            )
        except ClientError as e:
            raise e


class S3:
    
    def __init__ (self,bucketname):
                
        self.bucketname = bucketname        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    
    def downloadFile(self,s3_object, output_file):    
        s3_resource = boto3.resource('s3')
        body = s3_resource.Object(self.bucketname , s3_object).get()['Body']
        with open(output_file, 'wb') as f:
            for chunk in iter(lambda: body.read(1024), b''):
                f.write(chunk)

    def uploadFile(self,input_file, s3_object):
      
        s3_resource = boto3.resource('s3')

        with open(input_file, 'rb') as f:
            binary = f.read()

        s3_resource.Bucket(self.bucketname).put_object(
            Key=s3_object,
            Body=binary
        )


class EC2:
    
    def __init__ (self,region):
                
        self.region = region        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def describeTags(self,idInstance):    
        ec2 = boto3.resource('ec2',region_name=self.region)        
        response=ec2.Instance(idInstance)
        return response.tags