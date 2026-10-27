# Local control only

Use only on a trusted private network. Do not port-forward or expose the server publicly. The local HTTP server uses a per-launch bearer token; HTTP does not encrypt camera or command traffic. Anyone with that token and network access can access live views and issue commands. Restarting changes the token. No cloud video uploads or recording are implemented.

Camera capture is disabled unless the launcher explicitly enables it and a user presses Start cameras. Stop cameras to release the devices. Default camera indices are placeholders, not verified device identities.

Control timeout, stop-on-release, and disarming are software mechanisms. They do not guarantee a stop during OS freezes, serial failures, disconnected USB, or hardware failures. A reachable physical motor-power cutoff is required. Never leave a powered moving robot unattended.

The map is relative encoder odometry, not SLAM, obstacle detection, collision avoidance, or autonomous navigation. Verify mounting, direction signs and wheel geometry physically before driving. SO-101 arms and grippers are locked/unimplemented in this release.

Do not publish private access links, camera photos, maps, logs, or local configuration in issue reports.
