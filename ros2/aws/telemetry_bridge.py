"""Optional AWS IoT Core telemetry publisher. No command subscription/control."""
import json, os, ssl, time
from datetime import datetime, timezone

class AwsTelemetry:
    def __init__(self):
        import paho.mqtt.client as mqtt
        self.endpoint = os.environ['AWS_IOT_ENDPOINT']
        self.device_id = os.environ['ROBOT_DEVICE_ID']
        self.topic = f"robopilot/{self.device_id}/telemetry"
        ca, cert, key = (os.environ[k] for k in ('AWS_CA_FILE','AWS_CERT_FILE','AWS_PRIVATE_KEY_FILE'))
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.device_id, protocol=mqtt.MQTTv311)
        self.client.tls_set(ca_certs=ca, certfile=cert, keyfile=key, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        self.client.connect(self.endpoint, 8883, keepalive=30)
        self.client.loop_start()

    def publish(self, drive_type, mode, wheel_rates, odom, scan_ranges, estop, command_age_ms):
        finite = [x for x in scan_ranges if isinstance(x,(float,int)) and 0 < x < float('inf')]
        payload = {'schema_version':'1.0','device_id':self.device_id,
            'timestamp':datetime.now(timezone.utc).isoformat(), 'drive_type':drive_type,'mode':mode,
            'wheel_rates_rad_s':wheel_rates,'odom':odom,
            'lidar_min_range_m':min(finite) if finite else None,
            'estop':bool(estop),'command_age_ms':command_age_ms}
        self.client.publish(self.topic, json.dumps(payload), qos=1, retain=False)

    def close(self):
        self.client.loop_stop(); self.client.disconnect()
