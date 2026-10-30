-- Упаковка выполняется встроенным Lua SjASMPlus.
-- Активные файлы поступают из результата SAVETRD текущей сборки.
local disk_size = 655360
local image_path = "Awakenv02.trd"
local report_path = "Tools/Disasm/Reports/BuildVerification.json"
local image
local covered = {}
local allocations = {}

local function read_file(path)
    local file = assert(io.open(path, "rb"))
    local data = assert(file:read("a"))
    assert(file:close())
    return data
end

local function status(value, identical)
    -- Обновление результата только для текущего запуска ассемблера.
    local file = assert(io.open(report_path, "wb"))
    assert(file:write(string.format(
        '{\n  "status": "%s",\n  "method": "sjasmplus_lua",\n' ..
        '  "checked_at_utc": "%s",\n  "byte_identical": %s,\n' ..
        '  "disk_size": %d,\n  "active_allocations": %d\n}\n',
        value, os.date("!%Y-%m-%dT%H:%M:%SZ"), identical, disk_size, #allocations)))
    assert(file:close())
end

function reset_report()
    status("in_progress", "null")
end

local function write_at(offset, data)
    -- Проверка границ и отсутствия пересечений исходных физических областей.
    assert(offset >= 0 and offset + #data <= disk_size, "выход за границу TRD")
    for position = offset, offset + #data - 1 do
        assert(not covered[position], "повторная запись физического байта диска")
        covered[position] = true
    end
    assert(image:seek("set", offset))
    assert(image:write(data))
end

function begin_image()
    status("in_progress", "null")
    -- Создание носителя полного размера, служебные данные сохраняются отдельно от программ.
    image = assert(io.open(image_path, "w+b"))
    assert(image:write(string.rep("\0", disk_size)))
    local layout = dofile("Tools/Disasm/Disk/Layout.lua")
    for _, component in ipairs(layout) do
        local data = read_file(component.path)
        assert(#data == component.size, "изменилась длина сохранённого компонента")
        write_at(component.offset, data)
    end
end

function finish_image()
    -- Чтение собранных программ из текущего результата SAVETRD до восстановления разметки.
    local compiled = read_file(image_path)
    local units = dofile("Tools/Disasm/Disk/BuildUnits.lua")
    local blocks = {}
    for index, unit in ipairs(units) do
        local entry = (index - 1) * 16
        local low, high = compiled:byte(entry + 12, entry + 13)
        local length = low + 256 * high
        local sectors, sector, track = compiled:byte(entry + 14, entry + 16)
        local offset = (track * 16 + sector) * 256
        assert(length == unit.size and sectors * 256 == unit.size,
            "размер результата SAVETRD не совпадает с исходной областью")
        local data = compiled:sub(offset + 1, offset + length)
        assert(#data == length)
        blocks[#blocks + 1] = {unit=unit, data=data}
    end
    begin_image()
    for _, block in ipairs(blocks) do
        write_at(block.unit.offset, block.data)
        allocations[#allocations + 1] = block.unit.slot
    end
    -- Проверка полного покрытия и всех байтов, включая удалённые записи и хвосты.
    assert(image:flush())
    assert(image:seek("end") == disk_size)
    assert(image:close())
    image = nil
    assert(#allocations == 41, "собраны не все активные файлы")
    for position = 0, disk_size - 1 do
        assert(covered[position], "пропущен физический байт диска")
    end
    local result = read_file(image_path)
    local original = read_file("Tools/Disasm/Disk/original.trd")
    assert(#result == #original and #result == disk_size)
    for position = 1, disk_size do
        if result:byte(position) ~= original:byte(position) then
            status("failed", "false")
            error(string.format("отличие от оригинала по смещению #%06X", position - 1))
        end
    end
    status("passed", "true")
    print("Awakenv02.trd: byte-for-byte match, 655360 bytes")
end
