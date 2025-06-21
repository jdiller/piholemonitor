# PiHole Monitor

A Python daemon that monitors PiHole v6 API and sends metrics to Datadog via StatsD.

## Configuration

The application uses a configuration file (`config.ini`) with the following sections:

### PiHole Settings
- **host**: PiHole server hostname or IP
- **protocol**: Connection protocol (`auto`, `http`, or `https`)
  - `auto`: Try HTTPS first, fallback to HTTP
  - `https`: Force HTTPS connection
  - `http`: Force HTTP connection
- **port**: Custom port (optional)
  - Leave blank for protocol defaults (443 for HTTPS, 80 for HTTP)
  - Specify custom port if your PiHole runs on non-standard ports
- **password**: PiHole admin password (optional)
  - Leave blank if PiHole authentication is disabled
  - Required only if you need access to authenticated endpoints
- **client_cert**: Path to client certificate file (for client cert authentication)

### Datadog Settings
- **statsd_host**: StatsD server hostname
- **statsd_port**: StatsD server port

Copy `config.ini.sample` to `config.ini` and customize for your environment.

## Docker Usage

### Build the Image

```bash
docker build -t pihole-monitor .
```

### Run with Docker Compose (Recommended)

1. Create your configuration directory:
```bash
mkdir -p config certs
```

2. Place your configuration files in `./config/`
3. Place your client certificates in `./certs/`
4. Start the service:

```bash
docker-compose up -d
```

### Run with Docker Command

```bash
docker run -d \
  --name pihole-monitor \
  --restart unless-stopped \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/certs:/app/certs:ro \
  pihole-monitor
```

### Configuration

The application expects configuration files in `/app/config/` within the container. Make sure your `localconfig` module can find the configuration files.

Your client certificates should be placed in `/app/certs/` and referenced in your configuration accordingly.

### Logs

View logs with:
```bash
docker-compose logs -f pihole-monitor
# or
docker logs -f pihole-monitor
```

### Health Check

The container includes a health check that verifies the Python process is running. Check status with:
```bash
docker-compose ps
# or
docker ps
```