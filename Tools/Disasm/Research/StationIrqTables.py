"""Физические BCD-части, собственный стек ISR и цепочка возвратов заливки."""
COUNTER='Source/Station/Data/StationTimer.asm'
STACK='Source/Station/Data/InterruptStack.asm'
CHAIN='Source/Station/Data/WindowFillChain.asm'
SAVED=('SavedPage','SavedBCAlt','SavedDEAlt','SavedHLAlt','SavedAFAlt','SavedBC','SavedDE','SavedHL','SavedAF','SavedIY','SavedIX')
STACK_FIELDS=tuple(f'Scratch{i:02d}' for i in range(13))+SAVED
CHAIN_FIELDS=('InterruptPC',)+tuple(f'Row{i}' for i in range(1,8))+('AfterGroup','TailWord')


def record(module,label,structure,origin,values,fields,document):
    lines=['                module '+module,'; Документация ['+document+'](../../../Docs/'+document+'.md)',
           f'                assert $ == #{origin:04X}',(label+':').ljust(16)+structure+' {']
    for i,(value,field) in enumerate(zip(values,fields)):
        lines.append(('                    '+value+(',' if i<len(fields)-1 else '')).ljust(80)+'; '+structure+'.'+field)
    lines+=['                }','                endmodule']
    return '\n'.join(lines)+'\n'


def render(source,names):
    outputs={};symbols={}
    fields=('MidHigh','High','MidLow','Low')
    outputs[COUNTER]=record('StationTimer','Counter','FStationBcdCounter',0x983B,
                           [f'#{v:02X}' for v in source[0x383B:0x383F]],fields,'StationInterrupt')
    symbols['StationTimer.Counter']=0x983B
    symbols.update({'StationTimer.Counter.'+field:0x983B+offset for offset,field in enumerate(fields)})
    words=[int.from_bytes(source[a:a+2],'little') for a in range(0x3C13,0x3C43,2)]
    assert words==[0]*24
    text=record('StationIrqData','Storage','FStationIrqStorage',0x9C13,[f'#{v:04X}' for v in words],STACK_FIELDS,'StationInterrupt')
    text=text.replace('                endmodule','StackTop:       assert $ == #9C43\n                endmodule')
    outputs[STACK]=text;symbols.update({'StationIrqData.Storage':0x9C13,'StationIrqData.StackTop':0x9C43})
    values=['#0000']+['@'+names['Station',a] for a in range(0xA0A6,0xA0B6,2)]+['#A0B6']
    assert source[0x4102:0x4116]==b'\x00\x00'+b''.join(a.to_bytes(2,'little') for a in range(0xA0A6,0xA0B8,2))
    outputs[CHAIN]=record('WindowFillChain','State','FWindowReturnChain',0xA102,values,CHAIN_FIELDS,'WindowGraphics')
    symbols['WindowFillChain.State']=0xA102
    return outputs,symbols
