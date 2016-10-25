COMMAND_ENCODINGS = {
                    [0x01] = "frameadvance",
                    [0x02] = "speedmode_maximum",
                    [0x03] = "speedmode_normal",
                    [0x04] = "message",
                    [0x05] = "framecount",
                    [0x06] = "emulating",
                    [0x07] = "print",
                    [0x08] = "readbyte",
                    [0x09] = "readbytesigned",
                    [0x10] = "readbytes",
                    [0x11] = "joypadset",
                    [0x12] = "loadstate"}

function split(source, delimiters)
        local elements = {}
        local pattern = '([^'..delimiters..']+)'
        string.gsub(source, pattern, function(value) elements[#elements + 1] =     value;  end);
        return elements
end
function int_to_bool(val)
    if tonumber(val) == 0 then
        return false
    else
        return true
    end
end


local socket = require('socket')
local server = assert(socket.bind("*",9000))
local ip, port = server:getsockname()
emu.print("Hello world!  " .. port);
initial_state = savestate.object(1)
savestate.save(initial_state)
local client = server:accept()
emu.print("Client connected")

client:settimeout(5)
joypad_initial = joypad.get(1)
joypad_old = joypad.get(1)
joypad_current = joypad_initial
while (true) do
    local line, err = client:receive()
    if err then
        emu.print(err)
        break
    end
    local command = COMMAND_ENCODINGS[line:sub(1,1):byte()]
    local args = split(line:sub(2),'_')
    -- emu.print(line)
    -- emu.print(args)

    if command == "emulating" then
        if emu.emulating() then
            client:send('1')
        else
            client:send('0')
        end
    elseif command == "frameadvance" then
        joypad.set(1,joypad_current)
        -- for k,v in pairs(joypad_old) do
        --     if v ~= joypad.get(1)[k] then
        --         emu.print(k.." changed to "..tostring(joypad.get(1)[k]))
        --     end
        -- end
        -- joypad_old = joypad.get(1)
        --emu.print(joypad.getdown(1))
        emu.frameadvance()
    elseif command == "speedmode_maximum" then
        emu.speedmode("maximum")
    elseif command == "speedmode_normal" then
        emu.speedmode("normal")
    elseif command == "message" then
        emu.message(args[1])
    elseif command == "framecount" then
        client:send(tostring(emu.framecount()))
    elseif command == "print" then
        emu.print(args[1])
    elseif command == "readbyte" then
        local byte = memory.readbyte(args[1])
        client:send(byte)
    elseif command == "readbytesigned" then
        local byte = memory.readbytesigned(args[1])
        client:send(byte)
    elseif command == "readbytes" then
        for i=1, #args, 2 do
            local bytes = memory.readbyterange(args[i],args[i+1])
            client:send(bytes)
        end
    elseif command == "loadstate" then
        emu.print("LOADING")
        joypad_current = joypad_initial
        savestate.load(initial_state)
    elseif command == "joypadset" then
        -- emu.print(args)
        for k,v in pairs(args) do
            args[k] = int_to_bool(v)
        end
        -- emu.print("converted args")
        -- emu.print(args)
        joypad_current = {
            up = args[1],
            down = args[2],
            left = args[3],
            right = args[4],
            A = args[5],
            B = args[6],
            start = false,
            select = false}
    end
    client:send('\r\n')
end
