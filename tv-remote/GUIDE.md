# Turn your phone into a TV remote

Pair your phone with a Sony Android TV over Wi-Fi and put a remote widget on omalauncher, for when the remote is lost.

## When to skip

You have a working remote (lol), the Google TV app finds your TV (mine did not), or a USB keyboard works in the TV's USB port. Try those first.

## Who this is for and what it does

**For:** An Android TV (mine: Sony BRAVIA X900F), an Android phone with omalauncher and Claude Code, and one shared Wi-Fi.

**What it does:** An omalauncher widget (one .owl file) that sends remote-control keys to a Sony Android TV over Wi-Fi.

**What you get:** A tv.owl widget, a tv-remote command, and a pairing with your TV that lasts.

## The download

Have you ever lost your TV remote? We all have, at one time or another.

Well, I lost mine a few weeks ago, and it's gone. No idea where it went. Backup remote? Also gone.

Good thing I had already turned on debug mode on my Sony BRAVIA X900F, back when I was disabling animations to speed it up after I bought it. It is still laggy as hell. I'm going to install Omarchy TV on it eventually, but that's another project.

This one is about having Claude write an omalauncher widget to replace the remote you lost.

## Key things to know

- You need a working remote for step 1 only. Turn debug mode on while you still have one.
- I already had debug mode on before the remote went missing.
- You read the pairing code off the TV screen and type it yourself. Claude cannot see the screen.
- The code expires fast. If the TV hangs on a pairing box, unplug it and start again.
- The TV and the phone must be on the same Wi-Fi.
- The widget needs a recent omalauncher. It declares owl 12, and my phone runs it.
- Give the TV a fixed IP in your router. If it changes, the widget stops working until you edit ~/.config/tv-remote/host.
- Keep ~/.config/tv-remote/key.pem private. It is the key to your TV.
- I tested this on one TV only: a Sony BRAVIA X900F (model BRAVIA 4K GB ATV3).

## The steps

### 1. Turn on debug mode (do this first)

I did this long before the remote went missing, so it was already on. It is the one step you cannot do afterward without a remote. Press Home, then open Settings > Device Preferences > About. Press OK on Build 7 times. Press Back, open Developer options, and turn on USB debugging. Menu names follow Android TV 8 and 9.

*Zach says: Do this one while you still have a remote.*

### 2. Find your TV's IP address

Without a remote you cannot read the IP from the TV's menus. I had Claude Code on a PC scan my network. The TV is the device with port 6466 open, which is the Android TV remote port. Speakers and displays showed port 8009 only. My first pick, a device with only AirPlay open, was wrong. Step 5 confirms it: the status command prints the TV's model.

> **Ask Claude:** Scan my home network for an Android TV. Ping-sweep my subnet, then check which devices have port 6466 or 6467 open. Tell me their IP addresses. Do not print anything else.

*Zach says: The TV is the one with 6466 open.*

### 3. Pair once (you type the code)

I paired from a PC first, then again from the phone. Each device pairs on its own. Run the pair command. The TV shows a 6-character code. Type it at once, because it expires. My first tries failed: the code expired, and the TV then hung on the old pairing box. Unplugging the TV and plugging it back in fixed it.

```sh
tv-remote pair
```

### 4. Install the widget on your phone

In omalauncher's terminal, run Claude Code and give it the prompt below. It installs Python and the remote library, saves your TV's IP, and copies the widget into omalauncher's widgets folder. Pair it yourself, as in step 3. Claude cannot type the code.

> **Ask Claude:** Clone https://github.com/CloudStrife7/omalauncher-tools, then follow tv-remote/INSTALL-tv.md to install the TV remote widget. My TV's IP is YOUR_TV_IP. Do not pair. I will do that myself.

*Zach says: One file. No app on the TV.*

### 5. Tap a key and check it reached the TV

Tap a button on the widget. The header shows the TV's state and its volume. Press vol + and watch the number change. That proves the key reached the TV. A tap takes about two seconds, because each one opens a fresh connection.

```sh
tv-remote status
tv-remote key VOLUME_UP
```

*Zach says: Watch the volume number change.*

### 6. What broke after install (already fixed)

My first version looked fine and did nothing. Every tap exited cleanly and the TV ignored it. The fixes are in the script you installed, so you will not hit them. They are in the gotchas below, for the day you change it.

*Zach says: Test with the volume number, not the exit code.*

## Gotchas

| Problem | Fix |
|---|---|
| A key sent right after connecting did nothing. | The Sony BRAVIA drops a key sent within about 300 ms of connecting. The script now waits for the TV's first state, then a short pause. (Fixed in the script.) |
| The mute button muted nothing. | The key name MUTE is the microphone mute. The TV's mute is VOLUME_MUTE. (Fixed in the widget.) |
| The widget header said offline while the TV was on. | A status source is silently ignored under owl 7. The widget declares owl 12. (Fixed in the widget.) |
| A status check and a tap failed when they overlapped. | The TV takes one remote connection at a time. The script retries a few times. (Fixed in the script.) |
| The pairing code was rejected, then new pairings hung. | The code expired and the TV stayed on the old pairing box. Unplug the TV, plug it back in, and pair again. |
| I picked the wrong device from the scan. | A device with only AirPlay open was not the TV. The right one had port 6466. Check the model name that tv-remote status prints. |

## Sources

**Omalauncher**
- https://github.com/SimonSchubert/omalauncher
- https://play.google.com/store/apps/details?id=dev.omalauncher&hl=en_US

**Claude Code**
- https://claude.com/product/claude-code

**Want to learn more about Claude Code? Claude Academy**
- https://academy.claude.com/

## Files in this folder

| File | What it is |
|---|---|
| `tv.owl` | The widget. |
| `tv-remote` | The script the widget runs. Commands: `pair`, `key`, `app`, `status`. |
| `INSTALL-tv.md` | The steps Claude follows to install it. |
| `art/` | The Zach pictures and the script that made them. |
| `transcripts/` | The two sessions that built it. Part 1: PC. Part 2: phone. |
