import requests
import os
import logging

class Session():
    def __init__(self, config) -> None:
        self.config = config
        self._session = self._init_connection()

    def _init_connection(self):
        pihole_host = self.config.get("pihole", "host")
        pihole_protocol = self.config.get("pihole", "protocol", fallback="auto")
        pihole_port = self.config.get("pihole", "port", fallback=None)
        pihole_password = self.config.get("pihole", "password", fallback=None)

        # Determine protocol and port
        protocols_to_try = []

        if pihole_protocol.lower() == "auto":
            # Try HTTPS first, then HTTP
            protocols_to_try = [("https", 443), ("http", 80)]
        elif pihole_protocol.lower() == "https":
            protocols_to_try = [("https", 443)]
        elif pihole_protocol.lower() == "http":
            protocols_to_try = [("http", 80)]
        else:
            logging.warning(f"Unknown protocol '{pihole_protocol}', defaulting to auto-detection")
            protocols_to_try = [("https", 443), ("http", 80)]

        # Override default ports if specified in config
        if pihole_port:
            port = int(pihole_port)
            protocols_to_try = [(proto, port) for proto, _ in protocols_to_try]

        client_cert = self.config.get("pihole", "client_cert")
        logging.debug(f"client_cert from config: {client_cert}")
        logging.debug(f"password provided: {'Yes' if pihole_password else 'No'}")
        logging.debug(f"Protocols to try: {protocols_to_try}")

        # Try each protocol/port combination
        for protocol, port in protocols_to_try:
            self.base_url = f'{protocol}://{pihole_host}:{port}/api/'

            # Skip authentication if no password provided
            if not pihole_password:
                logging.info(f"No password provided, skipping authentication for {protocol.upper()}://{pihole_host}:{port}")
                self._session = {}  # Empty session for non-authenticated access
                return self._session

            auth_url = f'{self.base_url}auth'
            auth_payload = {'password': pihole_password}

            logging.info(f"Attempting authentication to {auth_url}")

            try:
                # Configure SSL settings based on protocol
                ssl_verify = True if protocol == "https" else None
                cert_param = None

                if protocol == "https" and client_cert and os.path.exists(client_cert):
                    cert_param = client_cert
                    logging.debug(f"Using client certificate: {client_cert}")
                elif protocol == "https" and client_cert and not os.path.exists(client_cert):
                    logging.warning(f"Client cert file NOT found: {client_cert}")

                # Make the request with appropriate parameters
                if protocol == "https":
                    if cert_param:
                        response = requests.post(auth_url, json=auth_payload, cert=cert_param, verify=ssl_verify, timeout=10)
                    else:
                        response = requests.post(auth_url, json=auth_payload, verify=ssl_verify, timeout=10)
                else:
                    # HTTP - no SSL parameters needed
                    response = requests.post(auth_url, json=auth_payload, timeout=10)

                # Check if the request was successful
                if response.status_code == 200:
                    logging.info(f"Successfully authenticated using {protocol.upper()} on port {port}")
                    logging.debug(f"Response text: {response.text}")
                    return response.json()['session']
                else:
                    logging.warning(f"Failed to authenticate with {protocol.upper()} on port {port}: HTTP {response.status_code}")
                    logging.debug(f"Response text: {response.text}")

            except requests.exceptions.SSLError as e:
                logging.warning(f"SSL error with {protocol.upper()} on port {port}: {e}")
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"Connection error with {protocol.upper()} on port {port}: {e}")
            except requests.exceptions.Timeout as e:
                logging.warning(f"Timeout error with {protocol.upper()} on port {port}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error with {protocol.upper()} on port {port}: {e}")

        # If we get here, all connection attempts failed
        raise ConnectionError(f"Failed to connect to PiHole API at {pihole_host} using any available protocol/port combination")

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

        # Build headers - only add session ID if we have one (authenticated)
        headers = {}
        if self.session.get('sid'):
            headers['X-FTL-SID'] = self.session.get('sid')
            logging.debug(f"Using authenticated request with SID: {self.session.get('sid')}")
        else:
            logging.debug("Using unauthenticated request (no SID)")

        logging.debug(f"headers: {headers}")

        # Configure SSL settings for the request
        ssl_verify = True if self.session.base_url.startswith('https') else None
        client_cert = self.session.config.get("pihole", "client_cert")

        try:
            if self.session.base_url.startswith('https'):
                if client_cert and os.path.exists(client_cert):
                    response = requests.get(metrics_url, headers=headers, cert=client_cert, verify=ssl_verify, timeout=10)
                else:
                    response = requests.get(metrics_url, headers=headers, verify=ssl_verify, timeout=10)
            else:
                # HTTP request
                response = requests.get(metrics_url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get metrics: HTTP {response.status_code}")
                logging.debug(f"Response text: {response.text}")
                return None

        except Exception as e:
            logging.error(f"Error getting metrics: {e}")
            return None