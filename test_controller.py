import unittest
from server import Controller, SimDriver

class ControlTests(unittest.TestCase):
    def setUp(self):
        self.driver = SimDriver()
        self.c = Controller(self.driver)
        self.c.command({'action':'connect'}, now=1)
    def arm(self): self.c.command({'action':'arm','client':'test-client'}, now=1)
    def drive(self, **updates):
        d = dict(action='drive',client='test-client',seq=1,direction='forward',speed=10)
        d.update(updates)
        self.c.command(d, now=1.1)
        self.c.tick(now=1.1)
    def test_no_drive_until_armed(self):
        with self.assertRaises(ValueError): self.drive()
        self.assertEqual(self.driver.values,(0,0))
    def test_mirrored_forward(self):
        self.arm(); self.drive()
        self.assertEqual(self.driver.values,(-10,10))
    def test_curve(self):
        self.arm(); self.drive(direction='forward_left',speed=20)
        self.assertEqual(self.driver.values,(-10,20))
    def test_timeout_stops_and_disarms(self):
        self.arm(); self.drive(); self.c.tick(now=1.46)
        self.assertEqual(self.driver.values,(0,0)); self.assertFalse(self.c.armed)
        self.assertFalse(self.driver.enabled)
    def test_stop_cannot_be_revived_by_delayed_message(self):
        self.arm(); self.drive(); self.c.command({'action':'stop'})
        with self.assertRaises(ValueError): self.drive(seq=2)
        self.assertFalse(self.driver.enabled)
    def test_expired_lease_cannot_be_renewed(self):
        self.arm()
        with self.assertRaises(ValueError):
            self.c.command(dict(action='drive',client='test-client',seq=1,direction='forward',speed=10),now=2)
        self.assertFalse(self.c.armed)
    def test_other_phone_cannot_take_over(self):
        self.arm()
        with self.assertRaises(ValueError): self.drive(client='another-phone')
    def test_speed_limit(self):
        self.arm()
        with self.assertRaises(ValueError): self.drive(speed=51)
    def test_stale_sequence(self):
        self.arm(); self.drive()
        with self.assertRaises(ValueError): self.drive()
    def test_analog_forward(self):
        self.arm();self.drive(throttle=1,turn=0,speed=50)
        self.assertEqual(self.driver.values,(-50,50))
    def test_analog_right(self):
        self.arm();self.drive(throttle=0,turn=-1,speed=10)
        self.assertEqual(self.driver.values,(-10,-10))
    def test_analog_normalizes_combined_stick(self):
        self.arm();self.drive(throttle=1,turn=1,speed=50)
        self.assertEqual(self.driver.values,(0,50))
    def test_analog_reject_nan(self):
        self.arm()
        with self.assertRaises(ValueError):self.drive(throttle=float('nan'),turn=0)
    def test_analog_reject_out_of_range(self):
        self.arm()
        with self.assertRaises(ValueError):self.drive(throttle=2,turn=0)
    def test_analog_still_expires(self):
        self.arm();self.drive(throttle=1,turn=.2);self.c.tick(now=1.46)
        self.assertEqual(self.driver.values,(0,0));self.assertFalse(self.c.armed)

if __name__ == '__main__': unittest.main()
