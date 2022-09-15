import json
import boto3


def get_configuration(input):
    with open(input) as filestream:
        obj = json.load(filestream)
    return obj


class communication:

    def __init__(myobject):

        myobject.client = boto3.client('sns',
                                       region_name='us-east-2', aws_access_key_id=config['aws_ak'],
                                       aws_secret_access_key=config['aws_sk'])

        myobject.arn = config['aws_sns_tp']
        sub = myobject.client.list_subscriptions_by_topic(
            TopicArn=myobject.arn)
        myobject.sub_mails = [i['Endpoint'] for i in sub['Subscriptions']]

    def make_sub_list(myobject, sub_emails, shared_by):
        myobject.sub_emails = sub_emails
        myobject.mail_subject = f"You recieved a new email. please find url"
        for email in myobject.sub_emails:
            if email not in myobject.sub_mails:
                myobject.client.subscribe(
                    TopicArn=myobject.arn, Protocol="email", Endpoint=email)

    def send_email(myobject, message):
        # This will publish the email and sends to the subscripbers
        myobject.client.publish(TopicArn=myobject.arn,
                                Message=message, Subject=myobject.mail_subject)


config = get_configuration(input="config.json")
