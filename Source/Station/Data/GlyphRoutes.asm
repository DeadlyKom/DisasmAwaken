                module GlyphRoutes
; Документация [рисование глифа](../../../Docs/GlyphRendering.md)
; порядок записи, сдвиг X, признак крайней колонки, младшие три бита Y
                assert $ == #9200
Shift0Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift0.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift0Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y0:        FGlyphRoute {
                    @Station.DrawGlyphShift0.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y1:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y2:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y3:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y4:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y5:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y6:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge0Y7:        FGlyphRoute {
                    @Station.SplitGlyphShift0.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift0.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift1.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift1Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift1.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift1.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge1.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge1Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge1.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge1.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift2.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift2Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift2.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift2.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge2.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge2Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge2.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge2.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift3.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift3Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift3.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift3.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge3.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge3Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge3.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge3.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift4.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift4Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift4.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift4.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge4.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge4Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge4.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge4.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift5.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift5Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift5.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift5.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge5.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge5Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge5.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge5.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift6.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift6Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift6.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift6.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge6.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge6Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge6.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge6.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y0:       FGlyphRoute {
                    @Station.DrawGlyphShift7.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y1:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Entry,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows1                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y2:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows6,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows2                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y3:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows5,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows3                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y4:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows4,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows4                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y5:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows3,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows5                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y6:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows2,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows6                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Shift7Y7:       FGlyphRoute {
                    @Station.SplitGlyphShift7.Rows1,                            ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphShift7.Rows7                              ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y0:        FGlyphRoute {
                    @Station.DrawGlyphEdge7.Entry,                              ; FGlyphRoute.First, участок до границы знакоместа
                    #0000                                                       ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y1:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Entry,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows1                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y2:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows6,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows2                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y3:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows5,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows3                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y4:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows4,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows4                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y5:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows3,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows5                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y6:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows2,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows6                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
Edge7Y7:        FGlyphRoute {
                    @Station.SplitGlyphEdge7.Rows1,                             ; FGlyphRoute.First, участок до границы знакоместа
                    @Station.DrawGlyphEdge7.Rows7                               ; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми
                }
                assert $ == #9400
                endmodule
