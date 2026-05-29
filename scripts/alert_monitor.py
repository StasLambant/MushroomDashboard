#This script monitors humidity levels and sends Telegram alerts when thresholds are breached.
# scripts/alert_monitor.py

import time
from datetime import datetime
import requests
import get_sensor_data
import os
import app

last_alert_time = 0
thermocouple_target_reached = False  # Track if target temperature has been reached

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Missing Telegram credentials in config.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
        else:
            print("✅ Telegram alert sent.")
    except Exception as e:
        print(f"Telegram exception: {e}")

def alert_monitor():
    global last_alert_time, thermocouple_target_reached

    while True:
        config = app.load_config()

        lower = config.get("lower", 60)
        upper = config.get("upper", 70)
        alert_threshold = config.get("alert_threshold", 5)
        cooldown = config.get("alert_cooldown", 15)
        thermocouple_target = config.get("thermocouple_target", 25)
        thermocouple_cooldown = config.get("thermocouple_cooldown", 20)

        try:
            _, humidity = get_sensor_data.get_sensor_data()
            thermocouple_temp = get_sensor_data.get_thermocouple_temp()

            # Humidity alerting (existing logic)
            if humidity is not None:
                lower_limit = lower - alert_threshold
                upper_limit = upper + alert_threshold
                now = time.time()

                if humidity < lower_limit or humidity > upper_limit:
                    if now - last_alert_time >= cooldown:
                        message = f"🚨 Humidity Alert: {humidity:.1f}% RH (outside {lower_limit}-{upper_limit}%)"
                        send_telegram_alert(message)
                        last_alert_time = now
                        print(f"[{datetime.now()}] ALERT SENT: {message}")
            else:
                print("Humidity read failed in alert_monitor.")

            # Thermocouple alerting (new logic)
            if thermocouple_temp is not None:
                now = time.time()

                if not thermocouple_target_reached and thermocouple_temp >= thermocouple_target:
                    # Target temperature reached - alert to turn off heating
                    if now - last_alert_time >= cooldown:
                        message = f"🔥 Thermocouple Alert: Target temperature reached! {thermocouple_temp:.1f}°C (≥ {thermocouple_target}°C). Turn off heating now!"
                        send_telegram_alert(message)
                        last_alert_time = now
                        thermocouple_target_reached = True
                        print(f"[{datetime.now()}] TARGET ALERT SENT: {message}")

                elif thermocouple_target_reached and thermocouple_temp <= thermocouple_cooldown:
                    # Cooled down to safe handling temperature
                    if now - last_alert_time >= cooldown:
                        message = f"❄️ Thermocouple Alert: Cooled to safe temperature! {thermocouple_temp:.1f}°C (≤ {thermocouple_cooldown}°C). Safe for handling."
                        send_telegram_alert(message)
                        last_alert_time = now
                        thermocouple_target_reached = False  # Reset for next heating cycle
                        print(f"[{datetime.now()}] COOLDOWN ALERT SENT: {message}")

            else:
                print("Thermocouple read failed in alert_monitor.")

        except Exception as e:
            print(f"Error in alert_monitor: {e}")

        time.sleep(5)

def run_alert_monitor():
    alert_monitor()
