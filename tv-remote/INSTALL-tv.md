# Install the TV remote widget (for Claude, on the phone)

You run in omalauncher's terminal (the launcher's Arch system) on the owner's phone. This repo is
cloned in the current folder or one level up: the files are `tv-remote/tv.owl` and `tv-remote/tv-remote`.
Do these steps. Keep your replies short. The owner gives you the TV's IP address in the prompt. If
they did not, ask for it once.

The widget sends one key per tap over Wi-Fi to the TV's Android TV remote port (6466/6467).

1. Install Python. You may be root already; use `sudo` only if it exists:

   ```sh
   pacman -S --needed --noconfirm python
   ```

2. Make the remote library's own Python folder:

   ```sh
   python -m venv ~/.local/share/tv-remote/venv
   ~/.local/share/tv-remote/venv/bin/pip install androidtvremote2
   ```

3. Install the script, pointed at that Python, and save the TV's IP (replace `TV_IP`):

   ```sh
   mkdir -p ~/.local/bin ~/.config/tv-remote && chmod 700 ~/.config/tv-remote
   sed "1s|.*|#!$HOME/.local/share/tv-remote/venv/bin/python|" tv-remote/tv-remote > ~/.local/bin/tv-remote
   chmod +x ~/.local/bin/tv-remote
   echo TV_IP > ~/.config/tv-remote/host
   ```

4. Copy the widget into omalauncher's widgets folder, then check it. `owl-check` may not exist on
   every setup; skip it if it is missing.

   ```sh
   mkdir -p ~/.config/omalauncher/widgets
   cp tv-remote/tv.owl ~/.config/omalauncher/widgets/tv.owl
   owl-check ~/.config/omalauncher/widgets/tv.owl
   ```

   The widget declares `owl: 12`. If the check says the launcher supports a lower version, tell the
   owner to update omalauncher.

5. Check the TV answers on its remote port. If it does not, tell the owner the TV must be on and on the
   same Wi-Fi as the phone:

   ```sh
   timeout 5 bash -c 'echo > /dev/tcp/$(cat ~/.config/tv-remote/host)/6466' && echo reachable
   ```

6. Stop here. Tell the owner, in one sentence, to type this themselves (the TV shows a 6-character
   code that they type at the prompt; you cannot do this step):

   ```sh
   tv-remote pair
   ```

   After that, `tv-remote status` prints the TV's model and volume, and the widget buttons work.

Never print or copy `~/.config/tv-remote/key.pem`.
