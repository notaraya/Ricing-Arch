------------------
---- MONITORS ----
------------------

hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "1.33",
})

hl.config({
    xwayland = {
        use_nearest_neighbor = false,
        force_zero_scaling = true,
    },
})
