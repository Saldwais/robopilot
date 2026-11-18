"""Pure-Python, ROS-independent differential/skid-steer kinematics."""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class DriveConfig:
    drive_type: str
    wheel_radius_m: float
    track_width_m: float
    max_wheel_rad_s: float = 8.0
    motor_ids: tuple[int, ...] = (9, 10)
    motor_signs: tuple[int, ...] = (-1, 1)

    def validate(self):
        if self.drive_type not in {"differential_2wd", "skid_4wd"}:
            raise ValueError("drive_type must be differential_2wd or skid_4wd")
        count = 2 if self.drive_type == "differential_2wd" else 4
        if len(self.motor_ids) != count or len(self.motor_signs) != count:
            raise ValueError(f"{self.drive_type} requires exactly {count} motor IDs and signs")
        if len(set(self.motor_ids)) != count or any(s not in (-1, 1) for s in self.motor_signs):
            raise ValueError("motor IDs must be unique and signs must be -1 or +1")
        if self.wheel_radius_m <= 0 or self.track_width_m <= 0 or self.max_wheel_rad_s <= 0:
            raise ValueError("geometry and speed limits must be positive")


def wheel_targets(linear_mps: float, angular_rps: float, config: DriveConfig) -> tuple[float, ...]:
    """Return motor angular rates in rad/s, in configured motor-ID order.

    Ordering: 2WD=(left,right); 4WD=(front_left,rear_left,front_right,rear_right).
    """
    config.validate()
    half_track = config.track_width_m / 2
    left = (linear_mps - angular_rps * half_track) / config.wheel_radius_m
    right = (linear_mps + angular_rps * half_track) / config.wheel_radius_m
    peak = max(abs(left), abs(right), config.max_wheel_rad_s)
    scale = min(1.0, config.max_wheel_rad_s / peak)
    if config.drive_type == "differential_2wd":
        physical = (left * scale, right * scale)
    else:
        physical = (left * scale, left * scale, right * scale, right * scale)
    return tuple(rate * sign for rate, sign in zip(physical, config.motor_signs))
