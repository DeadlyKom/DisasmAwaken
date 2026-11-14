                module ArchiveStartLayerPrograms
                module First
                ; Документация [исполняемый слой](../../Docs/BankArchiveTileLayers.md#исполняемые-слои)
                ; Каждая группа выводит восемь строк по 20 байтов, начиная с правого края.

                ; вывод экранных строк 24..31
Entry:          LD HL, #C07A
                ArchiveLayerRow #FFB5, #6D95, #48FF, #1700, #B4FF, #FFFF, #FEFF, #FF00, #0000, #0000
                ArchiveLayerRow #FFDF, #B6AA, #2AFF, #2E00, #F6EF, #FFFF, #ABFF, #FF08, #0000, #0000
                ArchiveLayerRow #FF54, #4911, #A4FF, #1360, #C9FF, #FFFF, #FFFF, #FF00, #0000, #0000
                ArchiveLayerRow #DFBB, #0224, #15FF, #0B00, #DEFF, #FFFF, #FFFB, #FF00, #0000, #0000
                ArchiveLayerRow #7F05, #0000, #48FB, #0200, #716F, #FFFD, #FFF7, #FF00, #0000, #0000
                ArchiveLayerRow #BF05, #0000, #22FF, #0300, #40DF, #BFBE, #FFEA, #FF00, #0000, #0000
                ArchiveLayerRow #DF02, #0000, #54B9, #0000, #C029, #7FA9, #D5DF, #A300, #0000, #0000
                ArchiveLayerRow #7701, #0000, #00F6, #0000, #802F, #1A6A, #BFEA, #FF00, #0000, #0000

                ; вывод экранных строк 32..39
Rows032:        LD HL, #C09A
                ArchiveLayerRow #1F00, #0000, #2014, #0000, #0011, #1700, #408D, #7F00, #0000, #0000
                ArchiveLayerRow #EF00, #0000, #002A, #0000, #0006, #1B00, #940A, #0000, #0000, #0000
                ArchiveLayerRow #1B00, #0000, #8028, #A000, #0024, #0F00, #0004, #A900, #0000, #0000
                ArchiveLayerRow #2F00, #0000, #0028, #C0DF, #0114, #1F00, #0000, #F600, #0000, #0000
                ArchiveLayerRow #1B00, #0000, #0014, #A8B7, #0205, #0F00, #0080, #BF00, #0000, #0000
                ArchiveLayerRow #1700, #0000, #0000, #F07E, #1B48, #1F00, #00D0, #FF00, #0000, #0000
                ArchiveLayerRow #1F00, #0000, #A020, #A4DF, #2AC8, #1F00, #00F4, #AB00, #0000, #0000
                ArchiveLayerRow #0F00, #0000, #0000, #D0BA, #7544, #0F00, #007E, #7F00, #0000, #0000

                ; вывод экранных строк 40..47
Rows040:        LD HL, #C0BA
                ArchiveLayerRow #0A00, #0000, #D004, #40F7, #7A00, #0300, #A0FB, #8200, #0000, #0000
                ArchiveLayerRow #1500, #0000, #0010, #B03A, #7500, #0F00, #D0DF, #ED04, #0000, #0000
                ArchiveLayerRow #EE03, #0000, #A000, #E0E7, #7A00, #0080, #D4B7, #F000, #0000, #0000
                ArchiveLayerRow #EB3F, #0000, #1000, #F82F, #7500, #0000, #69BF, #7E00, #0000, #4000
                ArchiveLayerRow #EAEB, #0000, #A000, #0000, #0000, #0000, #0080, #FF00, #0000, #E001
                ArchiveLayerRow #EDFF, #0100, #1012, #4001, #0000, #0000, #A8F0, #D700, #0000, #D003
                ArchiveLayerRow #9B94, #0300, #A000, #A002, #5000, #0000, #00B4, #FD10, #0000, #E003
                ArchiveLayerRow #2F00, #0700, #002C, #D001, #3002, #0000, #009F, #FD00, #0B00, #A003

                ; вывод экранных строк 48..55
Rows048:        LD HL, #C0DA
                ArchiveLayerRow #5000, #0500, #0032, #A000, #7440, #0000, #C01F, #D904, #FA0B, #C002
                ArchiveLayerRow #1F11, #0200, #0015, #4001, #5405, #0000, #001C, #F400, #E083, #0700
                ArchiveLayerRow #80E3, #1100, #202D, #0000, #3413, #0040, #031C, #FD80, #4280, #0F02
                ArchiveLayerRow #8B45, #0000, #002A, #000C, #502D, #0016, #001C, #FD80, #20EE, #4F06
                ArchiveLayerRow #091D, #0000, #100B, #000A, #8056, #FF01, #001E, #FD80, #5200, #6F06
                ArchiveLayerRow #2107, #0000, #002C, #040C, #E0B4, #0F00, #0018, #FC80, #EE64, #7F04
                ArchiveLayerRow #4200, #0400, #0037, #6906, #F465, #3D00, #0418, #FC80, #5B29, #7F06
                ArchiveLayerRow #8100, #0000, #005A, #081D, #F355, #3F00, #0408, #FC00, #F5EB, #7F02

                ; вывод экранных строк 56..63
Rows056:        LD HL, #C0FA
                ArchiveLayerRow #0200, #0000, #00BF, #0464, #F4BF, #6F00, #0006, #FC00, #167D, #FF01
                ArchiveLayerRow #1100, #0000, #007F, #4900, #7075, #FF00, #0446, #FC00, #25BB, #FF00
                ArchiveLayerRow #8442, #0200, #00AF, #8201, #78FF, #FF00, #0446, #FE00, #3B2D, #7F00
                ArchiveLayerRow #4304, #0000, #00BF, #60B5, #78FF, #FF00, #0826, #FC00, #54BE, #7F00
                ArchiveLayerRow #0C08, #0500, #00DF, #406D, #F9FA, #FF01, #0062, #FF00, #16D5, #7F00
                ArchiveLayerRow #0B10, #0000, #00BF, #0200, #3CFF, #FF00, #0063, #FE00, #04CE, #3F00
                ArchiveLayerRow #0040, #0000, #006B, #9617, #7CE9, #D703, #4073, #FD00, #7075, #3F00
                ArchiveLayerRow #0200, #0000, #00AF, #CA2F, #BCDE, #FF03, #0001, #F200, #9ABA, #1F00

                ; вывод экранных строк 64..71
Rows064:        LD HL, #C81A
                ArchiveLayerRow #2000, #0000, #0051, #0040, #3CE0, #1500, #0001, #AC00, #0070, #0F00
                ArchiveLayerRow #2011, #0000, #002E, #0248, #3EDA, #FF00, #B040, #FB00, #04B8, #6700
                ArchiveLayerRow #0210, #0100, #0093, #8480, #3EAD, #3600, #E080, #D000, #5078, #3F00
                ArchiveLayerRow #1112, #0000, #004A, #1241, #3FE8, #3B00, #A040, #A00A, #00DE, #7B00
                ArchiveLayerRow #D400, #0000, #0005, #42D4, #3D92, #2E00, #0000, #50E8, #01FD, #7F00
                ArchiveLayerRow #A000, #0000, #000A, #88CF, #3D64, #3D00, #0004, #D436, #F37E, #7E00
                ArchiveLayerRow #0A0A, #0000, #0001, #2426, #3C8C, #0B00, #0000, #536D, #A81F, #FF00
                ArchiveLayerRow #5500, #0000, #0002, #0A40, #3CA8, #0E00, #0000, #2513, #C10F, #FE00

                ; вывод экранных строк 72..79
Rows072:        LD HL, #C83A
                ArchiveLayerRow #0002, #0000, #0080, #0C00, #7800, #0200, #0020, #0000, #0080, #D701
                ArchiveLayerRow #3501, #0000, #0070, #1500, #FC80, #0D00, #0040, #0116, #0100, #A601
                ArchiveLayerRow #4400, #0000, #0050, #7C00, #FC03, #0300, #0028, #0025, #0080, #FC03
                ArchiveLayerRow #910A, #0000, #002F, #BC00, #FE0F, #4600, #0014, #0017, #1540, #EA07
                ArchiveLayerRow #0410, #0000, #0055, #4A01, #BC3F, #0300, #0000, #007F, #2120, #FD0F
                ArchiveLayerRow #2000, #00A0, #00AA, #1602, #7EFF, #8400, #000A, #00FF, #0280, #FB1D
                ArchiveLayerRow #0000, #0000, #0057, #0D54, #D5F7, #4300, #8000, #08FF, #B700, #EE3F
                ArchiveLayerRow #0200, #0000, #00AD, #55B8, #40FA, #0500, #4000, #35FF, #FFF7, #D57F

                ; вывод экранных строк 80..87
Rows080:        LD HL, #C85A
                ArchiveLayerRow #0002, #0000, #F800, #0000, #0000, #0000, #0000, #0000, #0008, #5500
                ArchiveLayerRow #8002, #0000, #F800, #0000, #0000, #0000, #2000, #0003, #0071, #AD02
                ArchiveLayerRow #4000, #0000, #F800, #0000, #0000, #0000, #1808, #00AA, #0A8A, #5A45
                ArchiveLayerRow #8000, #0000, #F800, #0000, #0000, #0000, #6C0B, #0055, #A468, #BD52
                ArchiveLayerRow #0000, #0000, #6800, #0000, #0000, #0000, #BB3E, #00AA, #0B00, #D094
                ArchiveLayerRow #0000, #0000, #C000, #0000, #0000, #0000, #F62F, #004B, #0400, #A06A
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #2000, #00FF, #00AA, #0200, #4095
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #0000, #445A, #0057, #0100, #40EB

                ; вывод экранных строк 88..95
Rows088:        LD HL, #C87A
                ArchiveLayerRow #0000, #0200, #0000, #0000, #0000, #0000, #0AAD, #00B5, #0000, #0015
                ArchiveLayerRow #0000, #0A00, #0000, #0000, #0000, #0000, #EF3E, #00D6, #0100, #00EE
                ArchiveLayerRow #0000, #4400, #0400, #0000, #0000, #1040, #3740, #026D, #0000, #0015
                ArchiveLayerRow #0000, #2C95, #0200, #0000, #0000, #0080, #8BA0, #02DF, #0000, #00FA
                ArchiveLayerRow #0000, #0800, #0500, #0000, #0000, #0040, #7F40, #07AF, #0000, #0048
                ArchiveLayerRow #0000, #1052, #0200, #0000, #0000, #0000, #BF00, #0EBF, #0000, #00F4
                ArchiveLayerRow #0000, #A800, #0700, #0000, #1600, #0000, #7D80, #17FF, #0000, #00B4
                ArchiveLayerRow #0000, #0094, #0700, #0000, #1500, #0000, #BE00, #0DFF, #0000, #0068

                ; вывод экранных строк 96..103
Rows096:        LD HL, #C89A
                ArchiveLayerRow #0000, #2000, #0700, #0000, #2A00, #0000, #6A00, #0A37, #0000, #0094
                ArchiveLayerRow #0000, #0000, #0500, #0000, #3500, #0000, #1D00, #0D7B, #0000, #006C
                ArchiveLayerRow #0000, #8044, #0700, #0000, #C000, #0000, #0000, #2037, #0000, #00D8
                ArchiveLayerRow #0002, #0A90, #0700, #0040, #5D00, #0000, #FE0F, #006D, #00C0, #FF54
                ArchiveLayerRow #0004, #4100, #0000, #0000, #3400, #00E0, #AF00, #0137, #00E0, #DDBC
                ArchiveLayerRow #000A, #0400, #0000, #00A8, #4000, #00C0, #5F0D, #013A, #00F8, #D77D
                ArchiveLayerRow #0000, #0140, #0000, #0000, #E000, #00B0, #B712, #0157, #0038, #44FF
                ArchiveLayerRow #0010, #2222, #0200, #0000, #E000, #10D8, #5FD7, #073B, #000C, #00FC

                ; вывод экранных строк 104..111
Rows104:        LD HL, #C8BA
                ArchiveLayerRow #0000, #4840, #0400, #0020, #C000, #8020, #3C0F, #073F, #000A, #80FC
                ArchiveLayerRow #0002, #3094, #7D00, #0020, #ED00, #80BC, #9000, #063F, #00B6, #99FD
                ArchiveLayerRow #0000, #B406, #FE00, #0060, #F800, #80FC, #0002, #063D, #006D, #3CFF
                ArchiveLayerRow #000A, #30C1, #FD00, #0070, #F000, #401E, #0000, #042B, #0015, #AEFD
                ArchiveLayerRow #0004, #4090, #FF00, #0060, #F800, #807D, #8F38, #0636, #00FB, #FBFF
                ArchiveLayerRow #0000, #A000, #F600, #00F0, #F800, #80FC, #EF00, #042D, #00D7, #4CFF
                ArchiveLayerRow #0000, #0004, #FF00, #0080, #F100, #80F1, #F100, #0637, #00EC, #5EFF
                ArchiveLayerRow #0000, #0001, #FE00, #0040, #F200, #00F1, #FF50, #071D, #00AD, #53FD

                ; вывод экранных строк 112..119
Rows112:        LD HL, #C8DA
                ArchiveLayerRow #0000, #4000, #FA00, #0080, #7D00, #00D2, #FF60, #0605, #0093, #85DA
                ArchiveLayerRow #0000, #0090, #FC00, #0040, #0200, #00E0, #C711, #021A, #00F6, #42B7
                ArchiveLayerRow #0000, #0080, #FF00, #0094, #1500, #0088, #F701, #020B, #00ED, #A3EE
                ArchiveLayerRow #0000, #0000, #FC00, #0060, #3F00, #00D0, #F305, #020A, #007B, #41DF
                ArchiveLayerRow #0000, #00E0, #FF00, #00C0, #2F00, #0048, #8B00, #0203, #00E6, #30FB
                ArchiveLayerRow #0000, #0080, #FE00, #00D0, #2A00, #0091, #1D00, #0101, #00EF, #40FF
                ArchiveLayerRow #8000, #0000, #FE00, #00A4, #3F00, #00AA, #0600, #0100, #00BC, #8CAF
                ArchiveLayerRow #4001, #0040, #FD00, #0050, #1700, #0091, #E100, #0105, #00FC, #68FF

                ; вывод экранных строк 120..127
Rows120:        LD HL, #C8FA
                ArchiveLayerRow #8000, #00A0, #F800, #0048, #2B00, #8052, #0180, #081F, #0090, #4035
                ArchiveLayerRow #A001, #0000, #C000, #00A0, #0F00, #80A7, #DD40, #00AF, #00F0, #AAFD
                ArchiveLayerRow #8000, #0000, #0000, #0050, #0100, #C00A, #9840, #08FF, #0200, #75C5
                ArchiveLayerRow #0005, #0880, #0100, #80E8, #0600, #A013, #7120, #00FF, #0340, #FF3A
                ArchiveLayerRow #F001, #00F0, #0600, #0085, #0000, #E016, #0000, #00FF, #1F00, #B733
                ArchiveLayerRow #4405, #20FE, #0B00, #00E2, #0000, #B03D, #4900, #00FF, #0B00, #DE0A
                ArchiveLayerRow #A801, #80AA, #1F00, #0000, #0000, #D876, #1800, #00FF, #7F00, #B80C
                ArchiveLayerRow #4044, #06DC, #7F00, #0000, #0000, #E43A, #1000, #00FF, #3F00, #F4C3

                ; вывод экранных строк 128..135
Rows128:        LD HL, #D01A
                ArchiveLayerRow #F008, #1824, #5000, #0000, #0000, #00D5, #0000, #00F5, #E500, #1043
                ArchiveLayerRow #E002, #6CB0, #A000, #0040, #0300, #00BA, #0000, #00FF, #BB00, #C0C1
                ArchiveLayerRow #F247, #0040, #9340, #0000, #3E00, #0035, #0100, #00DF, #F703, #E0F3
                ArchiveLayerRow #F015, #FAA0, #C50A, #0100, #3F04, #00A8, #0000, #00FB, #5F01, #F050
                ArchiveLayerRow #20F8, #6F03, #0BF4, #0500, #3408, #0032, #0100, #00D6, #AB06, #F8B0
                ArchiveLayerRow #55FF, #B544, #96FF, #0510, #A810, #0004, #0002, #007D, #7F03, #38DC
                ArchiveLayerRow #A0AF, #7B8D, #28F9, #1F82, #F528, #0048, #0004, #0040, #CB0A, #5864
                ArchiveLayerRow #4AD5, #B612, #31FE, #5748, #D240, #0010, #0100, #0001, #7505, #10D8

                ; вывод экранных строк 136..143
Rows136:        LD HL, #D03A
                ArchiveLayerRow #FFBF, #6848, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000
                ArchiveLayerRow #FAFF, #5641, #0500, #0000, #0000, #0000, #0000, #0000, #0800, #0000
                ArchiveLayerRow #FFBF, #FA11, #4200, #0000, #0000, #0000, #A800, #0000, #0000, #0000
                ArchiveLayerRow #EDFF, #D527, #0900, #0000, #0000, #0000, #FF07, #0000, #0000, #0000
                ArchiveLayerRow #DFE2, #750B, #8400, #0000, #0000, #00E0, #FF0F, #0000, #0000, #0000
                ArchiveLayerRow #BBFD, #7A77, #5300, #0000, #0000, #00F8, #FF1F, #0000, #0000, #0000
                ArchiveLayerRow #46BC, #A36D, #0400, #0000, #0000, #00F8, #FF7F, #0000, #0000, #0000
                ArchiveLayerRow #A96F, #5F92, #0B00, #0000, #0000, #00FE, #F7FF, #0000, #0000, #8000

                ; вывод экранных строк 144..151
Rows144:        LD HL, #D05A
                ArchiveLayerRow #A216, #A56A, #0500, #0000, #0000, #00EF, #7EF7, #0000, #0000, #0000
                ArchiveLayerRow #D36B, #5B35, #1100, #0000, #0000, #80FF, #FDDD, #0100, #0000, #0000
                ArchiveLayerRow #78B5, #7FEF, #1F00, #0000, #0000, #C0BB, #7FA1, #0100, #0000, #0000
                ArchiveLayerRow #B7FF, #FDFF, #E200, #0000, #0000, #E0FF, #BF7B, #0300, #0000, #0000
                ArchiveLayerRow #FE07, #00F0, #3F00, #0000, #0000, #E0AF, #FCA0, #0300, #0000, #0000
                ArchiveLayerRow #3F00, #0000, #F000, #0000, #0000, #A0FF, #37B2, #0300, #0000, #0000
                ArchiveLayerRow #0B00, #0000, #C000, #0000, #0000, #F07E, #41E8, #0300, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F03F, #10C0, #0300, #0000, #0000

                ; вывод экранных строк 152..159
Rows152:        LD HL, #D07A
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F01F, #2288, #0300, #0000, #0000
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #F0AF, #2AC4, #0300, #1500, #0000
                ArchiveLayerRow #0000, #0000, #0000, #E0FF, #0000, #F097, #3384, #0340, #5E00, #0000
                ArchiveLayerRow #0000, #0000, #0000, #E0FF, #0700, #F813, #5803, #0300, #0D00, #0000
                ArchiveLayerRow #0000, #0000, #0000, #F05B, #0F00, #F00D, #BC84, #2300, #0000, #0000
                ArchiveLayerRow #0040, #0001, #0000, #E827, #0800, #F060, #6E86, #0300, #0000, #0000
                ArchiveLayerRow #00A0, #110E, #0000, #0008, #1000, #0000, #DF42, #0300, #0200, #0040
                ArchiveLayerRow #0020, #9A00, #0000, #E488, #1300, #0000, #77F0, #0340, #4000, #0000

                ; вывод экранных строк 160..167
Rows160:        LD HL, #D09A
                ArchiveLayerRow #00C0, #0F01, #0000, #C881, #1900, #4000, #4902, #0300, #6000, #0000
                ArchiveLayerRow #00D0, #9F07, #0000, #341E, #1C00, #4090, #00C0, #0300, #0200, #0000
                ArchiveLayerRow #00FC, #1D1F, #0000, #3C1E, #1E00, #E040, #41E0, #0700, #471A, #0000
                ArchiveLayerRow #00FC, #9F1F, #0000, #F83F, #1F00, #6020, #00F9, #0700, #003E, #0000
                ArchiveLayerRow #00F8, #3F1F, #0000, #F0FF, #1F00, #2042, #00F8, #0720, #3005, #0000
                ArchiveLayerRow #00F4, #002F, #0000, #F8ED, #1F00, #E00B, #009F, #0700, #8002, #0000
                ArchiveLayerRow #00F8, #0107, #0000, #F0DC, #1F00, #8007, #10D0, #0F00, #0005, #0000
                ArchiveLayerRow #00F4, #0F07, #0000, #E8CB, #1F00, #A002, #A0C8, #0F00, #0000, #0000

                ; вывод экранных строк 168..175
Rows168:        LD HL, #D0BA
                ArchiveLayerRow #00F0, #FD06, #0000, #C854, #1F00, #980A, #04C2, #0F00, #0000, #0000
                ArchiveLayerRow #00F0, #4605, #0000, #5008, #1D00, #5750, #04C4, #1F00, #0000, #0000
                ArchiveLayerRow #00B0, #0008, #0000, #D814, #0F00, #4F42, #04E0, #1F00, #0000, #0000
                ArchiveLayerRow #00E8, #AA05, #0000, #4008, #0700, #DF00, #04C0, #1F00, #0000, #0000
                ArchiveLayerRow #00A8, #3504, #0000, #D0AF, #0700, #4F0A, #16C0, #3F00, #0000, #0000
                ArchiveLayerRow #00C8, #5611, #0000, #A048, #0300, #0B2A, #06E0, #7F00, #0000, #0000
                ArchiveLayerRow #00F8, #0206, #0000, #C08D, #0300, #0F28, #03C0, #FE00, #0000, #0000
                ArchiveLayerRow #0020, #0509, #0080, #80CA, #0100, #1500, #03F0, #FD00, #0000, #0000

                ; вывод экранных строк 176..183
Rows176:        LD HL, #D0DA
                ArchiveLayerRow #00C0, #7D02, #00A0, #80AB, #000C, #0080, #0140, #FC00, #0000, #0000
                ArchiveLayerRow #0020, #9E00, #00F8, #004B, #003C, #0060, #00A0, #6E00, #0000, #0000
                ArchiveLayerRow #0080, #2501, #A0FC, #000D, #00FC, #0030, #0020, #3D00, #0000, #0000
                ArchiveLayerRow #0000, #0800, #08FF, #0100, #00FE, #8010, #0060, #1C00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #52FF, #0100, #00FE, #C001, #0080, #0A00, #0000, #0000
                ArchiveLayerRow #0000, #0000, #25FF, #0100, #00FE, #C007, #0000, #0400, #0000, #0000
                ArchiveLayerRow #0000, #0000, #50FF, #0300, #00FF, #C03F, #0000, #8100, #0000, #0000
                ArchiveLayerRow #0100, #0000, #0AFF, #0100, #00FF, #E01F, #0080, #8400, #0000, #0005

                ; вывод экранных строк 184..191
Rows184:        LD HL, #D0FA
                ArchiveLayerRow #0000, #0000, #08FF, #0300, #00FE, #E01F, #00A0, #8000, #0000, #C03F
                ArchiveLayerRow #0900, #0000, #44FF, #0300, #80FF, #F00F, #04C0, #C200, #0000, #80FF
                ArchiveLayerRow #1400, #0000, #00FF, #0300, #80FF, #F01F, #0038, #C080, #0000, #40F8
                ArchiveLayerRow #1C00, #0000, #60FF, #0300, #80FF, #F007, #08D4, #E800, #0008, #80F2
                ArchiveLayerRow #3000, #0000, #10FF, #0300, #80FF, #F007, #2129, #E020, #0001, #00E5
                ArchiveLayerRow #3C00, #0000, #38FF, #0700, #80FF, #F803, #4E44, #E800, #0002, #00D2
                ArchiveLayerRow #3000, #0000, #0CFF, #0700, #80FF, #F805, #0D12, #E800, #0000, #00C8
                ArchiveLayerRow #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000, #0000

Restore:        JP #0000                                                        ; RunBankMenu записывает адрес RestoreLayerStack

                endmodule
                endmodule
