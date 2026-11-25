# Experiment log — 2026-11-24

## Recorded results
- November 18: initial recording experiments encountered invalid robot type, PowerShell JSON quoting, and camera capture errors. The explicit Python argument-list launcher was developed to avoid shell quoting problems.
- November 24: two source datasets merged successfully into 20 episodes / 35,974 frames at 15 FPS. Initial merge attempts failed because a pasted second command contaminated a boolean flag and because repository IDs and roots were parsed with unequal lengths. A Python sys.argv wrapper resolved the merge.
- CPU smoke test: 20 optimization steps reached completion, but updating the `last` checkpoint symlink raised Windows WinError 1314. Inspect the numbered checkpoint and resolve permissions before assuming checkpointing succeeded. PyAV was used because torchcodec was unavailable. The accelerate dependency was initially missing.
- Later baseline reported by the author: 5,000 ACT steps in about 4 h 53 min; training loss 49.695 → 0.903. Checkpoint location: `outputs/act-socks-cpu-5000/checkpoints/005000/pretrained_model`. Checkpoint contents and full run configuration have not been uploaded or independently inspected.
- Reported offline mean joint error, in dataset joint order: [5.98, 8.362, 17.969, 10.534, 10.24, 2.546]. Units and held-out status are not established here.
- Reported supervised 10-second autonomous rollouts and automatic return worked; elbow/gripper safety clamping occurred. Sock pickup and pair matching were not confirmed.
- Additional training is underway according to the author; new results pending.

## Next evaluation
Record the actual configuration, model step, wall time, loss, dataset version, split and trial outcomes. Evaluate novel sock placements and paired/unpaired socks separately. Report full task completion over the number of trials, pickup success, correct sorting, and safety interventions. Do not infer physical success from training loss alone.

| Checkpoint | Trials | Pickup successes | Correct sort | Complete task | Safety interventions |
| --- | --- | --- | --- | --- | --- |
| 005000 | Not recorded | Unconfirmed | Unconfirmed | Unconfirmed | Clamping observed |
| Next run | Pending | Pending | Pending | Pending | Pending |

## Pending upload
- Original sent-action recording, calibration-aware rollout/home-return and offline-evaluation source scripts.
- Exact environment lock and training configuration.
- Model checkpoint, training logs, representative images and demonstration videos after privacy review.
- Raw dataset link, if approved for publication.
