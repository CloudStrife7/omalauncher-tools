# Turn your phone's home screen into a TV remote (no TV remote needed)

How I paired my phone to a Sony Android TV over Wi-Fi and put a remote widget on omalauncher, with Claude doing the typing.

## Who this is for and what it does

**For:** You have an Android TV or Google TV (I used a Sony BRAVIA X900F) and an Android phone running [omalauncher](https://github.com/SimonSchubert/omalauncher). You can run Claude Code in the launcher's terminal. The TV and the phone are on the same Wi-Fi.

**What it does:** Your phone becomes a TV remote. The widget has a D-pad, OK, back, home, volume, play and power. It talks to the TV's own network remote port, so the TV needs no mods and no root.

**What you get:** A `tv-remote` command, a `tv.owl` widget, and a pairing that lasts. Plus a way to press any TV button from a PC when the real remote is lost or dead.

**Time:** about 15 minutes. Mine took longer because of the pairing gotchas below.

## When to skip

- **You have a working remote.** (lol) Use it. The TV's own remote is better.
- **The Google TV app on your phone already finds your TV.** It already does this job. Use that app.
- **Your TV is not Android TV or Google TV.** This talks to the Android TV remote port (6466/6467). Roku, Fire TV and others use something else.
- **You want to speed up the TV itself.** This is a remote, not a tune-up. (It is a first step: once you can press buttons, you can open the TV's Developer options. I did not finish that part, so this guide does not cover it.)

## Key things to know

- **You need the TV on, and you need to see its screen once.** The TV shows a 6-character code during pairing. Without a way to read it, you cannot pair.
- **No real remote at all?** You can still pair if the TV is on and shows the Android home screen. If it will not turn on, press the power button on the TV's body.
- **Standby is not on.** In standby, the TV answers ping but its remote port is closed. The Google TV app will say it cannot find the TV. Turn it fully on first.
- **Pairing is the one step you do yourself.** Claude cannot read the TV screen. You type the code.
- **The code is short-lived.** Type it within a few seconds of seeing it. A slow code makes the TV drop the pairing.
- **Keep your pairing keys private.** `~/.config/tv-remote/key.pem` is the key to your TV. Never paste it into a chat or a repo.
- **Give the TV a fixed IP** in your router. If the IP changes, the widget stops working.
- **Same Wi-Fi.** A guest network or a separate 5 GHz network can hide the TV from your phone.
- **This is not the same as installing omalauncher on the TV.** omalauncher is a phone launcher (it needs Android 10 or newer and an arm64 phone). Many TVs run Android 8 or 9. I did build a TV-ready copy, but I did not get it running on the TV, so it is not part of this guide.

## The steps

### 1. Find the TV on your network

On a PC or the phone, look for the device that has the Android TV remote port open (6466). My router showed 30 devices, so I scanned for the port.

> **Ask Claude:** Scan my home network for an Android TV. Ping-sweep my subnet, then check which devices have port 6466 or 6467 open. Tell me their IP addresses. Do not print anything else.

How to tell which one is the TV: speakers and displays also show up (port 8009 is a Chromecast-style port). My Android TV opened 6466. My Cast speakers did not. A device that only has AirPlay (7000) is not your TV. When you pair in step 3, the TV tells you its model name. Check that it is yours.

### 2. Turn the TV fully on

Press the power button on the TV and wait for the Android home screen. If you skip this, the scan in step 1 shows nothing useful and pairing fails.

### 3. Pair, once

You do this step yourself. Type it in the terminal:

```sh
tv-remote pair
```

The TV shows a 6-character code. Type it at the prompt right away.

**If it hangs or says the connection was lost:** The TV got stuck on the old pairing box. Unplug the TV from the wall for 30 seconds, plug it in, wait for the home screen, and try again.

### 4. Prove it works

```sh
tv-remote status
```

It should print your TV's model (mine: `BRAVIA 4K GB ATV3`). Then press a key:

```sh
tv-remote key HOME
```

The TV should go to its home screen. If it does, the hard part is done.

### 5. Install the widget

Let Claude do it. In the launcher's terminal, run `claude` and say:

> **Ask Claude:** Install the tv-remote widget from my omalauncher-tools repo. Install Python and a venv with androidtvremote2, put `tv-remote` in `~/.local/bin`, save my TV's IP in `~/.config/tv-remote/host`, and copy `tv.owl` into `~/.config/omalauncher/widgets/`. Do not pair. I will do that myself.

Replace the TV's IP when Claude asks for it. The widget appears on the home screen within a few seconds.

### 6. Use it

Tap a button. Each tap sends one key to the TV. Tap the header to refresh the status.

### 7. Press buttons from a PC (when you have no remote at all)

The same trick works from a PC with Python. Pair the PC the same way (step 3). Then Claude can press keys for you:

> **Ask Claude:** Using the paired remote library, press HOME, then SETTINGS on my TV. Tell me what I should see on screen.

Claude cannot see the TV. Send it a photo of the screen when you need it to know where it is.

## Gotchas I hit

| Problem | Fix |
|---|---|
| The Google TV app could not find my TV. | The TV was in standby. Its remote port was closed. Turn it fully on. |
| I picked the wrong device from the scan. | Two devices looked like candidates. One had only AirPlay open. The real one had port 6466. Check the model name after pairing. |
| No pairing code showed on the TV. | The old pairing box was stuck. Restarting the TV (unplug 30 seconds) brought the code back. Also keep the TV on its Android home screen, not an HDMI input (I did not test that part). |
| The code I typed was rejected. | It had expired. Codes last a short time. Start a new pairing and type the new code at once. |
| New pairings hung after one failed. | The TV was stuck on the old pairing box. Restart the TV by unplugging it for 30 seconds. |
| Opening Settings by link did nothing. | The TV ignored an Android settings link. Press the HOME and SETTINGS keys instead, and look at the screen. |
| Port 5555 (ADB) was closed. | It is off by default. It needs Developer options on the TV, which needs the Settings menu. That is why the remote comes first. |
| The widget checker on my PC rejected the new widget. | My PC's checker was older than my phone's launcher. The widget is fine on the phone. |

## What is not covered

- Installing omalauncher itself on the TV. I built a TV-ready copy and did not get it running.
- Turning on the TV's Developer options and ADB. I got as far as pressing Home and Settings.
- Anything for TVs that are not Android TV or Google TV.

## Files in this folder

| File | What it is |
|---|---|
| `tv.owl` | The widget. |
| `tv-remote` | The script the widget runs. Commands: `pair`, `key`, `app`, `status`. |
| `INSTALL-tv.md` | The steps Claude follows on my phone. |
| `transcripts/` | The two sessions that built it. Part 1 is the PC. Part 2 is the phone. |
