import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from server import Controller, SimDriver, make_handler
from telemetry import CameraManager, PathTracker

class MapTests(unittest.TestCase):
    def test_mirrored_forward(self):
        m=PathTracker(); m.integrate(-100,100)
        self.assertGreater(m.x,0); self.assertAlmostEqual(m.y,0); self.assertAlmostEqual(m.heading,0)
    def test_left_rotation(self):
        m=PathTracker(); m.integrate(100,100)
        self.assertAlmostEqual(m.x,0); self.assertGreater(m.heading,0)
    def test_encoder_wrap(self):
        m=PathTracker(simulated=False); m.update_ticks(6,4090); m.update_ticks(4090,6)
        self.assertGreater(m.x,0); self.assertLess(m.x,.01)
    def test_reset_rebases_encoders(self):
        m=PathTracker(); m.update_ticks(1,1); m.reset(); m.update_ticks(200,200)
        self.assertEqual(m.x,0); self.assertEqual(m.points,[[0,0]])
    def test_geometry_validation(self):
        with self.assertRaises(ValueError): PathTracker(radius=0)

class CameraTests(unittest.TestCase):
    def test_default_does_not_open_cameras(self):
        c=CameraManager()
        with self.assertRaises(ValueError): c.start()
        self.assertEqual(c.threads,[])
    def test_three_distinct_sources(self):
        with self.assertRaises(ValueError): CameraManager((0,0,1))
    def test_reject_stale_frame(self):
        c=CameraManager(); c.running=True;c.frames[0]=b'old';c.times[0]=time.monotonic()-5
        self.assertIsNone(c.snapshot(0))
    def test_stop_clears_frames(self):
        c=CameraManager();c.running=True;c.frames[0]=b'frame';c.times[0]=time.monotonic();c.stop()
        self.assertIsNone(c.snapshot(0));self.assertFalse(c.running)

class AuthTests(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(Controller(SimDriver()),'test-key',False))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def test_cameras_require_auth(self):
        with self.assertRaises(HTTPError) as e: urlopen(self.url+'/api/cameras/0.jpg')
        self.assertEqual(e.exception.code,401)
    def test_status_requires_auth(self):
        with self.assertRaises(HTTPError) as e: urlopen(self.url+'/api/status')
        self.assertEqual(e.exception.code,401)
    def test_cross_origin_command_rejected(self):
        r=Request(self.url+'/api/command',data=b'{"action":"connect"}',headers={'Authorization':'Bearer test-key','Origin':'http://other.example'})
        with self.assertRaises(HTTPError) as e: urlopen(r)
        self.assertEqual(e.exception.code,403)
    def test_camera_start_disabled_by_default(self):
        r=Request(self.url+'/api/command',data=b'{"action":"cameras_start"}',headers={'Authorization':'Bearer test-key'})
        with self.assertRaises(HTTPError) as e: urlopen(r)
        self.assertEqual(e.exception.code,400)

if __name__=='__main__':unittest.main()
