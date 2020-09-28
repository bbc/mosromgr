import boto3


class SNS:
    """
    This class provides basic AWS SNS publish functionality. To use the class
    instantiate it with an SNS topic ARN, and then call
    :func:`send_sns_notification`. Some strings are defined in the class to
    use in the *subject* field of :func:`send_sns_notification`.
    """

    subject_base = 'MosRoMgr %s Notification'
    WARNLVL = subject_base % 'WARNING'
    INFOLVL = subject_base % 'INFORMATION'
    ERRORLVL = subject_base % 'ERROR'
    DEBUGLVL = subject_base % 'DEBUG'

    def __init__(self, arn):
        self.topic_arn = arn
        self.client = boto3.client('sns')

    def send_sns_notification(self, subject, text):
        """
        Publishes an SNS notification with the subject: *subject* and
        the body: *text*. The status message from SNS is returned.
        """
        if 'Traceback' in text:
            attributes = {
                'type': {
                    'DataType': 'String',
                    'StringValue': 'Traceback'
                }
            }
        else:
            attributes = {
                'type': {
                    'DataType': 'String',
                    'StringValue': 'Other'
                }
            }
        return self.client.publish(
            TopicArn=self.topic_arn,
            Message=text,
            Subject=subject,
            MessageAttributes=attributes
        )
