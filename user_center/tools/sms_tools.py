import boto3
import random


def send_aws_sms(aws_access_key_id, aws_secret_access_key, phone_number, message, region_name=None):
    if region_name is None:
        region_name_list = [
            'ap-northeast-1',
            'ap-southeast-1',
            'ap-southeast-2',
            'eu-west-1',
            'sa-east-1',
            'us-east-1',
            'us-west-1',
            'us-west-2',
        ]
        region_name = random.sample(region_name_list, 1)[0]
    sns = boto3.client('sns', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    result = sns.publish(
        PhoneNumber=phone_number,
        Message=message,
    )
    # print('aws sms result', result, type(result))
    # {'MessageId': 'af55729f-9b2b-58d0-a398-261d16159cb2', 'ResponseMetadata': {'RequestId': '8b7d539f-905b-5aac-977f-071d1d65fece', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '8b7d539f-905b-5aac-977f-071d1d65fece', 'content-type': 'text/xml', 'content-length': '294', 'date': 'Thu, 06 Dec 2018 02:35:41 GMT'}, 'RetryAttempts': 0}}
    if isinstance(result, dict) and 'ResponseMetadata' in result and 'HTTPStatusCode' in result['ResponseMetadata'] and result['ResponseMetadata']['HTTPStatusCode'] == 200:
        result['region_name'] = region_name
        return True, result
    else:
        result['region_name'] = region_name
        return False, result


if __name__ == '__main__':
    pass


