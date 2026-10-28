# RoboPilot — Saleh Aldwais: setup for today

## Before connecting the robot

1. Pair your Xbox controller to the laptop using Windows Bluetooth settings, a compatible Xbox Wireless Adapter, or USB. This is not a Wi-Fi controller connection.
2. Start RoboPilot in simulation using START_PHONE_PREVIEW.cmd (or `python server.py`).
3. Open the printed LAPTOP `http://127.0.0.1:8765/#...` link in Edge or Chrome. The browser window must remain open, visible and focused for controller driving. Do not minimize it while operating.
4. Press a controller button once so the browser detects it. Click Connect wheels (simulation), then Use Xbox. If no controller appears, release buttons, press A once, and click Use Xbox again.
5. Centre the left stick and release LB/A/B. Press A again to arm. Hold LB, then move the left stick. Up/down drives forward/back, left/right steers; diagonal stick positions curve. The simulated map should respond.
6. Release LB: stops AND disarms. Centre the stick, release LB, press A to rearm. B always stops/disarms. Reconnecting the controller never arms automatically.

This is a wheel-only controller. Right stick and triggers do not move arms or grippers. No arm motion before calibration. Maximum speed remains capped at raw 50; default is 10. There is no automatic speed increase from gamepad buttons.

## At home with the robot

1. Keep robot power OFF while checking secure mounts, wheel clearance, and cables. Laptop rides in the basket with ventilation and securely managed USB leads.
2. Connect motor boards by USB. Confirm current ports: previously COM7 was right arm + wheel IDs 9/10; COM8 left arm + head. Disconnect Bambot before opening serial from RoboPilot.
3. Verify wheel directions with wheels securely raised, and measure wheel radius/spacing for map distances. Stock mirrored signs: ID9 negative / ID10 positive is forward; confirm physically.
4. Start hardware mode ONLY after directions are verified, using the README command. Connect wheels starts disarmed and addresses IDs 9/10 only. Keep a reachable 12V cutoff; no software watchdog is a guaranteed emergency stop.
5. Repeat neutral A → hold LB → small stick movement. Release LB. Verify visible stopping before any short floor-driving test.
6. Connect the three USB cameras. Device indices are not yet known; the laptop webcam may occupy index 0. Enable cameras with the correct indices and check all three labels/views; no recording.
7. Test phone access on trusted Wi-Fi using its printed URL. To switch from Xbox to phone/keys, stop first and click Use phone / keys; another client must explicitly rearm.
8. Calibrate arms separately before implementing/testing any arm or gripper controls.

## If Xbox is not detected

- Gamepad API requires a secure browser context. Localhost is suitable; ordinary HTTP to the laptop's Wi-Fi IP may not expose gamepad input. Use the laptop localhost link for Xbox, phone Wi-Fi URL for touch buttons.
- Confirm Windows sees the controller using Win+R → `joy.cpl` → Properties.
- Press a controller button with the browser focused, then Use Xbox.
- Only standard mappings are accepted. No controller hardware was connected/tested during development.
- Controller pairing loss, focus loss and heartbeat expiry request/attempt stop. A lost serial link or frozen OS may prevent it; cut external motor power if needed.

References: [Microsoft controller connection guide](https://support.xbox.com/en-US/help/hardware-network/controller/connect-xbox-wireless-controller-to-pc), [Browser Gamepad API](https://developer.mozilla.org/en-US/docs/Web/API/Gamepad_API/Using_the_Gamepad_API).
