                module ArchiveStartLayerPrograms
                module Third
                ; Документация [исполняемый слой](../../Docs/BankArchiveTileLayers.md#исполняемые-слои)
                ; Каждая группа выводит восемь строк по 20 байтов, начиная с правого края.

                ; вывод экранных строк 24..31
Entry:          LD HL, #C07A
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0200, #4000, #0080, #0000, #0000, #0000
                ArchiveLayerRow #0A00, #0000, #00AA, #2014, #972A, #9B16, #0055, #DA00, #0000, #0000
                ArchiveLayerRow #0500, #0000, #0020, #11E0, #2D01, #2441, #4490, #2200, #0000, #0000
                ArchiveLayerRow #1000, #0000, #004D, #00A0, #5E02, #4A28, #1142, #9400, #0000, #0000
                ArchiveLayerRow #2600, #0000, #0090, #0200, #BB04, #2490, #AA20, #4900, #0000, #0000
                ArchiveLayerRow #0100, #0000, #0054, #00C0, #6000, #1220, #0040, #2500, #0000, #0000
                ArchiveLayerRow #0A00, #0000, #0080, #0000, #C001, #2900, #1184, #A800, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0010, #0000, #8009, #0400, #0000, #FF00, #0000, #0000

                ; вывод экранных строк 32..39
Rows032:        LD HL, #C09A
                ArchiveLayerRow #0B00, #0000, #0020, #0000, #0003, #1200, #0094, #FF00, #0000, #0000
                ArchiveLayerRow #0400, #0000, #0000, #0000, #0006, #0A00, #0081, #0000, #0000, #0000
                ArchiveLayerRow #0200, #0000, #0000, #E003, #0004, #0500, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0500, #0000, #0000, #D0EF, #0307, #0800, #0000, #1000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #E8FF, #0305, #0500, #0000, #2200, #0000, #0000
                ArchiveLayerRow #0500, #0000, #0000, #F8FF, #3F0E, #0200, #0080, #0800, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #F4FF, #3F08, #0900, #0020, #0200, #0000, #0000
                ArchiveLayerRow #0100, #0000, #0000, #F4FF, #7F0C, #0400, #0054, #0000, #0000, #0000

                ; вывод экранных строк 40..47
Rows040:        LD HL, #C0BA
                ArchiveLayerRow #0000, #0000, #0000, #E8FF, #7B00, #0100, #0001, #8000, #0000, #0000
                ArchiveLayerRow #0100, #0000, #0000, #F6FF, #7F00, #0D00, #405A, #E000, #0000, #0000
                ArchiveLayerRow #C003, #0000, #0000, #F8FF, #7E00, #0200, #0001, #F800, #0000, #0000
                ArchiveLayerRow #E03F, #0000, #0000, #FCEF, #7D00, #0000, #0000, #7E00, #0000, #4000
                ArchiveLayerRow #E0FF, #0000, #0000, #0000, #0000, #0000, #0080, #5F00, #0000, #E001
                ArchiveLayerRow #E0FF, #0100, #0000, #0000, #0000, #0000, #00F0, #2700, #0000, #F003
                ArchiveLayerRow #00ED, #0300, #0000, #0000, #0000, #0000, #00FC, #9900, #0000, #F007
                ArchiveLayerRow #0080, #0700, #0000, #0000, #1000, #0000, #809F, #4500, #0B00, #E003

                ; вывод экранных строк 48..55
Rows048:        LD HL, #C0DA
                ArchiveLayerRow #4081, #0700, #0000, #8000, #0000, #0000, #E09F, #5900, #FE0F, #C003
                ArchiveLayerRow #001B, #0200, #0000, #0000, #3003, #0000, #5C1E, #A100, #F8C7, #0700
                ArchiveLayerRow #F0F1, #1D00, #0000, #000C, #0003, #00A0, #011E, #1580, #6280, #0F03
                ArchiveLayerRow #9867, #1D00, #0000, #000C, #0007, #002F, #001C, #5180, #40FE, #4F06
                ArchiveLayerRow #FC5D, #0F00, #0000, #000C, #C006, #FF01, #009F, #A980, #F380, #6F06
                ArchiveLayerRow #B08F, #1700, #0028, #0F0E, #E006, #3F00, #009D, #1480, #FFF7, #7F06
                ArchiveLayerRow #68F5, #0D00, #0000, #791E, #FA05, #0000, #041C, #4080, #FF6D, #7F06
                ArchiveLayerRow #E87F, #0300, #0052, #1E8F, #F717, #0900, #0408, #AC80, #FFFF, #7F02

                ; вывод экранных строк 56..63
Rows056:        LD HL, #C0FA
                ArchiveLayerRow #80C3, #0900, #0024, #8B3E, #FA07, #4200, #000E, #1000, #77FF, #FF03
                ArchiveLayerRow #4883, #1500, #000A, #4A08, #FC2B, #2900, #0446, #A480, #BFFF, #FF00
                ArchiveLayerRow #0067, #0A00, #0001, #E401, #7894, #4400, #0447, #1000, #7FBF, #7F00
                ArchiveLayerRow #10AE, #0700, #0014, #FAF5, #3821, #9500, #0C26, #4800, #FFFF, #7F00
                ArchiveLayerRow #00DF, #0100, #0003, #48FF, #7D88, #2800, #0067, #A400, #16DE, #7F00
                ArchiveLayerRow #50FC, #0100, #0004, #1600, #3C50, #4001, #0072, #1000, #0EFF, #3F00
                ArchiveLayerRow #007E, #0400, #0000, #DA3F, #3E20, #9500, #C073, #A400, #FCF7, #3F00
                ArchiveLayerRow #407C, #0300, #0001, #A43F, #3C90, #0001, #0003, #1000, #FEFE, #1F00

                ; вывод экранных строк 64..71
Rows064:        LD HL, #C81A
                ArchiveLayerRow #00B8, #0200, #0000, #DEEA, #3E00, #5500, #E801, #0000, #80FA, #0F00
                ArchiveLayerRow #80D4, #0300, #0000, #54DF, #3E40, #8800, #F801, #A000, #04FE, #7F00
                ArchiveLayerRow #00B8, #0100, #0000, #AAE0, #3F80, #1000, #E000, #0000, #68FD, #7F00
                ArchiveLayerRow #00D4, #0000, #0000, #56C1, #3F00, #0000, #F000, #000A, #08FE, #7F00
                ArchiveLayerRow #00FB, #0000, #0000, #D6FA, #3F00, #0000, #0000, #00FF, #8FFF, #7F00
                ArchiveLayerRow #0075, #0000, #0000, #AADF, #3F00, #0000, #0000, #00FF, #FB7F, #7F00
                ArchiveLayerRow #0000, #0000, #0000, #4CAF, #3C00, #0000, #0000, #00FF, #F83F, #FF00
                ArchiveLayerRow #0002, #0000, #8000, #8E60, #3E00, #0000, #0000, #0057, #D30F, #FE01

                ; вывод экранных строк 72..79
Rows072:        LD HL, #C83A
                ArchiveLayerRow #0000, #0000, #5080, #1D00, #7C00, #0000, #0000, #006A, #0180, #DF01
                ArchiveLayerRow #0000, #0000, #A4F0, #3F00, #FE00, #0000, #0000, #00BF, #0100, #F703
                ArchiveLayerRow #0010, #0000, #DA7C, #7D00, #FE03, #0000, #0000, #0057, #0040, #FF07
                ArchiveLayerRow #001F, #0040, #55FF, #FE00, #FC0F, #0000, #0000, #00AF, #35A0, #FE07
                ArchiveLayerRow #C00B, #00D0, #BB5F, #7F01, #FF3F, #0200, #0000, #00FF, #76C0, #FF0F
                ArchiveLayerRow #E006, #00F4, #6FFF, #AE02, #FEFF, #0000, #0000, #00FF, #2B80, #FF1F
                ArchiveLayerRow #BC01, #00FC, #DFDF, #3FF5, #FFFF, #0000, #0000, #14FF, #DF7D, #FF3F
                ArchiveLayerRow #FF02, #0054, #75FF, #7F3C, #F5FF, #0000, #0000, #7FFF, #FFFF, #FF7F

                ; вывод экранных строк 80..87
Rows080:        LD HL, #C85A
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #0000, #1000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F000, #0000, #0000, #0000, #0015, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #C000, #0000, #0000, #0000, #000A, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #8000, #0000, #0000, #0000, #0020, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000

                ; вывод экранных строк 88..95
Rows088:        LD HL, #C87A
                ArchiveLayerRow #0000, #0200, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #0C00, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0000, #7700, #0500, #0000, #0000, #0000, #0200, #0000, #0000, #0000
                ArchiveLayerRow #0000, #5455, #0500, #0000, #0000, #0000, #0100, #0000, #0000, #0000
                ArchiveLayerRow #0000, #AE4A, #0300, #0000, #0000, #0000, #0A00, #0000, #0000, #0000
                ArchiveLayerRow #0000, #D8D5, #0700, #0000, #0000, #0000, #2400, #0401, #0000, #0000
                ArchiveLayerRow #0000, #7C22, #0700, #0000, #0000, #0000, #1000, #005C, #0000, #0000
                ArchiveLayerRow #0000, #54D5, #0700, #0000, #0000, #0000, #2800, #0022, #0000, #0000

                ; вывод экранных строк 96..103
Rows096:        LD HL, #C89A
                ArchiveLayerRow #0000, #B0AA, #0700, #0000, #0000, #0000, #0400, #044A, #0000, #0000
                ArchiveLayerRow #0000, #D0CD, #0700, #0000, #2800, #0000, #1000, #0128, #0000, #0000
                ArchiveLayerRow #0000, #AC4A, #0700, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #0002, #0BF0, #0700, #0000, #1800, #0000, #FF0F, #0000, #00C0, #FF00
                ArchiveLayerRow #0004, #C580, #0000, #0000, #3F00, #00E0, #FF0B, #0100, #00E0, #FF02
                ArchiveLayerRow #000E, #0500, #0000, #00BC, #6200, #00F0, #7F07, #0100, #00F8, #FF0B
                ArchiveLayerRow #0000, #0260, #0200, #0060, #E000, #00F0, #BF3B, #0100, #007C, #8426
                ArchiveLayerRow #0010, #6C23, #0200, #0000, #F000, #00F8, #7FFF, #0701, #001C, #0090

                ; вывод экранных строк 104..111
Rows104:        LD HL, #C8BA
                ArchiveLayerRow #001C, #2A50, #0C00, #0020, #C000, #8038, #FC0F, #0708, #0000, #3020
                ArchiveLayerRow #0002, #7CF4, #FF00, #0020, #ED00, #C0FC, #B002, #0725, #00B6, #9D48
                ArchiveLayerRow #0004, #B4AF, #FF00, #0060, #F800, #80FE, #4100, #0600, #0068, #9C54
                ArchiveLayerRow #000A, #78C3, #FF00, #0070, #F800, #803E, #8000, #0E00, #0094, #8E20
                ArchiveLayerRow #000C, #A0F8, #FF00, #0060, #F800, #C0FF, #8F38, #0400, #0068, #32C9
                ArchiveLayerRow #0000, #C000, #FE00, #00F0, #FC00, #C0FD, #FF40, #0600, #0052, #4C28
                ArchiveLayerRow #0000, #4004, #FF00, #0080, #F100, #80FF, #F330, #0600, #00C0, #0444
                ArchiveLayerRow #0000, #8003, #FF00, #0000, #FF00, #80F1, #FFBD, #0700, #0088, #0390

                ; вывод экранных строк 112..119
Rows112:        LD HL, #C8DA
                ArchiveLayerRow #0000, #4000, #FE00, #0000, #7800, #00FB, #FF70, #0600, #00C0, #014A
                ArchiveLayerRow #0000, #00B1, #FF00, #0000, #0000, #00E4, #EF79, #0200, #0090, #0020
                ArchiveLayerRow #0000, #00C0, #FF00, #0000, #0000, #00D8, #F711, #0200, #0040, #0192
                ArchiveLayerRow #0000, #0000, #FE00, #0000, #0A00, #00F4, #F325, #0200, #0060, #0004
                ArchiveLayerRow #0000, #00F0, #FF00, #0080, #0000, #00DD, #DB01, #0300, #0024, #0028
                ArchiveLayerRow #8000, #00C0, #FF00, #0000, #0000, #00F5, #1F00, #0300, #0060, #0010
                ArchiveLayerRow #C000, #0000, #FE00, #0000, #0800, #00DA, #0F00, #0100, #0008, #0020
                ArchiveLayerRow #0001, #0080, #FF00, #0000, #0200, #00B3, #F300, #0100, #0010, #0040

                ; вывод экранных строк 120..127
Rows120:        LD HL, #C8FA
                ArchiveLayerRow #E001, #00E0, #F800, #0000, #0000, #80D5, #01C0, #0001, #0000, #0080
                ArchiveLayerRow #C011, #0040, #E000, #0000, #0000, #C0F3, #FD81, #000A, #0000, #0080
                ArchiveLayerRow #B002, #0000, #0000, #0000, #0000, #C04F, #9960, #0048, #0000, #00E0
                ArchiveLayerRow #C805, #0080, #0000, #0000, #0000, #E093, #7520, #0025, #0000, #0070
                ArchiveLayerRow #F002, #18F0, #0700, #0000, #0000, #F03F, #3920, #00D2, #0400, #1438
                ArchiveLayerRow #EC0D, #20FF, #0F00, #0000, #0000, #F8BF, #5C00, #0009, #0900, #0004
                ArchiveLayerRow #B215, #D3FE, #1F00, #0000, #0000, #F87F, #3800, #00AA, #0200, #100E
                ArchiveLayerRow #F86F, #66FE, #7F00, #0000, #0000, #F4FF, #0000, #00A4, #2800, #000B

                ; вывод экранных строк 128..135
Rows128:        LD HL, #D01A
                ArchiveLayerRow #F6AA, #5F7E, #FD00, #0000, #0000, #DBFF, #0000, #0013, #4100, #9003
                ArchiveLayerRow #F9BF, #7EFA, #F100, #0000, #0100, #44FF, #0100, #0054, #8800, #C083
                ArchiveLayerRow #F657, #55E8, #D374, #0000, #0000, #00BD, #0200, #0002, #1100, #E003
                ArchiveLayerRow #FAEF, #FEE1, #E79A, #0300, #2804, #00FC, #0100, #0028, #0200, #F000
                ArchiveLayerRow #B4FD, #FF53, #DFFE, #0500, #000C, #0032, #0100, #0040, #0000, #F800
                ArchiveLayerRow #6FFF, #FFEF, #BFFF, #0F00, #1018, #00F4, #0002, #0000, #0000, #F800
                ArchiveLayerRow #D4FF, #7F9F, #3DFF, #3F00, #0030, #0008, #0004, #0000, #0000, #3800
                ArchiveLayerRow #EBFF, #FF7A, #7BFF, #5F00, #4060, #00D0, #0104, #0000, #0000, #3800

                ; вывод экранных строк 136..143
Rows136:        LD HL, #D03A
                ArchiveLayerRow #1000, #7500, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #60A9, #FE00, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #80C4, #FF03, #0000, #0000, #0000, #0000, #F000, #0000, #0000, #0000
                ArchiveLayerRow #20F5, #FF07, #0000, #0000, #0000, #0000, #FF07, #0000, #0000, #0000
                ArchiveLayerRow #00EA, #FF1F, #0000, #0000, #0000, #00E0, #FF0F, #0000, #0000, #0000
                ArchiveLayerRow #00FC, #FF7F, #0000, #0000, #0000, #00F8, #FF3F, #0000, #0000, #0000
                ArchiveLayerRow #00FF, #F7FF, #0000, #0000, #0000, #00FC, #FF7F, #0000, #0000, #0000
                ArchiveLayerRow #80FE, #FFD7, #0300, #0000, #0000, #00FE, #FFFF, #0000, #0000, #0000

                ; вывод экранных строк 144..151
Rows144:        LD HL, #D05A
                ArchiveLayerRow #A0FF, #FFFF, #0700, #0000, #0000, #00FF, #FFFF, #0000, #0000, #0000
                ArchiveLayerRow #E9FF, #FFFF, #1B00, #0000, #0000, #80FF, #FFFF, #0100, #0000, #0000
                ArchiveLayerRow #FEFF, #7FFF, #3F00, #0000, #0000, #C0FF, #FFF5, #0100, #0000, #0000
                ArchiveLayerRow #FEFF, #FFFF, #FB00, #0000, #0000, #E0FF, #FFEF, #0300, #0000, #0000
                ArchiveLayerRow #FF17, #00F0, #FF00, #0000, #0000, #E0FF, #FFF9, #0300, #0000, #0000
                ArchiveLayerRow #BF00, #0000, #FA00, #0000, #0000, #E0FF, #BFF3, #0300, #0000, #0000
                ArchiveLayerRow #0B00, #0000, #C000, #0000, #0000, #F0FF, #61FA, #0300, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F07F, #3AD8, #0300, #0000, #0000

                ; вывод экранных строк 152..159
Rows152:        LD HL, #D07A
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F01F, #37C8, #0300, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F0CF, #3B86, #0300, #1F00, #0000
                ArchiveLayerRow #0000, #0000, #0000, #E0FF, #0000, #F8B7, #77C4, #0380, #7E00, #0000
                ArchiveLayerRow #0000, #0000, #0000, #E0FF, #0700, #F81B, #B987, #0340, #1F00, #0000
                ArchiveLayerRow #0000, #0000, #0000, #F0FF, #0F00, #F00D, #FCC6, #0300, #0100, #0000
                ArchiveLayerRow #0000, #0000, #0000, #F8BF, #0800, #F064, #7EC7, #0300, #0000, #0000
                ArchiveLayerRow #00C0, #110F, #0000, #0018, #1000, #4080, #FFE2, #0300, #0200, #0000
                ArchiveLayerRow #0080, #1E02, #0000, #E48C, #1300, #0000, #7FF3, #0360, #4200, #0000

                ; вывод экранных строк 160..167
Rows160:        LD HL, #D09A
                ArchiveLayerRow #00E0, #DF05, #0000, #ECC9, #1B00, #4080, #7FFA, #0300, #6200, #0000
                ArchiveLayerRow #00F8, #BF0F, #0000, #FC9E, #1E00, #C0D8, #19D2, #0300, #6630, #0000
                ArchiveLayerRow #00FC, #9F3F, #0000, #3C1F, #1E00, #E0E0, #C3E0, #0700, #473E, #0000
                ArchiveLayerRow #00FC, #BF3F, #0000, #FCBF, #1F00, #6071, #02F9, #0740, #901F, #0000
                ArchiveLayerRow #00FC, #1F1F, #0000, #F8FF, #1F00, #60E6, #81FD, #0700, #501F, #0000
                ArchiveLayerRow #00FC, #093F, #0000, #FCFD, #1F00, #A04B, #08FF, #0700, #C00F, #0000
                ArchiveLayerRow #00FC, #010F, #0000, #F4DF, #1F00, #C007, #10DA, #0F00, #0001, #0000
                ArchiveLayerRow #00F8, #0F17, #0000, #F8EB, #1F00, #B007, #D4DD, #0F00, #0000, #0000

                ; вывод экранных строк 168..175
Rows168:        LD HL, #D0BA
                ArchiveLayerRow #00F4, #FF0F, #0000, #ECDC, #1F00, #DC06, #04C5, #0F00, #0000, #0000
                ArchiveLayerRow #00F8, #EB0F, #0000, #F888, #1F00, #FF51, #04E4, #1F00, #0000, #0000
                ArchiveLayerRow #00F4, #0105, #0000, #501F, #0F00, #5F42, #24C0, #1F00, #0000, #0000
                ArchiveLayerRow #00EC, #AE0D, #0000, #F088, #0700, #DF10, #14E0, #1F00, #0000, #0000
                ArchiveLayerRow #00F8, #7F17, #0000, #D0FF, #0700, #4F0B, #06E0, #3F00, #0000, #0000
                ArchiveLayerRow #00E8, #BF15, #0000, #E0C8, #0700, #1F2A, #07E0, #7F00, #0000, #0000
                ArchiveLayerRow #00F8, #670F, #0000, #C0DF, #0300, #4F28, #0FF0, #FF00, #0000, #0000
                ArchiveLayerRow #00F0, #1E09, #0080, #C0EB, #0100, #1F00, #03E0, #FF00, #0000, #0000

                ; вывод экранных строк 176..183
Rows176:        LD HL, #D0DA
                ArchiveLayerRow #00E0, #FF06, #00E0, #80FF, #000C, #0AC1, #0370, #FF00, #0000, #0000
                ArchiveLayerRow #00E0, #BF03, #00F8, #80EF, #003C, #0A60, #01F0, #FF00, #0000, #0000
                ArchiveLayerRow #0080, #D700, #00FE, #012F, #00FE, #0078, #00A0, #7E00, #0000, #0000
                ArchiveLayerRow #0080, #6D00, #00FF, #0114, #00FE, #8030, #00F0, #3F00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0100, #00FF, #C001, #0090, #1C00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0100, #00FF, #C007, #0020, #0F00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #00FF, #E03F, #0080, #8100, #0000, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0100, #00FF, #E01F, #0080, #8600, #0000, #8006

                ; вывод экранных строк 184..191
Rows184:        LD HL, #D0FA
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #00FF, #E01F, #00E0, #8100, #0000, #C03F
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #F01F, #04D0, #C200, #0000, #C0FF
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #F01F, #00AC, #E080, #0000, #40FD
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #F00F, #28FC, #E040, #0000, #80FA
                ArchiveLayerRow #1000, #0000, #00FF, #0300, #80FF, #F807, #BF6F, #F020, #0000, #80F7
                ArchiveLayerRow #0000, #0000, #00FF, #0700, #80FF, #F803, #5F55, #E000, #0000, #00F4
                ArchiveLayerRow #1000, #0000, #08FF, #0700, #C0FF, #F887, #AE7E, #F000, #0000, #00EA
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000

Restore:        JP #0000                                                        ; RunBankMenu записывает адрес RestoreLayerStack

                endmodule
                endmodule
