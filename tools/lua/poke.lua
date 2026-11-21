-- Write bytes into CPU address space at one frame (recon helper).
--   emu.py ... --script tools/lua/poke.lua --var "POKES='306132=01,306138=70,306139=07'" [--var POKE_AT=5]
-- Values are hex bytes; addresses are 24-bit CPU addresses (SRAM is $30:6000-$7FFF here).
local at = POKE_AT or 5
L.on_frame(function(f)
  if f ~= at then return end
  for a, v in (POKES or ""):gmatch("(%x+)=(%x+)") do
    emu.write(tonumber(a, 16), tonumber(v, 16), emu.memType.snesMemory)
    L.log(string.format("poke %s=%s", a, v))
  end
end)
