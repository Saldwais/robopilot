"""Small reactive point-to-point planner; no occupancy map or SLAM."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class VelocityCommand:
    linear_x: float
    angular_z: float
    state: str

class MaplessPlanner:
    def __init__(self, stop_distance=0.55, goal_tolerance=0.25, max_linear=0.18, max_angular=0.65, robot_radius=0.22):
        if stop_distance <= 0 or goal_tolerance <= 0 or max_linear <= 0 or max_angular <= 0:
            raise ValueError('planner distances and speed limits must be positive')
        self.stop_distance = stop_distance
        self.goal_tolerance = goal_tolerance
        self.max_linear = max_linear
        self.max_angular = max_angular
        self.robot_radius = robot_radius

    @staticmethod
    def wrap(a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def plan(self, goal_dx, goal_dy, ranges, angle_min, angle_increment, range_max=12.0):
        if not ranges or not math.isfinite(goal_dx) or not math.isfinite(goal_dy):
            return VelocityCommand(0.0, 0.0, 'invalid_input')
        distance = math.hypot(goal_dx, goal_dy)
        if distance <= self.goal_tolerance:
            return VelocityCommand(0.0, 0.0, 'goal_reached')
        target = math.atan2(goal_dy, goal_dx)
        bins = []
        blocked = []
        for i, r in enumerate(ranges):
            angle = self.wrap(angle_min + i * angle_increment)
            safe_range = float(r) if math.isfinite(float(r)) else range_max
            if safe_range >= self.stop_distance:
                bins.append(angle)
            else:
                blocked.append((angle, safe_range))
        # Inflate each obstacle by the robot footprint, preventing a near-zero
        # angular detour that still clips the chassis.
        safe_bins = [a for a in bins if all(abs(self.wrap(a-obstacle)) > math.atan2(self.robot_radius, max(r, 0.05)) for obstacle, r in blocked)]
        if not safe_bins:
            return VelocityCommand(0.0, 0.0, 'blocked')
        # Pick the clear beam closest to the goal direction; when equally close,
        # prefer more clearance. The result remains reactive and mapless.
        best = min(safe_bins, key=lambda a: (abs(self.wrap(a - target)), -self._range_at(a, ranges, angle_min, angle_increment, range_max)))
        error = self.wrap(best - target)
        angular = max(-self.max_angular, min(self.max_angular, 1.8 * best))
        alignment = max(0.0, math.cos(error))
        clearance = self._range_at(best, ranges, angle_min, angle_increment, range_max)
        linear = self.max_linear * alignment * min(1.0, max(0.0, clearance - self.stop_distance))
        direct_blocked = any(abs(self.wrap(target-a)) <= math.atan2(self.robot_radius, max(r, 0.05)) for a,r in blocked)
        state = 'driving' if not direct_blocked and abs(error) < 0.45 and clearance > self.stop_distance else 'avoiding_obstacle'
        return VelocityCommand(linear, angular, state)

    @staticmethod
    def _range_at(angle, ranges, angle_min, angle_increment, range_max):
        if not angle_increment:
            return range_max
        idx = round((angle - angle_min) / angle_increment)
        idx = max(0, min(len(ranges) - 1, idx))
        r = float(ranges[idx])
        return r if math.isfinite(r) else range_max
