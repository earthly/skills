# Systemd Configuration

Systemd is a system and service manager for Linux that provides a standardized
way to define and control how services start, stop, and behave on boot.

For Lunar, systemd may be used to ensure that the application is reliably managed,
automatically started at boot, and cleanly shut down or reloaded when needed.

Here's a simple systemd unit file that will run `lunar` in a resilient way.

```ini
[Unit]
Description=Lunar CI Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu
ExecStart=/usr/local/bin/lunar
EnvironmentFile=/etc/lunar.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
