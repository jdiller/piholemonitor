import requests
import os
import logging

class Session():
    def __init__(self, config) -> None:
        self.config = config
        self._session = self._init_connection()

    def _init_connection(self):
        pihole_host = self.config.get("pihole", "host")
        pihole_port = self.config.get("pihole", "port", fallback=443)
        pihole_api_key = self.config.get("pihole", "api_key")
        self.base_url = f'https://{pihole_host}:{pihole_port}/api/'
        auth_url = f'{self.base_url}auth'
        auth_payload = {'password': pihole_api_key}

        # Debug: Check what we're getting from config
        client_cert = self.config.get("pihole", "client_cert")
        logging.debug(f"client_cert from config: {client_cert}")
        logging.debug(f"client_cert type: {type(client_cert)}")

        # Handle client certificate authentication properly
        if client_cert:
            # Check if the file exists
            if os.path.exists(client_cert):
                logging.info(f"Client cert file exists: {client_cert}")
                # Use cert= for client authentication, verify=True for server validation
                response = requests.post(auth_url, json=auth_payload, cert=client_cert, verify=True)
            else:
                logging.warning(f"Client cert file NOT found: {client_cert}")
                # No client cert available, try without it
                response = requests.post(auth_url, json=auth_payload, verify=True)
        else:
            logging.info("No client_cert specified, using default SSL verification only")
            # Use default SSL verification, no client cert
            response = requests.post(auth_url, auth_payload, verify=True)

        logging.info(f"Response status: {response.status_code}")
        logging.debug(f"Response text: {response.text}")
        return response.json()['session']

    def __getitem__(self, key):
        return self._session[key]

    def __setitem__(self, key, value):
        self._session[key] = value

    def __delitem__(self, key):
        del self._session[key]

    def __contains__(self, key):
        return key in self._session

    def __iter__(self):
        return iter(self._session)

    def __len__(self):
        return len(self._session)

    def keys(self):
        return self._session.keys()

    def values(self):
        return self._session.values()

    def items(self):
        return self._session.items()

    def get(self, key, default=None):
        return self._session.get(key, default)

    def pop(self, key, default=None):
        return self._session.pop(key, default)

    def update(self, other):
        self._session.update(other)

class Api():
    def __init__(self, session:Session) -> None:
        self.session = session

    def get_metrics_summary(self):
        metrics_url = f'{self.session.base_url}stats/summary'
        headers = {'X-FTL-SID': self.session.get('sid')}
        logging.debug(f"headers: {headers}")
        response = requests.get(metrics_url, headers=headers)
        return response.json()