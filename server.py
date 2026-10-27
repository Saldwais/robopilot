"""Local phone remote. Simulation is the default; no serial imports until --hardware."""
import argparse
import json
import secrets
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from telemetry import CameraManager, PathTracker

DIRECTIONS = {
    'forward': (-1, 1), 'backward': (1, -1),
    'left': (1, 1), 'right': (-1, -1),
    'forward_left': (-0.5, 1), 'forward_right': (-1, 0.5),
    'backward_left': (0.5, -1), 'backward_right': (1, -0.5),
    'stop': (0, 0),
}

class SimDriver:
    def __init__(self):
        self.values = (0, 0)
        self.enabled = False
    def connect(self): pass
    def drive(self, left, right):
        self.enabled = True
        self.values = (left, right)
    def stop(self):
        self.values = (0, 0)
        self.enabled = False
    def close(self): self.stop()

class HardwareDriver:
    def __init__(self, port):
        from lerobot.motors import Motor, MotorNormMode
        from lerobot.motors.feetech import FeetechMotorsBus
        self.bus = FeetechMotorsBus(port, {str(i): Motor(i, 'sts3215', MotorNormMode.RANGE_M100_100) for i in (9, 10)})
        self.enabled = False
    def connect(self):
        self.bus.connect(handshake=False)
        self.bus.set_baudrate(1_000_000)
        try:
            for n in self.bus.motors:
                if self.bus.ping(n, raise_on_error=True) != 777:
                    raise RuntimeError('Expected STS3215 model 777')
            self.stop()
            for n in self.bus.motors:
                # Do not alter saved mode automatically or touch arm IDs.
                if self.bus.read('Operating_Mode', n, normalize=False) != 1:
                    raise RuntimeError(f'ID {n} is not in wheel mode')
        except Exception:
            self.close()
            raise
    def drive(self, left, right):
        if not self.enabled:
            for n in self.bus.motors:
                self.bus.write('Goal_Velocity', n, 0, num_retry=1)
                self.bus.write('Torque_Enable', n, 1, num_retry=1)
            self.enabled = True
        for n, speed in zip(self.bus.motors, (left, right)):
            self.bus.write('Goal_Velocity', n, speed, num_retry=1)
    def positions(self):
        return tuple(self.bus.read('Present_Position', n, normalize=False) for n in self.bus.motors)
    def stop(self):
        errors = []
        for n in self.bus.motors:
            for register in ('Goal_Velocity', 'Torque_Enable'):
                try:
                    self.bus.write(register, n, 0, num_retry=2)
                except Exception as exc:
                    errors.append(str(exc))
        self.enabled = False
        if errors:
            raise RuntimeError('STOP could not be confirmed. CUT 12V POWER. ' + '; '.join(errors))
    def close(self):
        if self.bus.is_connected:
            try:
                self.stop()
            finally:
                self.bus.disconnect(disable_torque=False)

