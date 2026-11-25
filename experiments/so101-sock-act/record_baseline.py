"""Adapted from the Nov 18 historical pick-and-place recording command.
Not the later sent-action recorder; hardware execution has not been verified.
"""
import argparse
import json
import subprocess
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, default=Path.cwd())
    p.add_argument("--recorder", default="lerobot-record")
    p.add_argument("--camera0", type=int, default=0)
    p.add_argument("--camera1", type=int, default=1)
    p.add_argument("--name", default="socks-training-20")
    p.add_argument("--hardware-verified", action="store_true",
                   help="Confirm ports, calibrated arms, camera identities, clear workspace and physical cutoff.")
    a = p.parse_args()
    if not a.hardware_verified:
        p.error("Supervised recording requires --hardware-verified after physical checks.")
    if a.camera0 == a.camera1:
        p.error("Choose distinct verified camera indices.")
    if Path(a.name).name != a.name or a.name in ("", ".", ".."):
        p.error("Use a simple dataset folder name.")
    root = a.workspace.resolve() / "recordings" / a.name
    cal = a.workspace.resolve() / "calibration"
    for name in ("follower_com5.json", "leader_com3.json"):
        if not (cal / name).is_file():
            raise SystemExit(f"Missing verified calibration: {cal / name}")
    if root.exists():
        raise SystemExit(f"Dataset already exists: {root}")
    cameras = {f"camera{i}": {"type": "opencv", "index_or_path": idx,
                              "width": 640, "height": 480, "fps": 30}
               for i, idx in enumerate((a.camera0, a.camera1))}
    args = [a.recorder, "--robot.type=so101_follower", "--robot.port=COM5",
            "--robot.id=follower_com5", f"--robot.calibration_dir={cal}",
            "--robot.cameras=" + json.dumps(cameras), "--robot.max_relative_target=5",
            "--teleop.type=so101_leader", "--teleop.port=COM3", "--teleop.id=leader_com3",
            f"--teleop.calibration_dir={cal}", f"--dataset.repo_id=local/{a.name}",
            f"--dataset.root={root}", "--dataset.single_task=Pick up a sock and place it on the left side",
            "--dataset.num_episodes=20", "--dataset.episode_time_s=120",
            "--dataset.reset_time_s=15", "--dataset.fps=30", "--dataset.video=true",
            "--dataset.push_to_hub=false", "--display_data=false"]
    subprocess.run(args, check=True)

if __name__ == "__main__":
    main()
