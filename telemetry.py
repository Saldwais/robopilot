"""Relative wheel odometry and opt-in local camera capture. No SLAM or recording."""
import math
import threading
import time

class PathTracker:
    def __init__(self, radius=0.05, wheelbase=0.25, simulated=True):
        if not 0 < radius <= 1 or not 0 < wheelbase <= 3:
            raise ValueError('Wheel geometry must be positive and plausible (metres)')
        self.radius, self.wheelbase, self.simulated = radius, wheelbase, simulated
        self.reset()
    def reset(self):
        self.x = self.y = self.heading = 0.0
        self.previous = None
        self.points = [[0, 0]]
        self.updated = None
        self.error = ''
    def integrate(self, raw_left, raw_right):
        # Raw ID9 has the opposite sign because its mounting is mirrored.
        dl = -raw_left * (2 * math.pi / 4096) * self.radius
        dr = raw_right * (2 * math.pi / 4096) * self.radius
        distance, angle = (dl + dr) / 2, (dr - dl) / self.wheelbase
        self.x += distance * math.cos(self.heading + angle / 2)
        self.y += distance * math.sin(self.heading + angle / 2)
        self.heading = (self.heading + angle + math.pi) % (2 * math.pi) - math.pi
        if math.hypot(self.x - self.points[-1][0], self.y - self.points[-1][1]) > 0.002:
            self.points.append([round(self.x, 4), round(self.y, 4)])
            self.points = self.points[-2000:]
        self.updated = time.monotonic()
        self.error = ''
    def update_ticks(self, left, right):
        if self.previous is not None:
            delta = [((new - old + 2048) % 4096) - 2048 for new, old in zip((left, right), self.previous)]
            self.integrate(*delta)
        self.previous = (left, right)
        self.updated = time.monotonic()
    def state(self):
        return dict(x=round(self.x, 3), y=round(self.y, 3), heading=round(self.heading, 4),
                    points=self.points[:], simulated=self.simulated, error=self.error,
                    age=None if self.updated is None else round(time.monotonic() - self.updated, 1),
                    label='Simulated path · not real location' if self.simulated else 'Estimated wheel odometry · not SLAM',
                    radius=self.radius, wheelbase=self.wheelbase)

class CameraManager:
    NAMES = ('Head', 'Left wrist', 'Right wrist')
    def __init__(self, indices=(0, 1, 2), allowed=False, capture_factory=None):
        if len(indices) != 3 or len(set(indices)) != 3:
            raise ValueError('Use three different camera indices')
        self.indices, self.allowed = indices, allowed
        self.capture_factory = capture_factory
        self.lock = threading.Lock()
        self.halt = threading.Event()
        self.threads = []
        self.frames = [None] * 3
        self.errors = ['Off'] * 3
        self.times = [None] * 3
        self.running = False
    def start(self):
        if not self.allowed:
            raise ValueError('Live cameras disabled. Restart with --enable-cameras after confirming camera indices.')
        if self.running:
            return
        if any(t.is_alive() for t in self.threads):
            raise ValueError('Camera driver is still stopping; restart the server if it hangs')
        self.halt.clear()
        self.running = True
        with self.lock:
            self.frames = [None] * 3
            self.times = [None] * 3
            self.errors = ['Opening…'] * 3
        self.threads = [threading.Thread(target=self._capture, args=(slot,), daemon=True) for slot in range(3)]
        for t in self.threads:
            t.start()
    def _capture(self, slot):
        cap = None
        try:
            import cv2
            cap = self.capture_factory(self.indices[slot]) if self.capture_factory else cv2.VideoCapture(self.indices[slot])
            if not cap.isOpened():
                raise RuntimeError('Camera unavailable; check USB/index')
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
            cap.set(cv2.CAP_PROP_FPS, 10)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            while not self.halt.is_set():
                ok, frame = cap.read()
                if not ok:
                    raise RuntimeError('Camera frame unavailable')
                frame = cv2.resize(frame, (640, 360))
                ok, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 65])
                if not ok:
                    raise RuntimeError('JPEG encoding failed')
                with self.lock:
                    self.frames[slot] = jpeg.tobytes()
                    self.times[slot] = time.monotonic()
                    self.errors[slot] = ''
                self.halt.wait(0.15)
        except Exception as exc:
            with self.lock:
                self.errors[slot] = str(exc)
                self.frames[slot] = None
        finally:
            if cap is not None:
                cap.release()
    def snapshot(self, slot):
        with self.lock:
            if not self.running or self.times[slot] is None or time.monotonic() - self.times[slot] > 2:
                return None
            return self.frames[slot]
    def stop(self):
        self.running = False
        self.halt.set()
        for t in self.threads:
            t.join(timeout=0.3)
        with self.lock:
            self.frames = [None] * 3
            self.times = [None] * 3
            self.errors = ['Off'] * 3
    def state(self):
        with self.lock:
            now = time.monotonic()
            return [dict(slot=i, name=name, index=self.indices[i], running=self.running,
                         allowed=self.allowed, error=self.errors[i],
                         age=None if self.times[i] is None else round(now - self.times[i], 1))
                    for i, name in enumerate(self.NAMES)]
