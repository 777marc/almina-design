# Lightsail Runtime Layout

The bootstrap script installs and manages the app in these locations:

- App root: `/opt/almina-design`
- Current checkout: `/opt/almina-design/current`
- Shared env file: `/opt/almina-design/shared/.env`
- Virtualenv: `/opt/almina-design/.venv`
- Systemd unit: `/etc/systemd/system/almina-design.service`
- Nginx site: `/etc/nginx/sites-available/almina-design`

Useful commands after SSH:

```bash
sudo systemctl status almina-design
sudo journalctl -u almina-design -n 200 --no-pager
sudo systemctl restart almina-design
sudo nginx -t
```
