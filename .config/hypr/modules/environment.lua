-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

hl.env("XCURSOR_THEME", "modest-dark")


hl.env("XCURSOR_SIZE", "20")


hl.env("GTK_THEME", "Prefer-dark")

-- Example for Lua-based Hyprland config
hyprland = {
    env = {
        STEAM_FORCE_WAYLAND = "1",
        QT_QPA_PLATFORM = "wayland",
        QT_AUTO_SCREEN_SCALE_FACTOR = "1",
        GDK_BACKEND = "wayland",
    },
    -- ... rest of your config
}


hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
