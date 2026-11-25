# SO-101 Sock Sorting — ACT Learning Experiment

**Author:** Saleh Aldwais · November 2026  
**Status:** Work in progress; physical task success has not been validated.

## Goal
Teach an SO-101 follower arm through leader–follower demonstrations to pick up socks, identify matching pairs and sort unmatched socks into a marked left-side area. The initial recording task was the simpler sock-pick-and-place primitive. Pair matching is a target, not a demonstrated capability.

## Hardware and data
- SO-101 leader: COM3; follower: COM5; six joint positions/actions.
- Final training camera layout (reported): camera0 = OpenCV index 2 (arm view); camera1 = index 0 (overhead).
- Earlier recording configuration used indices 0 and 1 at 30 FPS. Do not interchange these without checking actual camera identity.
- Merged dataset: local/socks-act-merged-20, LeRobot dataset v3.0, 20 episodes, 35,974 frames, 15 FPS, two 640 x 480 RGB video streams (H.264).
- Source recordings: socks-sent-actions-20261122-213531-301002 and socks-sent-actions-20261122-223119-755593.
- Action/state fields: shoulder_pan.pos, shoulder_lift.pos, elbow_flex.pos, wrist_flex.pos, wrist_roll.pos, gripper.pos.

## Learning pipeline
1. Verify hardware, calibration and camera ordering.
2. Record supervised leader–follower demonstrations.
3. Merge the two recorded sessions using the local LeRobot dataset editor.
4. Train Action Chunking Transformer (ACT) offline using the merged dataset.
5. Compare offline predictions with recorded joint actions.
6. Evaluate short supervised hardware rollouts and log actual task completion.

## Repository contents
- `record_baseline.py`: reconstructed historical recording launcher, with explicit hardware verification and configurable paths. Not the later sent-action recorder.
- `merge_sessions.py`: portable version of the successful November 24 merge command.
- `train_act.py`: portable launcher based on the documented 20-step CPU smoke-test command; optionally run longer training. Not a verified exact reproduction of the 5,000-step configuration.
- `RESULTS.md`: known results, troubleshooting and next evaluation checklist.
- `dataset_summary.json`: extracted dataset metadata summary, not the raw dataset.
- `.gitignore`: excludes raw videos, calibration and model outputs.

## Running from the existing xleRobot workspace
Use the same Python environment as the original LeRobot installation. The exact dependency lock and version are not yet recovered. Install the appropriate LeRobot training dependencies in an isolated environment if needed; the initial run specifically required accelerate. The original workspace had recordings under `RO 101 Leader Follower/recordings`.

From that workspace, run the scripts by their full path:
```powershell
python <script-path>/merge_sessions.py --recordings "RO 101 Leader Follower/recordings"
python <script-path>/train_act.py --dataset "RO 101 Leader Follower/recordings/socks-act-merged-20" --output outputs/act-socks-reproduction-test
```
If the merged dataset already exists, do not merge again. Use a new output path so earlier checkpoints are preserved. The scripts here have not been executed against the user's actual robot or environment.

## Safety
These scripts are research tools, not a validated autonomous controller. Use supervised operation only, with a clear workspace, verified calibration, reachable physical motor-power cutoff and low-risk test objects. Do not bypass position clamping or run an unvalidated policy unattended.

## Publication scope
The original local source tree, calibration, raw videos, model weights and latest in-progress run are not accessible in this upload session. The scripts are recovered/adapted from prior console records, not claimed to be the complete original source. Raw recordings and checkpoints should be reviewed for privacy and published separately with a suitable large-file or model/dataset hosting workflow. No external upload of the raw data is performed.
