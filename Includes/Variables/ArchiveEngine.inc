                module ArchiveEngineState
MemoryMode      equ #5F5E                                                       ; режим памяти, переданный архивным меню
VectorJump      equ #5F5F                                                       ; код JP, на который указывает таблица IM2
VectorTarget    equ #5F60                                                       ; адрес в операнде JP для IM2
                endmodule