class Controller:
    TIMEOUT = 0.35
    def __init__(self, driver, tracker=None):
        self.driver = driver
        self.lock = threading.RLock()
        self.connected = False
        self.armed = False
        self.owner = None
        self.sequence = -1
        self.deadline = 0
        self.target = (0, 0)
        self.applied = (0, 0)
        self.error = ''
        self.reason = 'Disconnected'
        self.was_driving = False
        self.tracker = tracker or PathTracker(simulated=isinstance(driver, SimDriver))
        self.last_tick = None
        self.last_sample = 0
    def stop(self, reason='Stopped'):
        self.target = (0, 0)
        self.armed = False
        self.owner = None
        self.reason = reason
        if self.connected:
            self.driver.stop()
        self.applied = (0, 0)
        self.was_driving = False
    def command(self, data, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            action = data.get('action')
            if action == 'connect':
                if not self.connected:
                    self.driver.connect()
                    self.connected = True
                    self.stop('Connected · disarmed')
                return
            if action == 'stop':
                self.stop()
                return
            if action == 'map_reset':
                if self.armed:
                    raise ValueError('Stop and disarm before resetting the map')
                self.tracker.reset()
                return
            if not self.connected or self.error:
                raise ValueError('Connect first; restart after a hardware error')
            client = data.get('client')
            if not isinstance(client, str) or not 8 <= len(client) <= 100:
                raise ValueError('Invalid controller identity')
            if action == 'arm':
                if self.owner and self.owner != client:
                    raise ValueError('Another device is armed. Press STOP first.')
                self.stop('Armed · hold a direction')
                self.owner = client
                self.sequence = -1
                self.armed = True
                self.deadline = now + self.TIMEOUT
                return
            if action != 'drive' or not self.armed or client != self.owner:
                raise ValueError('Press ARM first')
            if now > self.deadline:
                self.stop('Command timed out · disarmed')
                raise ValueError('Command expired. Press ARM again.')
            seq = data.get('seq')
            if type(seq) is not int or seq <= self.sequence:
                raise ValueError('Stale command')
            direction = data.get('direction')
            speed = data.get('speed')
            if direction not in DIRECTIONS or type(speed) is not int or not 0 <= speed <= 50:
                raise ValueError('Invalid direction or speed (0–50)')
            self.sequence = seq
            self.target = tuple(round(v * speed) for v in DIRECTIONS[direction])
            self.deadline = now + self.TIMEOUT
    def tick(self, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            dt = 0 if self.last_tick is None else min(max(now - self.last_tick, 0), 0.2)
            self.last_tick = now
            if self.tracker.simulated:
                self.tracker.integrate(*(v * dt for v in self.applied))
            if self.armed and now > self.deadline:
                self.stop('Command timed out · disarmed')
            if self.armed and self.target != self.applied:
                if self.target == (0, 0):
                    self.driver.stop()
                else:
                    self.driver.drive(*self.target)
                self.applied = self.target
            if self.connected and not self.tracker.simulated and now - self.last_sample >= 0.2:
                self.last_sample = now
                try:
                    self.tracker.update_ticks(*self.driver.positions())
                except Exception as exc:
                    self.tracker.error = 'Wheel position unavailable: ' + str(exc)
                    if self.armed:
                        raise
    def fail(self, exc):
        with self.lock:
            try:
                self.stop('Error · disarmed')
            except Exception as stop_exc:
                self.error = f'{exc}; {stop_exc}'
            else:
                self.error = str(exc)
    def state(self):
        with self.lock:
            return dict(connected=self.connected, armed=self.armed, target=self.target,
                        applied=self.applied, error=self.error, reason=self.reason, map=self.tracker.state())

def make_handler(controller, token, hardware, cameras=None):
    cameras = cameras or CameraManager()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass  # Never log access tokens.
        def respond(self, status, body, content='application/json'):
            payload = body if isinstance(body, bytes) else body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', content)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(payload)
        def authorized(self):
            return secrets.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token)
        def do_GET(self):
            path = urlsplit(self.path).path
            if path.startswith('/api/'):
                if not self.authorized():
                    return self.respond(401, {'error': 'Open the private link printed by the launcher'})
                if path == '/api/status':
                    return self.respond(200, dict(controller.state(), hardware=hardware, cameras=cameras.state()))
                if path in ('/api/cameras/0.jpg', '/api/cameras/1.jpg', '/api/cameras/2.jpg'):
                    frame = cameras.snapshot(int(path.split('/')[-1][0]))
                    return self.respond(200, frame, 'image/jpeg') if frame else self.respond(503, {'error':'No fresh camera frame'})
                return self.respond(404, {'error':'Not found'})
            files = {'/': ('index.html', 'text/html; charset=utf-8'),
                     '/app.js': ('app.js', 'application/javascript'), '/style.css': ('style.css', 'text/css')}
            if path not in files:
                return self.respond(404, {'error': 'Not found'})
            name, mime = files[path]
            self.respond(200, Path(__file__).with_name(name).read_text(encoding='utf-8'), mime)
        def do_POST(self):
            if self.path != '/api/command' or not self.authorized():
                return self.respond(403, {'error': 'Unauthorized'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.respond(403, {'error': 'Wrong origin'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 2048:
                    raise ValueError('Invalid request size')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Invalid request')
                if data.get('action') in ('cameras_start', 'cameras_stop'):
                    # Separate from wheel driver; camera failures cannot enable motors.
                    if data['action'] == 'cameras_start':
                        cameras.start()
                    else:
                        cameras.stop()
                else:
                    controller.command(data)
                self.respond(200, controller.state())
            except (ValueError, TypeError) as exc:
                self.respond(400, {'error': str(exc)})
            except Exception as exc:
                controller.fail(exc)
                self.respond(503, controller.state())
    return Handler

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--hardware', action='store_true')
    p.add_argument('--directions-verified', action='store_true')
    p.add_argument('--serial-port', default='COM7')
    p.add_argument('--bind', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--enable-cameras', action='store_true', help='Allow opening three local USB cameras after pressing Start cameras')
    p.add_argument('--camera-indices', default='0,1,2')
    p.add_argument('--wheel-radius', type=float, default=0.05, help='Uncalibrated stock assumption in metres')
    p.add_argument('--wheelbase', type=float, default=0.25, help='Uncalibrated stock assumption in metres')
    args = p.parse_args()
    if args.hardware and not args.directions_verified:
        p.error('Verify stock motor mounting/directions before using --hardware --directions-verified')
    token = secrets.token_urlsafe(24)
    tracker = PathTracker(args.wheel_radius, args.wheelbase, simulated=not args.hardware)
    controller = Controller(HardwareDriver(args.serial_port) if args.hardware else SimDriver(), tracker)
    try:
        indices = tuple(int(i) for i in args.camera_indices.split(','))
        if min(indices) < 0:
            raise ValueError('Camera indices must be nonnegative')
        cameras = CameraManager(indices, allowed=args.enable_cameras)
    except ValueError as exc:
        p.error(str(exc))
    server = ThreadingHTTPServer((args.bind, args.port), make_handler(controller, token, args.hardware, cameras))
    server.daemon_threads = True
    shutdown = threading.Event()
    def worker():
        while not shutdown.wait(0.04):
            try:
                controller.tick()
            except Exception as exc:
                controller.fail(exc)
    threading.Thread(target=worker, daemon=True).start()
    print('HARDWARE' if args.hardware else 'SIMULATION — no robot connection', flush=True)
    print(f'Laptop: http://127.0.0.1:{args.port}/#{token}', flush=True)
    if args.bind == '0.0.0.0':
        for ip in sorted({x[4][0] for x in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}):
            print(f'Phone (same trusted Wi-Fi): http://{ip}:{args.port}/#{token}', flush=True)
    print('Hold to drive. Release/STOP disarms. Network command timeout: 350 ms. Ctrl+C quits.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        shutdown.set()
        cameras.stop()
        with controller.lock:
            try:
                controller.stop('Shutdown')
            finally:
                controller.driver.close()
        server.server_close()

if __name__ == '__main__': main()
