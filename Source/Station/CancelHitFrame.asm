                module Station
                module CancelHitFrame
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
; -----------------------------------------
; Удаление двух слов кадра попадания перед возвратом без изменения геометрии
; исходная запись 4, файловые смещения #6A15..#6A16
; In:
;   на SP находятся FGeometryHitFrame и за ним FPointerGuardFrame
; Out:
;   два слова попадания отброшены, исходный контекст возвращён через ReturnGeometry, Carry=0
; Corrupt:
;   HL, DE, BC, AF, IX
; Note:
;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
;   это внутреннее продолжение, обычный CALL без вложенного кадра недопустим
; -----------------------------------------
                ; отбрасывание FGeometryHitFrame перед возвратом без действия
Entry:          POP BC
                POP BC
                ; JP @Station.ReturnGeometry.Entry, продолжение в ReturnGeometry.asm

                endmodule
                endmodule
