"""Adapted CPU smoke-test configuration, not the exact later long-run config."""
import argparse
import subprocess
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--batch-size", type=int, default=2)
    p.add_argument("--save-freq", type=int, default=20)
    a = p.parse_args()
    if min(a.steps, a.batch_size, a.save_freq) <= 0:
        p.error("Steps, batch size and save frequency must be positive.")
    if not (a.dataset / "meta" / "info.json").is_file():
        p.error("Dataset metadata not found.")
    if a.output.exists():
        p.error("Use a new output directory; will not overwrite.")
    args = ["lerobot-train", "--dataset.repo_id=local/socks-act-merged-20",
            f"--dataset.root={a.dataset.resolve()}", "--dataset.video_backend=pyav",
            "--policy.type=act", f"--policy.device={a.device}",
            "--policy.push_to_hub=false", f"--output_dir={a.output.resolve()}",
            "--job_name=act_socks_reproduction", f"--batch_size={a.batch_size}",
            f"--steps={a.steps}", "--num_workers=0", "--log_freq=1",
            f"--save_freq={a.save_freq}", "--wandb.enable=false"]
    subprocess.run(args, check=True)

if __name__ == "__main__":
    main()
