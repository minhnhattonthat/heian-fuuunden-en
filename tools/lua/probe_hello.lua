-- Minimal probe: proves --script Lua runs and L.log reaches log.txt (Step 0 check).
L.on_frame(function(n)
  if n == 60 then L.log("probe ok frame " .. n) end
end)
