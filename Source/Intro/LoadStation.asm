                module Intro
                module LoadStation
                ; Физические параметры [источники и потребители](../../Docs/IntroPhysicalParameters.md)
                ; Документация [переносимый загрузчик станции](../../Docs/IntroStationTransition.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Переносимая завершающая стадия, поиск STATIONF.C и чтение #C0 секторов
; исходная запись 3, файловые смещения #02B7..#0314
                ; In:
                ;   этот код перенесён в #5D3B, распаковщик доступен в #6E31, 7FFD разблокирован
                ;   каталог TR-DOS содержит STATIONF.C, 4000..5AFF и экран банка 7 доступны
                ; Out:
                ;   распакованный экран скопирован в банк 7, страница #18, I=#3F, IM 1, IFF=0, IY=#5C3A
                ;   на входе TR-DOS HL=#6000, DE содержит сектор и дорожку из заголовка, BC=#C005
                ;   SP=#5FFD содержит возврат #6300, управление передано через JP
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, I, IM, IFF, R, экран, системные поля TR-DOS и 7FFD
                ; Note:
                ;   блок не проверяет результат поиска и чтения заголовка
                ;   модель исполняет экранную и банковую часть, две функции каталога подменены, секторное чтение не выполняется
; -----------------------------------------
Entry:          CALL @IntroUnpack.UnpackScreen.Entry
                LD A, #1F
                LD BC, #7FFD
                OUT (C), A
                LD HL, #D800
                LD DE, #D801
                LD BC, #02FF
                LD (HL), L
                LDIR
                LD HL, #4000
                LD DE, #C000
                LD BC, #1B00
                LDIR
                DI
                LD SP, #5FFF
                LD A, #3F
                LD I, A
                IM 1
                LD A, #18
                LD BC, #7FFD
                OUT (C), A
                LD IY, #5C3A
                LD HL, @IntroStationFileKey.Entry
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD C, #0A
                CALL @TrDos.Dispatch
                LD A, C
                LD C, #08
                CALL @TrDos.Dispatch
                LD HL, #6300
                PUSH HL
                LD HL, #6000
                LD DE, (#5CEB)
                LD B, #C0
                LD C, #05
                JP @TrDos.Dispatch


                endmodule
                endmodule
