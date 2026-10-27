-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })

---------------
--  LAYOUTS  --
---------------

-- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
hl.config({
    dwindle = {
        preserve_split = true, -- You probably want this
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Master-Layout/ for more
hl.config({
    master = {
        new_status = "master",
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/ for more
hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- See https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- and https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

-- Example window rules that are useful

local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})
-- suppressMaximizeRule:set_enabled(false)

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Hyprland-run windowrule
hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

-- Remember floating window sizes per app class, persisted across sessions
local sizes_file = os.getenv("HOME") .. "/.config/hypr/floating_sizes.tsv"
local sizes = {}

do
    local f = io.open(sizes_file, "r")
    if f then
        for line in f:lines() do
            local class, w, h = line:match("^(.-)\t(%d+)\t(%d+)$")
            if class then sizes[class] = { x = tonumber(w), y = tonumber(h) } end
        end
        f:close()
    end
end

local function save_sizes()
    local f = io.open(sizes_file, "w")
    if not f then return end
    for class, s in pairs(sizes) do
        f:write(class, "\t", s.x, "\t", s.y, "\n")
    end
    f:close()
end

local function remember(w)
    if w and w.floating and w.class and w.class ~= "" then
        sizes[w.class] = { x = math.floor(w.size.x), y = math.floor(w.size.y) }
        save_sizes()
    end
end

hl.unbind("SUPER + A")
hl.bind("SUPER + A", function()
    local w = hl.get_active_window()
    if not w then return end

    if w.floating then
        remember(w)
        hl.dispatch(hl.dsp.window.float({ action = "unset", window = w }))
    else
        hl.dispatch(hl.dsp.window.float({ action = "set", window = w }))
        local s = sizes[w.class]
        if s then
            hl.timer(function()
                hl.dispatch(hl.dsp.window.resize({ x = s.x, y = s.y, relative = false, window = w }))
                hl.dispatch(hl.dsp.window.center({ window = w }))
            end, { timeout = 50, type = "oneshot" })
        end
    end
end)

hl.on("window.close", function(w) remember(w) end)


