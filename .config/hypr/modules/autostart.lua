-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--

hl.on("hyprland.start", function ()
   hl.exec_cmd("awww-daemon")
   hl.exec_cmd("nohup ~/.config/rofi/watch-theme.sh > ~/.config/rofi/watch-theme.log 2>&1 < /dev/null &")
   hl.exec_cmd("~/.config/kitty/watch-theme.sh")
   hl.exec_cmd("~/.config/themes/watch-themes.sh")
   hl.exec_cmd("wl-clip-persist --clipboard regular")
   hl.exec_cmd("notification-daemon")
   hl.exec_cmd("env GDK_BACKEND=x11 /usr/lib/notification-daemon-1.0/notification-daemon")
   hl.exec_cmd("mpd --no-daemon ~/.config/mpd/mpd.conf &")
   hl.exec_cmd("sleep 2; waybar")
   hl.exec_cmd("https://chatgpt.com/c/6adf3574-c2cc-83ee-8739-8285a752ba31")
end)
