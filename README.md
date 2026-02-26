# Door Opener LSCS

A Raspberry Pi-powered door opener service with a small Flask web/API layer and GPIO motor control.

This project exposes HTTP endpoints to open/close a door mechanism, verify whether it is open via a sensor button, and report lightweight status data. It is intended to run on a Raspberry Pi connected to a motor driver and RGB status LED.

## What this project does

- Controls a door motor through GPIO pins (`open` / `close`).
- Uses a physical button/sensor input to verify open-state.
- Exposes a Flask API for remote operations.
- Uses a time-based HMAC key for simple API authentication.
- Updates RGB LED state to indicate door status:
  - **Green** = open
  - **Red** = closed

## Repository structure

- `api/main.py` – Flask entry point.
- `api/website/__init__.py` – Flask app factory.
- `api/website/views.py` – Routes (UI + API) and auth logic.
- `api/website/templates/home.html` – Landing page template.
- `api/website/static/base.css` – UI styles.
- `control.py` – Hardware control layer (GPIO + motor + LED).
- `logs.py` – Terminal helper for reading/filtering log files.
- `requirements.txt` – Python dependencies.

## Hardware expectations

The code assumes these GPIO assignments (BCM mode):

- Motor driver:
  - `IN1 = 10`
  - `IN2 = 9`
  - `ENA = 25`
- Door position button/sensor:
  - `BTN = 14` (configured pull-up)
- RGB LED:
  - `R = 17`, `G = 27`, `B = 22`

> Update pin constants in `control.py` if your wiring differs.

## Software requirements

- Python 3.10+
- Raspberry Pi OS / Linux environment with GPIO support
- Packages in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file (or export variables in your shell):

```bash
FLASK_SECRET_KEY=change-me
API_SECRET_KEY=change-me-too
```

- `FLASK_SECRET_KEY` is used by Flask session/security internals.
- `API_SECRET_KEY` is used to generate a rolling HMAC auth key.

## Running the project

Start the web server:

```bash
python api/main.py
```

By default it binds to:

- Host: `0.0.0.0`
- Port: `4000`
- Debug: enabled

## How authentication works

Protected endpoints require `?key=<token>`.

Server-side key generation:

1. Take current UNIX time.
2. Divide into 60-second windows.
3. Compute `HMAC-SHA256(API_SECRET_KEY, time_window)`.
4. Compare request key with the generated key for the current window.

This means the key rotates every minute and client/server clocks must be reasonably in sync.

You can fetch the current server key at:

- `GET /key`

## API reference

### `GET /api/open?key=<token>`

Attempts to open the door.

Behavior:
- Starts motor in open direction.
- Waits until `Control.verified_open()` succeeds or timeout (10s).

Response:
- Success: `{"success": true}`
- Timeout: `{"success": false}`
- Unauthorized: `{"success": false, "error": "unauthorized"}` with 401

---

### `GET /api/close?key=<token>`

Attempts to close the door.

Behavior:
- Starts motor in close direction.
- Waits until sensor no longer indicates open, or timeout (10s).

Response mirrors `/api/open`.

---

### `GET /api/status?key=<token>`

Returns service/door status metadata.

Current response fields:
- `api` (bool)
- `opened` (bool)
- `position` (currently static placeholder)
- `power_supply` (currently estimated placeholder)
- `wifi_network` (currently static placeholder)
- `last_updated` (unix timestamp)

> Note: there is currently a route definition typo in code (`"api/status"` instead of `"/api/status"`) that may prevent this endpoint from registering as intended.

---

### Helper/debug endpoints (not authenticated)

- `GET /fopen` – force open motor action
- `GET /fclose` – force close motor action
- `GET /freset` – stop PWM and run GPIO cleanup

These are useful for local bring-up and should be protected/disabled in production.

## Internal flow overview

1. Flask receives request in `views.py`.
2. `@before_app_request` initializes GPIO through `Control.setup()`.
3. Route validates auth key (for protected routes).
4. Route invokes `Control.open()` / `Control.close()`.
5. Loop checks `Control.verified_open()` until success/failure timeout.
6. JSON response returned to caller.

## Development notes

- `RPi.GPIO` is hardware-specific; local non-Pi runs may fail unless mocked.
- The current code starts in Flask debug mode; change for production use.
- Consider running via `gunicorn` or `systemd` service for deployment stability.
- Consider rate limiting + TLS if exposed outside trusted LAN.

## Log utility (`logs.py`)

Run:

```bash
python logs.py
```

Features:
- Arrow-key menu navigation.
- Read full `logs.txt` file.
- Filter logs by IP address.

The “Date” option is scaffolded but currently not fully implemented.

## Safety and operations

- Test motor direction with short runs before full operation.
- Ensure driver power and wiring are correct before enabling.
- Always include a physical emergency override/disconnect when controlling doors.

## License

See `LICENSE`.
