                module ArchiveStartLayerPrograms
                module Second
                ; Документация [исполняемый слой](../../Docs/BankArchiveTileLayers.md#исполняемые-слои)
                ; Каждая группа выводит восемь строк по 20 байтов, начиная с правого края.

                ; вывод экранных строк 24..31
Entry:          LD HL, #C07A
                ArchiveLayerRow #0000, #0000, #0000, #0095, #0200, #0000, #0000, #00AB, #2A21, #0000
                ArchiveLayerRow #0000, #0000, #0000, #A0FE, #0700, #0000, #0000, #00AA, #AA02, #0000
                ArchiveLayerRow #0000, #0000, #0000, #90F0, #0F00, #0000, #0000, #0045, #0100, #0000
                ArchiveLayerRow #0000, #0000, #0000, #48E0, #1F00, #0000, #0000, #0028, #0200, #0000
                ArchiveLayerRow #0000, #0000, #0000, #28C0, #3F00, #0000, #0000, #00C2, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #14C8, #6100, #0000, #0000, #0015, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0200, #E000, #0000, #0000, #0040, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0940, #8001, #0000, #0000, #FC0A, #0000, #0000

                ; вывод экранных строк 32..39
Rows032:        LD HL, #C09A
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0003, #0000, #0080, #FF00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #A000, #0006, #0000, #0000, #0100, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #F007, #8707, #0000, #0000, #000A, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0080, #F8FF, #1307, #0000, #0000, #0005, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #FCFF, #1B0F, #0000, #0000, #0008, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0080, #FCFF, #3F0E, #0000, #0000, #0005, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #FCFF, #7F0D, #0000, #0000, #002A, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #FEFF, #7F0C, #0000, #0000, #000A, #0000, #0000

                ; вывод экранных строк 40..47
Rows040:        LD HL, #C0BA
                ArchiveLayerRow #0000, #0000, #0000, #FCFF, #7F04, #0000, #0000, #8035, #0100, #0000
                ArchiveLayerRow #8000, #0000, #0000, #FEFF, #FF08, #0800, #0000, #E09A, #0400, #0000
                ArchiveLayerRow #C017, #0000, #0000, #FCFF, #7F04, #0700, #0000, #F86D, #4B04, #2000
                ArchiveLayerRow #E07F, #0000, #0000, #FEFF, #7F08, #0000, #0000, #7EB6, #9611, #C001
                ArchiveLayerRow #E0FF, #0000, #0000, #0000, #000C, #0000, #0080, #1F5D, #7F5F, #F853
                ArchiveLayerRow #E0FF, #0100, #0000, #0000, #0000, #0000, #00F0, #07AB, #FE5B, #FF0F
                ArchiveLayerRow #80FF, #0300, #0000, #0000, #0004, #0000, #00FC, #015F, #ADEE, #FE27
                ArchiveLayerRow #00C0, #0700, #0000, #0000, #0000, #0000, #809F, #01AB, #FFD3, #FF0F

                ; вывод экранных строк 48..55
Rows048:        LD HL, #C0DA
                ArchiveLayerRow #4081, #0700, #0000, #0000, #0002, #0000, #F09F, #0105, #FE1F, #D003
                ArchiveLayerRow #001B, #0200, #0000, #0000, #0003, #0000, #7C5E, #0116, #F8F7, #0700
                ArchiveLayerRow #C0F3, #0100, #0040, #000C, #8003, #00F0, #031E, #01DA, #7780, #0F03
                ArchiveLayerRow #88EF, #1200, #00A0, #000C, #4007, #007F, #001E, #01A5, #F8FE, #CF06
                ArchiveLayerRow #803F, #0400, #0040, #021E, #C006, #FF03, #00DF, #01CA, #F3C3, #6F07
                ArchiveLayerRow #209F, #0000, #0080, #0F2F, #F007, #7F00, #809F, #0095, #FFF7, #7F06
                ArchiveLayerRow #4000, #0000, #0040, #FF5E, #FF07, #0000, #045C, #00C2, #FFFF, #FF06
                ArchiveLayerRow #8000, #0200, #00C0, #BFBF, #FF07, #0088, #0C0E, #0099, #FFFF, #7F13

                ; вывод экранных строк 56..63
Rows056:        LD HL, #C0FA
                ArchiveLayerRow #0000, #0000, #0000, #DFFF, #FE07, #0000, #0C0F, #0084, #FFFF, #FF23
                ArchiveLayerRow #0080, #0000, #0000, #FFAE, #FF03, #0088, #0447, #00A8, #FFFF, #FF51
                ArchiveLayerRow #0002, #0000, #0000, #F64B, #7A00, #0004, #2467, #0042, #FFFF, #7FA0
                ArchiveLayerRow #0024, #0100, #0000, #FEFF, #7D00, #0050, #1D67, #000A, #FFFF, #7FA0
                ArchiveLayerRow #000C, #0000, #0000, #FDFF, #3F00, #0020, #0467, #0080, #BEFF, #7F40
                ArchiveLayerRow #0010, #0000, #0000, #3EA1, #3E00, #0008, #8473, #000A, #5FFF, #3F80
                ArchiveLayerRow #0060, #0000, #0000, #FE3F, #3F00, #0020, #F873, #0000, #FEFF, #3F00
                ArchiveLayerRow #0010, #0000, #0000, #FEBF, #3E00, #0020, #A603, #0008, #FEFF, #1F00

                ; вывод экранных строк 64..71
Rows064:        LD HL, #C81A
                ArchiveLayerRow #0000, #0000, #0000, #FEFF, #3E00, #0000, #F801, #0001, #CCFF, #2F00
                ArchiveLayerRow #0000, #0000, #0000, #FEFF, #3F00, #0000, #FD01, #0000, #16FE, #7F00
                ArchiveLayerRow #0000, #0100, #0000, #FEF5, #3F00, #00C0, #F200, #0000, #FCFF, #7F10
                ArchiveLayerRow #0010, #0000, #0000, #F6F5, #3F00, #0080, #FA00, #005F, #5DFF, #7F30
                ArchiveLayerRow #0000, #0000, #0000, #FEFF, #3F00, #0000, #0000, #00FF, #AFFF, #7F10
                ArchiveLayerRow #0000, #0000, #0000, #EEFF, #3F00, #0000, #0000, #00FF, #FFFF, #FF20
                ArchiveLayerRow #0000, #0000, #0000, #FEFF, #3F00, #0000, #0000, #00FF, #F97F, #FF50
                ArchiveLayerRow #0000, #0000, #0000, #CF6A, #3E00, #0000, #0000, #00FF, #F70F, #FF41

                ; вывод экранных строк 72..79
Rows072:        LD HL, #C83A
                ArchiveLayerRow #0000, #0000, #00C0, #BF15, #7F00, #0080, #0000, #00FF, #5BC3, #FFC1
                ArchiveLayerRow #0000, #0000, #00F0, #FF40, #FF00, #0000, #0000, #00FF, #15E0, #FFC3
                ArchiveLayerRow #0000, #0000, #00FC, #7FA1, #FE03, #0000, #0000, #00FF, #6BD1, #FF47
                ArchiveLayerRow #000A, #0000, #00FF, #FF56, #FF0F, #0000, #0000, #00FF, #BFF2, #FFAF
                ArchiveLayerRow #0000, #0080, #00FF, #FFAB, #FF3F, #0000, #0000, #08FF, #FFE9, #FF4F
                ArchiveLayerRow #2000, #0000, #00FF, #FF4F, #FFFF, #0000, #0000, #34FF, #7FED, #FF3F
                ArchiveLayerRow #0000, #0000, #00FF, #7FFF, #FFFF, #0000, #0080, #DEFF, #FFFF, #FF7F
                ArchiveLayerRow #0200, #0000, #00FF, #FFFE, #FFFF, #0000, #0080, #7FFF, #FFFF, #FFFF

                ; вывод экранных строк 80..87
Rows080:        LD HL, #C85A
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #2E00, #0000, #FA00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #5200, #0000, #FD00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #BF00, #0000, #FE00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #6D01, #0000, #FE00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #F800, #0000, #0000, #FA02, #0000, #FD00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #C000, #0000, #0000, #F501, #0000, #FE00, #0000, #0000
                ArchiveLayerRow #0020, #0000, #8000, #0000, #0000, #AA02, #0000, #F800, #0000, #0000
                ArchiveLayerRow #00A0, #0000, #8000, #0000, #0000, #AA00, #0000, #7C00, #0000, #0000

                ; вывод экранных строк 88..95
Rows088:        LD HL, #C87A
                ArchiveLayerRow #0090, #0E00, #0000, #0000, #0000, #1101, #0000, #E000, #0000, #0000
                ArchiveLayerRow #0048, #1F00, #0400, #0000, #0000, #CA00, #0000, #F800, #0000, #0000
                ArchiveLayerRow #00B0, #FF83, #0700, #0000, #0000, #3600, #0000, #F000, #0000, #0000
                ArchiveLayerRow #0040, #FFFF, #0F00, #0000, #0000, #4D00, #0000, #F000, #0000, #0000
                ArchiveLayerRow #00A0, #FEEF, #0700, #0000, #0000, #BB00, #0000, #E000, #0000, #0000
                ArchiveLayerRow #0010, #FFDF, #0F00, #0000, #0000, #5700, #0000, #F000, #0000, #0000
                ArchiveLayerRow #0044, #FDFA, #0700, #0000, #0000, #0F00, #0000, #C000, #0000, #0000
                ArchiveLayerRow #0050, #FEF7, #0F00, #0000, #0000, #3700, #0000, #8000, #0000, #0000

                ; вывод экранных строк 96..103
Rows096:        LD HL, #C89A
                ArchiveLayerRow #0000, #FAEF, #0700, #0000, #0000, #0F00, #0000, #8000, #0000, #0000
                ArchiveLayerRow #0000, #F5DF, #0F00, #0000, #0000, #3F00, #0000, #4000, #0000, #0000
                ArchiveLayerRow #0000, #FEFF, #0700, #0000, #0000, #7F00, #0000, #C000, #0000, #0A00
                ArchiveLayerRow #00C6, #1FF8, #0F00, #0040, #1D00, #7F80, #FF2F, #C000, #00C0, #FF00
                ArchiveLayerRow #00AE, #FFC3, #0100, #00AC, #3F00, #7FF0, #FFDF, #D300, #00F0, #FF03
                ArchiveLayerRow #00DE, #D741, #0800, #00FE, #6700, #3BF0, #FF6F, #A100, #00F0, #FF03
                ArchiveLayerRow #0049, #2F70, #0600, #0078, #F000, #D5F0, #FFBF, #5500, #00FC, #FE03
                ArchiveLayerRow #00BB, #FFF7, #0600, #0054, #F000, #BAF8, #FFFF, #A700, #001C, #0800

                ; вывод экранных строк 104..111
Rows104:        LD HL, #C8BA
                ArchiveLayerRow #005E, #FE78, #0E00, #0028, #C000, #BF7D, #FE1F, #0F00, #0008, #3000
                ArchiveLayerRow #00B7, #7FFF, #FF00, #0030, #ED00, #FCFE, #F006, #0700, #00B4, #9D01
                ArchiveLayerRow #005E, #FCFF, #FF00, #0078, #F900, #FFFE, #E302, #0E00, #00E8, #9F00
                ArchiveLayerRow #002E, #FBFB, #FF00, #0070, #FA00, #FF7E, #8001, #0700, #00D0, #8E00
                ArchiveLayerRow #009E, #F4FF, #FF00, #00F8, #FE00, #FFFF, #8F78, #0600, #0020, #3200
                ArchiveLayerRow #0050, #EAA9, #FF00, #00F4, #FC00, #FFFF, #FF60, #0600, #0040, #0800
                ArchiveLayerRow #00A4, #F556, #FF00, #0080, #FD00, #FFFF, #FB3D, #0600, #00C0, #0400
                ArchiveLayerRow #0096, #CA2F, #FF00, #0000, #FF00, #BFFB, #FFFD, #0F00, #0080, #0300

                ; вывод экранных строк 112..119
Rows112:        LD HL, #C8DA
                ArchiveLayerRow #0000, #F503, #FE00, #0000, #7800, #7FFF, #FFFB, #0600, #0080, #0100
                ArchiveLayerRow #00AE, #AAFC, #FF00, #0000, #0000, #BFF0, #EF79, #0E00, #0080, #0000
                ArchiveLayerRow #0040, #54C3, #FF00, #0000, #0000, #7FFE, #F775, #BE00, #0040, #0000
                ArchiveLayerRow #008F, #4A09, #FE00, #0000, #0000, #FFFC, #F33F, #7F00, #0040, #0000
                ArchiveLayerRow #C054, #B5FE, #FF00, #0000, #0000, #BFFF, #DF21, #FF00, #0020, #0000
                ArchiveLayerRow #C016, #40E0, #FF00, #0000, #0000, #7FFF, #3F90, #BF00, #0020, #0000
                ArchiveLayerRow #E015, #1685, #FF00, #0000, #0040, #BFFF, #4F00, #7F00, #0000, #0000
                ArchiveLayerRow #C02B, #50E9, #FF00, #0000, #0000, #DFFB, #F3C1, #BB00, #0000, #0000

                ; вывод экранных строк 120..127
Rows120:        LD HL, #C8FA
                ArchiveLayerRow #F015, #00F4, #FC00, #0000, #0040, #A5FF, #09C0, #7D00, #0000, #0080
                ArchiveLayerRow #F055, #00EA, #EB00, #0000, #0000, #DAF7, #FDC1, #F200, #0000, #00C0
                ArchiveLayerRow #F01B, #0010, #DD00, #0000, #0080, #E4FF, #BDE0, #AD00, #0000, #00E0
                ArchiveLayerRow #FC57, #08C0, #BB00, #0000, #0000, #F9FF, #FD60, #D600, #0000, #0070
                ArchiveLayerRow #F82F, #BDF0, #EF00, #0000, #0020, #F4BF, #7DB0, #B700, #0000, #0038
                ArchiveLayerRow #FEDF, #BAFF, #DF00, #0000, #0000, #FBFF, #FD50, #EF00, #0000, #002C
                ArchiveLayerRow #FA7F, #F7FF, #DF00, #0000, #0000, #FC7F, #38A0, #FA00, #0000, #001E
                ArchiveLayerRow #FEFF, #7FFF, #FF00, #0000, #0000, #FCFF, #1050, #F500, #0000, #000F

                ; вывод экранных строк 128..135
Rows128:        LD HL, #D01A
                ArchiveLayerRow #FFFF, #7FFE, #FF00, #0000, #0000, #FFFF, #0000, #8000, #0000, #8003
                ArchiveLayerRow #FDFF, #7FFA, #FB6C, #0000, #0010, #FFFF, #0304, #5000, #0000, #C007
                ArchiveLayerRow #FFFF, #FFFE, #FBFE, #0100, #0000, #D2FF, #0308, #4000, #0000, #E003
                ArchiveLayerRow #FFFF, #FFF3, #EFFE, #0300, #000D, #D0FF, #051C, #0000, #0000, #F001
                ArchiveLayerRow #FFFF, #FFF7, #DFFF, #0F00, #000C, #00FF, #0D31, #0000, #0000, #F800
                ArchiveLayerRow #FFFF, #FFFF, #BFFF, #1F00, #0038, #00FE, #0B32, #0000, #0000, #F800
                ArchiveLayerRow #FFFF, #FFFF, #FFFF, #3F00, #0030, #007C, #056D, #0000, #0000, #7800
                ArchiveLayerRow #FFFF, #FFFF, #7FFF, #7F00, #00E0, #00F8, #132C, #0000, #0000, #3C00

                ; вывод экранных строк 136..143
Rows136:        LD HL, #D03A
                ArchiveLayerRow #0000, #7F00, #00FF, #FFFF, #FFFF, #0000, #0000, #00FF, #57A2, #FDFF
                ArchiveLayerRow #0000, #FF00, #00FF, #FFFF, #FFFF, #0000, #0000, #00F5, #2B40, #FE7F
                ArchiveLayerRow #00C0, #FF07, #00FF, #FF55, #FFF7, #0000, #FA01, #005A, #0900, #F5D7
                ArchiveLayerRow #00C0, #FF0F, #00FF, #3F00, #FEFF, #0000, #FF07, #00AB, #0600, #E8BF
                ArchiveLayerRow #00F8, #FF3F, #00FF, #1F4A, #F8FE, #00E0, #FF0F, #0054, #0000, #A04A
                ArchiveLayerRow #00FC, #FF7F, #00FF, #4F24, #F5BF, #00F8, #FF3F, #0052, #0000, #50F5
                ArchiveLayerRow #00FF, #FFFF, #00FF, #0712, #C1FB, #00FC, #FF7F, #0001, #0000, #8016
                ArchiveLayerRow #00FF, #FFFF, #03FF, #4209, #CA57, #00FE, #FFFF, #000A, #0000, #80EA

                ; вывод экранных строк 144..151
Rows144:        LD HL, #D05A
                ArchiveLayerRow #E0FF, #FFFF, #07AF, #0100, #80EF, #00FF, #FFFF, #0102, #0000, #0015
                ArchiveLayerRow #F0FF, #FFFF, #1FD6, #0200, #40FF, #80FF, #FFFF, #090A, #0000, #006C
                ArchiveLayerRow #FEFF, #FFFF, #7F5B, #0100, #80FF, #C0FF, #FFFF, #5503, #0A00, #00AE
                ArchiveLayerRow #FFFF, #FFFF, #FFF6, #0100, #00FF, #E0FF, #FFFF, #2703, #2500, #005D
                ArchiveLayerRow #FF3F, #00F8, #FF95, #0000, #00FF, #E0FF, #FFFB, #DB82, #5E00, #00B4
                ArchiveLayerRow #FF00, #0000, #FEF5, #0100, #80FF, #F0FF, #FFFF, #2FC3, #BF00, #00D4
                ArchiveLayerRow #0F00, #0000, #C0F6, #0000, #00FF, #F2FF, #FFFB, #FF00, #AA00, #0020
                ArchiveLayerRow #0000, #0000, #00FA, #0000, #00FF, #F87F, #BFFD, #7F81, #5F01, #00D0

                ; вывод экранных строк 152..159
Rows152:        LD HL, #D07A
                ArchiveLayerRow #0000, #0000, #00A5, #0000, #00FF, #F29F, #FFDE, #FF00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #00ED, #0010, #28FF, #FFFF, #3FEF, #FF80, #7F00, #0050
                ArchiveLayerRow #0000, #0000, #00F5, #F0FF, #10FF, #FFF7, #FFC6, #FFE0, #FF00, #0024
                ArchiveLayerRow #0000, #0000, #00FA, #F0FF, #07FF, #FF9F, #FB87, #FFC0, #3F00, #00A8
                ArchiveLayerRow #0000, #0000, #00EF, #F0FF, #0FFF, #FF5D, #FDC7, #FB00, #0700, #0050
                ArchiveLayerRow #0000, #A000, #00FD, #F8FF, #0AFF, #F264, #FFEF, #2B00, #020F, #00B0
                ArchiveLayerRow #0000, #1114, #00DF, #0C1C, #10F7, #73C0, #FFF7, #0300, #0310, #0060
                ArchiveLayerRow #0000, #BE00, #00F6, #E48D, #1BFF, #4080, #7FFF, #0360, #E628, #0090

                ; вывод экранных строк 160..167
Rows160:        LD HL, #D09A
                ArchiveLayerRow #00F0, #DF07, #00EB, #ECCD, #1BBF, #6080, #7FFF, #0300, #6312, #0040
                ArchiveLayerRow #00F8, #DF3F, #00FD, #FCBE, #1FF6, #C0FB, #7FF3, #0340, #673C, #0000
                ArchiveLayerRow #00FC, #BF3F, #00FB, #7C5F, #1EFF, #E0FD, #D3ED, #7700, #6F7F, #00A0
                ArchiveLayerRow #00FE, #FF3F, #00FF, #FCBF, #1FBF, #6073, #EBFB, #8F60, #DD7F, #0040
                ArchiveLayerRow #00FC, #BF3F, #00FF, #FCFF, #1FFF, #60FF, #DFFF, #BF40, #FB3F, #0080
                ArchiveLayerRow #00FE, #193F, #00FF, #FCFF, #BFF4, #E0EF, #EBFF, #7781, #DFCF, #0040
                ArchiveLayerRow #00FC, #013F, #00FF, #FCFF, #1FFF, #D497, #3AFF, #FF42, #7F3F, #0080
                ArchiveLayerRow #00FC, #5F1F, #00FE, #FCEB, #1FFF, #F5BF, #F6FF, #FFC2, #BF41, #0040

                ; вывод экранных строк 168..175
Rows168:        LD HL, #D0BA
                ArchiveLayerRow #00FC, #FF2F, #00FF, #FCFF, #9FAF, #FC2F, #ECDF, #FF41, #FF0D, #0000
                ArchiveLayerRow #00FC, #FF1F, #00FF, #F989, #5FFB, #FF57, #3CE5, #BFC4, #F702, #0080
                ArchiveLayerRow #00FC, #851F, #00FF, #F8FF, #0FFF, #7F42, #E4E2, #DF42, #5F05, #0000
                ArchiveLayerRow #00FC, #FF2F, #00FF, #F188, #87F9, #FF13, #7EF1, #FF88, #DE02, #0040
                ArchiveLayerRow #00FC, #FF1F, #00EF, #F2FF, #07ED, #5F0B, #B7E8, #BF80, #AD00, #0000
                ArchiveLayerRow #00F8, #FF3F, #00FB, #E1E9, #47FB, #FF2A, #5FF0, #FF80, #B602, #0000
                ArchiveLayerRow #00F8, #F71F, #00FF, #E0FF, #036C, #DFA8, #2FF8, #FF40, #2900, #0000
                ArchiveLayerRow #00F0, #BF1F, #00FF, #C0EB, #41B8, #7F80, #07F4, #FF81, #5600, #0000

                ; вывод экранных строк 176..183
Rows176:        LD HL, #D0DA
                ArchiveLayerRow #00F0, #FF07, #00E4, #C0FF, #004E, #1FD5, #03F8, #FF00, #0000, #0000
                ArchiveLayerRow #00E0, #FF07, #00FB, #80FF, #00BC, #2FE4, #01F4, #FF00, #0100, #0000
                ArchiveLayerRow #00C0, #FF01, #00FE, #017F, #00FE, #9DFA, #00FA, #FF00, #7408, #0000
                ArchiveLayerRow #0080, #FF01, #00FF, #011E, #00FF, #FA7C, #04F6, #FF00, #0A04, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0100, #00FF, #D423, #08BA, #FF00, #0009, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0100, #00FF, #E84F, #04D5, #BF00, #0004, #0000
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #00FF, #EC3F, #14B4, #FF00, #804A, #0B00
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #00FF, #E83F, #84CE, #B700, #0882, #C407

                ; вывод экранных строк 184..191
Rows184:        LD HL, #D0FA
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #00FF, #F45F, #96F2, #AF00, #00A8, #E23F
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #F43F, #8DFA, #F700, #00A2, #D5FF
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #FA5F, #76FD, #EBC0, #5FDD, #E2FF
                ArchiveLayerRow #0000, #0000, #00FF, #0300, #80FF, #FA2F, #FDFF, #FD40, #E1B7, #C0FF
                ArchiveLayerRow #0000, #0000, #00FF, #0700, #80FF, #FA5F, #FFFF, #F9F0, #BEA8, #B0FF
                ArchiveLayerRow #0000, #0000, #00FF, #0700, #80FF, #FAAF, #FFFF, #FC48, #7FB7, #C0FF
                ArchiveLayerRow #0000, #0000, #00FF, #0700, #C0FF, #FDAF, #FFFF, #FAA0, #5D55, #00FF
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000

Restore:        JP #0000                                                        ; RunBankMenu записывает адрес RestoreLayerStack

                endmodule
                endmodule
