import time
import logging
from localconfig import get_config
from logconfig import configure_logging
from datadog import initialize, statsd
from pihole_client import Session, Api

PREFIX = 'pihole.'

def send_metrics(query_metrics:dict, prefix:str):
    for sensor in query_metrics:
        if type(query_metrics[sensor]) == dict:
            prefix = f'{prefix}.{sensor}'
            send_metrics(query_metrics[sensor], prefix)
        else:
            statsd.gauge(f'{prefix}.{sensor}', query_metrics[sensor])

def send_status_metrics(status_metrics:dict):
    for sensor in status_metrics:
        statsd.gauge(f'{PREFIX}status.{sensor}', status_metrics[sensor])

def send_replies_metrics(replies_metrics:dict):
    for sensor in replies_metrics:
        statsd.gauge(f'{PREFIX}replies.{sensor}', replies_metrics[sensor])

def main_loop(session:Session):
    while True:
        api = Api(session)
        metrics = api.get_metrics_summary()
        logging.debug(f"metrics: {metrics}")
        send_metrics(metrics, PREFIX)
        time.sleep(10)

if __name__ == "__main__":
    config = get_config()
    configure_logging(config)
    session = Session(config)
    dd_options = {
        'statsd_host': config.get('datadog', 'statsd_host'),
        'statsd_port': config.get('datadog', 'statsd_port'),
    }
    initialize(**dd_options)
    main_loop(session)