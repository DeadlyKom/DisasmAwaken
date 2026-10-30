                module ActionBoot
                module InitializeFlight
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Перенос ядра в #6000, загрузка графических банков и запуск полётного режима
; исходная запись 17, файловые смещения #0043..#00ED
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          LD SP, #C000
                PUSH HL
                LD DE, #6000
                LD BC, #1F8F
                LDIR
                LD A, #1E
                CALL #AB1B
                LD A, #09
                LD (#5D06), A
                LD HL, #42F4
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #C000
                PUSH HL
                LD A, #03
                LD C, #0E
                CALL @TrDos.Dispatch
                POP HL
                LD D, H
                LD E, L
                CALL #AB23
                LD A, #1B
                CALL #AB1B
                LD HL, #42D9
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, #42D0
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #EC00
                PUSH HL
                LD A, #03
                LD C, #0E
                CALL @TrDos.Dispatch
                POP HL
                LD A, #19
                CALL #AB1B
                LD HL, #42EB
                CALL @ActionBoot.GetFileLocation.Entry
                LD (#5E20), HL
                LD (#5E23), A
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, #42E2
                CALL @ActionBoot.GetFileLocation.Entry
                LD HL, #DADE
                CALL @ActionBoot.LoadFileAtAddress.Entry
                LD A, #1C
                CALL #AB1B
                LD HL, #42FD
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                CALL @ActionBoot.LoadFileToBank.Entry
                LD A, #18
                CALL #AB1B
                CALL @ActionBoot.InitializeRandomStates.Entry
                CALL @ActionBoot.BuildProjectionTable.Entry
                CALL @ActionBoot.BuildReciprocalTable.Entry
                CALL @ActionBoot.BuildBitmapTables.Entry
                LD A, #19
                CALL #AB1B
                CALL #EC0E
                JP #A82D


                endmodule
                endmodule
