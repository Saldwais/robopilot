import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from drive_model import DriveConfig, wheel_targets

class DriveModelTests(unittest.TestCase):
    def test_two_wheel_straight(self):
        c = DriveConfig('differential_2wd', .1, .4, 10, (9,10), (-1,1))
        self.assertEqual(wheel_targets(.2, 0, c), (-2, 2))
    def test_four_wheel_straight_pairs(self):
        c = DriveConfig('skid_4wd', .1, .4, 10, (1,2,3,4), (1,1,1,1))
        self.assertEqual(wheel_targets(.2, 0, c), (2,2,2,2))
    def test_turn_left_has_left_right_differential(self):
        c = DriveConfig('skid_4wd', .1, .4, 10, (1,2,3,4), (1,1,1,1))
        left_front,left_rear,right_front,right_rear = wheel_targets(0, 1, c)
        self.assertLess(left_front, right_front)
        self.assertEqual(left_front,left_rear)
        self.assertEqual(right_front,right_rear)
    def test_limit(self):
        c = DriveConfig('differential_2wd', .05, .3, 4, (9,10), (1,1))
        self.assertLessEqual(max(map(abs,wheel_targets(10, 0, c))), 4)
    def test_invalid_motor_count(self):
        c = DriveConfig('skid_4wd', .05, .3, motor_ids=(9,10))
        with self.assertRaises(ValueError): wheel_targets(.1, 0, c)

if __name__ == '__main__': unittest.main()
