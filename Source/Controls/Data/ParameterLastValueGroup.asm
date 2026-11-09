                module ParameterLastValueGroup
                ; Документация [группы исходных шаблонов](../../../Docs/ControlsParameterTables.md)
                assert $ == #DF55
                ; -----------------------------------------
                ; исходная физическая запись Group3
Group3:         FParameterValueBytes {
                    #00,                                                        ; Value00, групповая прибавка к соответствующему полю Parameters
                    #FF,                                                        ; Value01, групповая прибавка к соответствующему полю Parameters
                    #FF,                                                        ; Value02, групповая прибавка к соответствующему полю Parameters
                    #00,                                                        ; Value03, групповая прибавка к соответствующему полю Parameters
                    #00,                                                        ; Value04, групповая прибавка к соответствующему полю Parameters
                    #00,                                                        ; Value05, групповая прибавка к соответствующему полю Parameters
                    #1A,                                                        ; Value06, групповая прибавка к соответствующему полю Parameters
                    #05,                                                        ; Value07, групповая прибавка к соответствующему полю Parameters
                    #06,                                                        ; Value08, групповая прибавка к соответствующему полю Parameters
                    #FE,                                                        ; Value09, групповая прибавка к соответствующему полю Parameters
                    #F0,                                                        ; Value10, групповая прибавка к соответствующему полю Parameters
                    #F6,                                                        ; Value11, групповая прибавка к соответствующему полю Parameters
                    #0A,                                                        ; Value12, групповая прибавка к соответствующему полю Parameters
                    #0A,                                                        ; Value13, групповая прибавка к соответствующему полю Parameters
                    #00                                                         ; Value14, групповая прибавка к соответствующему полю Parameters
                }
                assert $ == #DF64
                endmodule
