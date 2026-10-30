                module Station
                module HandleItem31
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [номер строки, Z и отдельный вход нажатия](../../Docs/MissionHover.md)
; -----------------------------------------
; Вход наведения элемента 31, хвостовое обновление подсветки миссии
; исходная запись 4, файловые смещения #1145..#1147
; In:
;   тот же входной контекст и предусловия, что у UpdateMissionRowHover
; Out:
;   хвостовой переход UpdateMissionRowHover с исходным адресом возврата, дальнейшие выходы по его договору
; Corrupt:
;   HL, DE, BC, AF, AF' по UpdateMissionRowHover
; Note:
;   это только трёхбайтовый вход наведения из EventHandler элемента 31
;   диспетчер нажатия использует EventHandler+3, то есть отдельный вход 6E9C, его алгоритм ещё разбирается
;   описание наведения не считается разбором принятия или отмены миссии
; -----------------------------------------
Entry:          JP @Station.UpdateMissionRowHover.Entry

                endmodule
                endmodule
