from termcolor import colored
import boto3
from datetime import datetime, timedelta
from settings import LAMBDA_FUNCTION_MAP

if __name__ == '__main__':
    logs = boto3.client('logs')
    stage = 'dev'

    start_time = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)

    response = logs.filter_log_events(
        logGroupName='/aws/lambda/' + LAMBDA_FUNCTION_MAP[stage],
        startTime=start_time,
        interleaved=True
    )

    for event in response['events']:
        dt = datetime.fromtimestamp(event['timestamp'] / 1000)
        dt = colored(str(dt), 'green')
        msg = event['message']
        print(f"{dt}: {msg}")