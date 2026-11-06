"""Шесть оригинальных указателей клавиатурных обработчиков и их накопителей."""
# start, name, tag, channel, direction, add, limit, own, opposite, latch, value
ENTRIES=(
    (0x76C7,'RequestTurnNegative','ActionKeyTurnNegative','Turn',-1,94,0xF9,0x76CD,0x76F0,0x6FE5,0x9B97),
    (0x76EA,'RequestTurnPositive','ActionKeyTurnPositive','Turn',1,94,8,0x76F0,0x76CD,0x6FE5,0x9B97),
    (0x770D,'RequestXNegative','ActionKeyXNegative','X',-1,70,0xFD,0x7713,0x7736,0x6F7B,0x9B96),
    (0x7730,'RequestXPositive','ActionKeyXPositive','X',1,70,4,0x7736,0x7713,0x6F7B,0x9B96),
    (0x7753,'RequestYNegative','ActionKeyYNegative','Y',-1,72,0xFD,0x7759,0x777C,0x6FB0,0x9B95),
    (0x7776,'RequestYPositive','ActionKeyYPositive','Y',1,72,4,0x777C,0x7759,0x6FB0,0x9B95))
