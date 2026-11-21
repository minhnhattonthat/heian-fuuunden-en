-- Write bytes into CPU address space each time the CPU executes one address (force a value a routine is about to
-- read, e.g. the place index of the overworld banner).
--   emu.py ... --script tools/lua/execpoke.lua --var "AT=0xC136C0" --var "POKES='7E1088=14,7E1089=01'"
-- Values are hex bytes; addresses are 24-bit CPU addresses. Logs the first hit.
local MEM = emu.memType.snesMemory
local hit = false
L.on_exec(AT, AT, function()
  for a, v in (POKES or ""):gmatch("(%x+)=(%x+)") do emu.write(tonumber(a, 16), tonumber(v, 16), MEM) end
  if not hit then hit = true; L.log(string.format("execpoke %06X %s f%d", AT, POKES or "", L.frame)) end
end)
