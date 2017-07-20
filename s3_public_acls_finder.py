import boto3 
import requests
import json

AWS_ACCESS_KEY = 'your_access_key'
AWS_SECRET_ACCESS_KEY ='your_secre_access_key'
SLACKWEBHOOK = 'https://hooks.slack.com/services/your slack web hook'
SLACK_CHANNEL = '#s3-public'
SLACK_USERNAME = 'slack user name'
SLACK_EMOJI = ':wastebasket:'

s3_client_connection = boto3.resource(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)

def check_bucket_grant(grant_permission, bucket_name):
    granted_warning = 'The following permission: :bangbang:*{}*:bangbang: has been granted on the bucket *{}*'
    if grant_permission == 'read':
        return granted_warning.format('Read - Public Access: List Objects', bucket_name), True
    elif grant_permission == 'write':
        return granted_warning.format('Write - Public Access: Write Objects', bucket_name), True
    elif grant_permission == 'read_acp':
        return granted_warning.format('Write - Public Access: Read Bucket Permissions', bucket_name), True
    elif grant_permission == 'write_acp':
        return granted_warning.format('Write - Public Access: Write Bucket Permissions', bucket_name), True
    elif grant_permission == 'full_control':
        return granted_warning.format('Public Access: Full Control', bucket_name), True
    return '', False
           
def post_to_slack(webhook, text, channel, username, icon_emoji):
    slack_data = {'text': text, 'username': username, 'icon_emoji': icon_emoji, 'channel': channel, 'link_names': 1}
    response = requests.post(
        webhook, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

def check_S3_buckets_grants():
    for bucket in s3_client_connection.buckets.all():
        print(bucket.name)
        acl = bucket.Acl()
        for grant in acl.grants:
            #http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html
            if grant['Grantee']['Type'].lower() == 'group' \
                and grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
           
                text_to_post, send_warning = check_bucket_grant(grant['Permission'].lower(), bucket.name)
                if send_warning:            
                    post_to_slack(SLACKWEBHOOK, text_to_post, SLACK_CHANNEL, SLACK_USERNAME, SLACK_EMOJI)

if __name__ == "__main__":
    check_S3_buckets_grants()