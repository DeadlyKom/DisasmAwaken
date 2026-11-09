"""Разделение числовых совпадений CONTROL, HELP, ACTION и интро без сборки."""
import hashlib,json,re
from CheckIntro import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    def read(name):return json.loads((reports/(name+'.json')).read_bytes())
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    flow=read('ControlFlow');functions=read('Functions');entries={e['slot']:e for e in manifest['entries']}
    payloads={slot:(ROOT/(e['path']+'.bin')).read_bytes() for slot,e in entries.items()}
    template=payloads[23][:127];assert template[:6]==bytes.fromhex('DDE5ED73335E')
    assert template[0xDB01-0xDADE:0xDB03-0xDADE]==bytes(2)
    watched=(0xDADE,0xDB01,0xDB02,0x5E33,0x5E34,0xC600,0x6500)
    decoded=[]
    for region in flow:
        for item in region['instructions']:
            literals={int(x,16) for x in re.findall(r'#([0-9A-F]{4})\b',item['operation'])}
            if not literals.intersection(watched):continue
            owners=[f for f in functions if f['region']==region['name'] and f['slot']==item['slot']
                    and f['offset']<=item['offset']<f['end_offset']]
            decoded.append(dict(region=region['name'],slot=item['slot'],offset=item['offset'],
                address=item['address'],operation=item['operation'],
                path=owners[0]['path'] if len(owners)==1 else None,
                matching_literals=sorted(literals.intersection(watched))))
    # Проверка буквальных копий всего шаблона, совпадение само по себе не доказывает вызов.
    copies=[];pairs=[]
    for slot,data in payloads.items():
        begin=0
        while (offset:=data.find(template,begin))>=0:
            copies.append(dict(slot=slot,offset=offset));begin=offset+1
        for address in watched:
            needle=address.to_bytes(2,'little');begin=0;offsets=[]
            while (offset:=data.find(needle,begin))>=0:offsets.append(offset);begin=offset+1
            if offsets:pairs.append(dict(slot=slot,value=address,offsets=offsets,
                                         raw_pair_occurrence_is_not_pointer_or_instruction_proof=True))
    assert copies==[dict(slot=23,offset=0)]
    restore=next(f for f in functions if f['region']=='Action' and f['address']==0x6000)
    assert restore['path']=='Source/Action/QueueNumberBank1.asm'
    # Проверка ссылки HELP с тем же CPU-адресом, это другой банк и другой операнд.
    shared=next(i for i in decoded if i['region']=='Help' and i['address']==0xDB57)
    assert shared['operation']=='LD (#DB01),A' and shared['path']=='Source/Help/SelectText.asm'
    proof=read('ControlsTemporaryModuleVerification');assert proof['passed'] and proof['direct_switch_changes_next_opcode']
    result=dict(passed=True,method='original_payload_exact_template_and_decoded_literal_reference_audit',
        template_bytes=127,template_sha256=hashlib.sha256(template).hexdigest(),exact_original_payload_copies=copies,
        original_length_operand=0,decoded_references=decoded,raw_little_endian_pair_occurrences=pairs,
        same_numeric_help_write_is_not_control_length_writer=True,
        restored_unchanged_action_core_entry=restore['path'],restored_entry_address=0x6000,
        direct_bank_switch_next_opcode=proof['bank6_panel_opcode'],template_next_opcode=proof['stored_opcode'],
        dynamic_reference_graph_complete=False,legitimate_relocation_proved=False,nonzero_length_writer_proved=False,
        temporary_module_payload_and_real_caller_proved=False,semantic_contract_complete=False,
        assembly_executed=False,native_execution=False)
    target=reports/'ControlsTemporaryModuleReferenceAudit.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('decoded_references','raw_little_endian_pair_occurrences')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
