## Weather App (Flask + OpenWeather)

A simple Flask app that fetches current weather by city using the OpenWeather API. Includes a responsive Bootstrap UI, error handling, and Docker support.

### Prerequisites
- Python 3.8+
- OpenWeather API key

### Configuration
Set the API key via environment variable (recommended):

```bash
export OPENWEATHER_API_KEY="YOUR_API_KEY"
```

Alternatively, it will fall back to the value in `var.py` (`key`).

### Run Locally
```bash
pip install -r requirements.txt
export OPENWEATHER_API_KEY="YOUR_API_KEY"
python app.py
```
App runs at `http://localhost:8080`.

### Docker
Build and run:
```bash
docker build -t weather-app .
docker run -p 8080:8080 -e OPENWEATHER_API_KEY="YOUR_API_KEY" weather-app
```

### Notes
- Uses HTTPS for API calls.
- Displays descriptive errors returned by OpenWeather when applicable.
- UI shows weather icon, temperature, humidity, wind, pressure, and feels-like.

## AWS CI/CD: GitHub → CodePipeline → CodeDeploy → EC2

This repo includes files to deploy automatically to an EC2 instance via AWS CodePipeline and CodeDeploy.

### What’s included
- `appspec.yml`: CodeDeploy configuration and lifecycle hooks
- `buildspec.yml`: CodeBuild artifact packaging (used by CodePipeline)
- `scripts/`:
  - `install_dependencies.sh`: Creates venv and installs Python deps
  - `configure_systemd.sh`: Installs `weather.service` for systemd
  - `start_server.sh` / `stop_server.sh`: Manage the service
  - `validate_service.sh`: Health check on `http://localhost:8080`

### EC2 instance prerequisites
- Amazon Linux 2 or Ubuntu with `systemd`
- Instance profile with CodeDeploy permissions
- CodeDeploy agent installed and running
- Security group allows inbound TCP 8080 (or change the port in service file)

### Configure environment variables
Put secrets in `/etc/sysconfig/weather` on the EC2 host (created by script):
```
OPENWEATHER_API_KEY=YOUR_API_KEY
```
Then run:
```
sudo systemctl daemon-reload
sudo systemctl restart weather.service
```

### CodePipeline (high-level)
1. Create an S3 bucket for artifacts.
2. Create a CodeBuild project using this repo; use `buildspec.yml`.
3. Create a CodeDeploy application (Compute platform: EC2/On-Premises) and a Deployment group targeting the EC2 instance (using tags or Auto Scaling group).
4. Create a CodePipeline:
   - Source: GitHub repo
   - Build: CodeBuild project above
   - Deploy: CodeDeploy application/group above

Deployments will copy the repo to `/home/ec2-user/weather-app`, create a venv, install deps, write a `systemd` unit, start the service with `gunicorn`, and validate via HTTP.
