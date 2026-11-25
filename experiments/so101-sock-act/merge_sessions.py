"""Portable adaptation of the successful Nov 24 merge."""
import argparse
import json
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recordings", required=True, type=Path)
    p.add_argument("--session1", default="socks-sent-actions-20261122-213531-301002")
    p.add_argument("--session2", default="socks-sent-actions-20261122-223119-755593")
    a = p.parse_args()
    root = a.recordings.resolve()
    sources = [root / a.session1, root / a.session2]
    out = root / "socks-act-merged-20"
    for source in sources:
        if not source.is_dir():
            raise SystemExit(f"Missing source: {source}")
    if sources[0] == sources[1]:
        raise SystemExit("Sources must be distinct.")
    if out.exists():
        raise SystemExit(f"Output exists; will not overwrite: {out}")
    from lerobot.scripts.lerobot_edit_dataset import main as edit
    sys.argv = [
        "lerobot-edit-dataset", "--operation.type=merge",
        "--operation.repo_ids=" + json.dumps(["local/session1", "local/session2"]),
        "--operation.roots=" + json.dumps([str(s) for s in sources]),
        "--new_repo_id=local/socks-act-merged-20", "--new_root=" + str(out),
        "--operation.concatenate_videos=false", "--operation.concatenate_data=false",
        "--push_to_hub=false",
    ]
    edit()
    print((out / "meta" / "info.json").read_text())

if __name__ == "__main__":
    main()
