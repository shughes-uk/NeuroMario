ButtonNames = {
       "A",
       "B",
       "Up",
       "Down",
       "Left",
       "Right",
}

BoxRadius = 6
InputSize = (BoxRadius*2+1)*(BoxRadius*2+1)
Inputs = InputSize+1
Outputs = #ButtonNames

function split(source, delimiters)
        local elements = {}
        local pattern = '([^'..delimiters..']+)'
        string.gsub(source, pattern, function(value) elements[#elements + 1] =     value;  end);
        return elements
  end
emu.speedmode("maximum")

local socket = require('socket')
--local socket = require("socket")
local server = assert(socket.bind("*",9000))
local ip, port = server:getsockname()
emu.print("Hello world!  " .. port);

local client = server:accept()


while (true) do
    client:settimeout(10)
    local line, err = client:receive()
    local requested_memory_str = split(line,',')
    local requested_memory = {}
    for k,address_range in pairs(requested_memory_str) do
      address_range = split(address_range,'_')
      --emu.print(address_range[1],address_range[2])
      --emu.print(memory.readbyterange(address_range[1],address_range[2]))
      local memstr = memory.readbyterange(address_range[1],address_range[2])
      table.insert(requested_memory,memstr)
    end
    -- emu.print(requested_memory)
    for k,memstr in pairs(requested_memory) do
      -- emu.print("sending "..memstr)
      client:send(memstr)
      client:send('\r\r')
    end
    client:send('\n\r\n\r')
    emu.frameadvance();
    emu.frameadvance();
    emu.frameadvance();
    emu.frameadvance();
end;
