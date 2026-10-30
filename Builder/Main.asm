; -----------------------------------------
; сборка исходного Awakenv02.trd средствами SjASMPlus
; адреса DISP восстанавливают только размещение, заданное оригинальными загрузчиками
; -----------------------------------------
                DEVICE ZXSPECTRUM48
                include "../Includes/Const/Include.inc"
                include "../Includes/Structs/Include.inc"
                include "../Includes/Variables/Include.inc"
                LUA PASS1
                    dofile("Tools/pack.lua")
                    reset_report()
                ENDLUA
                EMPTYTRD "Awakenv02.trd", "AWAKEN"

                ; сборка исходных секторов записи 3
                ORG 0
                include "../Source/Files/03_AWAKEN.inc"
                assert $ == #2D00
                SAVETRD "Awakenv02.trd", "S03.C", 0, 11520

                ; сборка исходных секторов записи 4
                ORG 0
                include "../Source/Files/04_STATIONF.inc"
                assert $ == #A000
                SAVETRD "Awakenv02.trd", "S04.C", 0, 40960

                ; сборка исходных секторов записи 5
                ORG 0
                include "../Source/Files/05_LANG.inc"
                assert $ == #1000
                SAVETRD "Awakenv02.trd", "S05.C", 0, 4096

                ; сборка исходных секторов записи 6
                ORG 0
                include "../Source/Files/06_D3D.inc"
                assert $ == #3F00
                SAVETRD "Awakenv02.trd", "S06.C", 0, 16128

                ; сборка исходных секторов записи 7
                ORG 0
                include "../Source/Files/07_KARTA.inc"
                assert $ == #2E00
                SAVETRD "Awakenv02.trd", "S07.C", 0, 11776

                ; сборка исходных секторов записи 8
                ORG 0
                include "../Source/Files/08_HELP.inc"
                assert $ == #1800
                SAVETRD "Awakenv02.trd", "S08.C", 0, 6144

                ; сборка исходных секторов записи 9
                ORG 0
                include "../Source/Files/09_stscr.inc"
                assert $ == #EF00
                SAVETRD "Awakenv02.trd", "S09.C", 0, 61184

                ; сборка исходных секторов записи 10
                ORG 0
                include "../Source/Files/10_MUZ1.inc"
                assert $ == #1D00
                SAVETRD "Awakenv02.trd", "S10.C", 0, 7424

                ; сборка исходных секторов записи 11
                ORG 0
                include "../Source/Files/11_SAVE1.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S11.C", 0, 512

                ; сборка исходных секторов записи 12
                ORG 0
                include "../Source/Files/12_SAVE2.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S12.C", 0, 512

                ; сборка исходных секторов записи 13
                ORG 0
                include "../Source/Files/13_SAVE3.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S13.C", 0, 512

                ; сборка исходных секторов записи 14
                ORG 0
                include "../Source/Files/14_SAVE4.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S14.C", 0, 512

                ; сборка исходных секторов записи 15
                ORG 0
                include "../Source/Files/15_SAVE5.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S15.C", 0, 512

                ; сборка исходных секторов записи 16
                ORG 0
                include "../Source/Files/16_SAVE0.inc"
                assert $ == #0200
                SAVETRD "Awakenv02.trd", "S16.C", 0, 512

                ; сборка исходных секторов записи 17
                ORG 0
                include "../Source/Files/17_ACTION.inc"
                assert $ == #A000
                SAVETRD "Awakenv02.trd", "S17.C", 0, 40960

                ; сборка исходных секторов записи 18
                ORG 0
                include "../Source/Files/18_DATAS.inc"
                assert $ == #1D00
                SAVETRD "Awakenv02.trd", "S18.C", 0, 7424

                ; сборка исходных секторов записи 19
                ORG 0
                include "../Source/Files/19_3DPART.inc"
                assert $ == #2100
                SAVETRD "Awakenv02.trd", "S19.C", 0, 8448

                ; сборка исходных секторов записи 20
                ORG 0
                include "../Source/Files/20_VOXAL0.inc"
                assert $ == #2C00
                SAVETRD "Awakenv02.trd", "S20.C", 0, 11264

                ; сборка исходных секторов записи 21
                ORG 0
                include "../Source/Files/21_VOXAL.inc"
                assert $ == #0F00
                SAVETRD "Awakenv02.trd", "S21.C", 0, 3840

                ; сборка исходных секторов записи 22
                ORG 0
                include "../Source/Files/22_CONTROL0.inc"
                assert $ == #1B00
                SAVETRD "Awakenv02.trd", "S22.C", 0, 6912

                ; сборка исходных секторов записи 23
                ORG 0
                include "../Source/Files/23_CONTROL.inc"
                assert $ == #1A00
                SAVETRD "Awakenv02.trd", "S23.C", 0, 6656

                ; сборка исходных секторов записи 24
                ORG 0
                include "../Source/Files/24_OBJECT3D.inc"
                assert $ == #2A00
                SAVETRD "Awakenv02.trd", "S24.C", 0, 10752

                ; сборка исходных секторов записи 25
                ORG 0
                include "../Source/Files/25_PANEL.inc"
                assert $ == #0600
                SAVETRD "Awakenv02.trd", "S25.C", 0, 1536

                ; сборка исходных секторов записи 26
                ORG 0
                include "../Source/Files/26_PANELF.inc"
                assert $ == #0600
                SAVETRD "Awakenv02.trd", "S26.C", 0, 1536

                ; сборка исходных секторов записи 27
                ORG 0
                include "../Source/Files/27_PANELMET.inc"
                assert $ == #0600
                SAVETRD "Awakenv02.trd", "S27.C", 0, 1536

                ; сборка исходных секторов записи 28
                ORG 0
                include "../Source/Files/28_PANELFF.inc"
                assert $ == #0700
                SAVETRD "Awakenv02.trd", "S28.C", 0, 1792

                ; сборка исходных секторов записи 29
                ORG 0
                include "../Source/Files/29_FINALF.inc"
                assert $ == #4B00
                SAVETRD "Awakenv02.trd", "S29.C", 0, 19200

                ; сборка исходных секторов записи 30
                ORG 0
                include "../Source/Files/30_scene1po.inc"
                assert $ == #4900
                SAVETRD "Awakenv02.trd", "S30.C", 0, 18688

                ; сборка исходных секторов записи 31
                ORG 0
                include "../Source/Files/31_choose1.inc"
                assert $ == #1B00
                SAVETRD "Awakenv02.trd", "S31.C", 0, 6912

                ; сборка исходных секторов записи 32
                ORG 0
                include "../Source/Files/32_choose2.inc"
                assert $ == #1B00
                SAVETRD "Awakenv02.trd", "S32.C", 0, 6912

                ; сборка исходных секторов записи 33
                ORG 0
                include "../Source/Files/33_BANK0.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S33.C", 0, 16384

                ; сборка исходных секторов записи 34
                ORG 0
                include "../Source/Files/34_BANK1.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S34.C", 0, 16384

                ; сборка исходных секторов записи 35
                ORG 0
                include "../Source/Files/35_BANK2.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S35.C", 0, 16384

                ; сборка исходных секторов записи 36
                ORG 0
                include "../Source/Files/36_BANK3.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S36.C", 0, 16384

                ; сборка исходных секторов записи 37
                ORG 0
                include "../Source/Files/37_BANK4.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S37.C", 0, 16384

                ; сборка исходных секторов записи 38
                ORG 0
                include "../Source/Files/38_BANK5.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S38.C", 0, 16384

                ; сборка исходных секторов записи 39
                ORG 0
                include "../Source/Files/39_BAR.inc"
                assert $ == #0D00
                SAVETRD "Awakenv02.trd", "S39.C", 0, 3328

                ; сборка исходных секторов записи 40
                ORG 0
                include "../Source/Files/40_BD0.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S40.C", 0, 16384

                ; сборка исходных секторов записи 41
                ORG 0
                include "../Source/Files/41_BD1.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S41.C", 0, 16384

                ; сборка исходных секторов записи 42
                ORG 0
                include "../Source/Files/42_BD2.inc"
                assert $ == #4000
                SAVETRD "Awakenv02.trd", "S42.C", 0, 16384

                ; сборка исходных секторов записи 43
                ORG 0
                include "../Source/Files/43_BD3.inc"
                assert $ == #3000
                SAVETRD "Awakenv02.trd", "S43.C", 0, 12288

                IF _ERRORS = 0
                LUA PASS3
                    dofile("Tools/pack.lua")
                    finish_image()
                ENDLUA
                ENDIF
