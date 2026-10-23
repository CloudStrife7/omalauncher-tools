# Install the TV remote widget (for Claude, on the phone)

You are running in the launcher's Arch system. This repo is `~/.config/omalauncher`, so
`widgets/tv.owl` is already in the widgets folder and the launcher shows it. Do these steps. Do
not ask the owner questions. Keep your replies short.

The widget is a remote for the owner's Sony BRAVIA (Android TV). `widgets/scripts/tv-remote`
sends one key per tap over Wi-Fi to the TV's remote port (6466/6467).

1. Install Python. You may be root already; use `sudo` only if it exists:

   ```sh
   pacman -S --needed --noconfirm python
   ```

2. Make the remote library's own Python folder:

   ```sh
   python -m venv ~/.local/share/tv-remote/venv
   ~/.local/share/tv-remote/venv/bin/pip install androidtvremote2
   ```

3. Install the script, pointed at that Python, and save the TV's address. Replace `<TV_IP>` with your TV's IP address (TV Settings > Network):

   ```sh
   mkdir -p ~/.local/bin ~/.config/tv-remote && chmod 700 ~/.config/tv-remote
   sed "1s|.*|#!$HOME/.local/share/tv-remote/venv/bin/python|" ~/.config/omalauncher/widgets/scripts/tv-remote > ~/.local/bin/tv-remote
   chmod +x ~/.local/bin/tv-remote
   [ -s ~/.config/tv-remote/host ] || echo <TV_IP> > ~/.config/tv-remote/host
   ```

4. Check the TV answers on its remote port. If it does not, tell the owner the TV must be on and
   on the same Wi-Fi as the phone:

   ```sh
   timeout 5 bash -c 'echo > /dev/tcp/$(cat ~/.config/tv-remote/host)/6466' && echo reachable
   ```

5. Stop here. Tell the owner, in one sentence, to type this themselves (the TV shows a
   6-character code that they type at the prompt; you cannot do this step):

   ```sh
   tv-remote pair
   ```

   After that, `tv-remote status` prints the TV's model, and the widget buttons work.

Never print or copy `~/.config/tv-remote/key.pem`.
