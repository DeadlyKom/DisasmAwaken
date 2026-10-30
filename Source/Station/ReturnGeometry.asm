                module Station
                module ReturnGeometry
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
; -----------------------------------------
; Возврат исходных регистров и исходного A с очисткой Carry через AND A
; исходная запись 4, файловые смещения #6A17..#6A1E
; In:
;   SP указывает на ранее созданный FPointerGuardFrame без вложенных слов
; Out:
;   HL, DE, BC, IX и A восстановлены, F=AND_flags(исходный A), Carry=0
; Corrupt:
;   HL, DE, BC, AF, IX
; Note:
;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
;   Byte A сохраняется, но исходные флаги не восстанавливаются побитно из-за завершающего AND A
; -----------------------------------------
                ; снятие базового FPointerGuardFrame, исходный A возвращается отдельно от исходных флагов
Entry:          POP BC
                POP DE
                POP HL
                POP AF
                POP IX
                ; очистка Carry и расчёт S,Z,P/V по восстановленному исходному A
                AND A
                RET

                endmodule
                endmodule
