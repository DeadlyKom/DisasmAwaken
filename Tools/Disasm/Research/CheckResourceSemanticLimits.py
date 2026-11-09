"""Распознанный формат не означает доказанного игрового потребителя, эти границы считаются отдельно."""
import hashlib,json
from CheckIntro import ROOT
from AllocatedSectorSuffixResources import RANGES


def main():
    reports=ROOT/'Tools/Disasm/Reports';raw=(reports/'SourceMap.json').read_bytes();sm=json.loads(raw);groups=[]
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries']}
    from BankScreenStrips import verify_published
    verify_published(sources,sm)
    suffixes={path for slot,start,end,path,declared in RANGES}
    definitions=(('bank_screen_strips',lambda r:r['slot'] in range(33,39) and r['kind']=='typed_data' and not r['path'].endswith(('/PartialStripCopy.asm','/ArchiveRouteCopies.asm')),
      'заголовки и растры доказаны, внекаталожный загрузчик и рисователь проверены, вход из активной игры неизвестен','Docs/BankScreenStrips.md'),
      ('bank_partial_strip_copies',lambda r:r['path'].endswith('/PartialStripCopy.asm'),
       'точные заголовки и неполные копии растров установлены, штатные потребители неизвестны','Docs/BankScreenStrips.md'),
      ('bank_archive_route_copies',lambda r:r['path'].endswith('/ArchiveRouteCopies.asm'),
       'формат маршрутов установлен по исходному архивному рисователю, чтение копий внутри BANK неизвестно','Docs/BankArchiveRouteCopies.md'),
      ('bank_strip_staging_tails',lambda r:r.get('format')=='BANK_STRIP_STAGING_TAIL',
       'исходный LDIR читает хвосты за растром, их подмена не меняет вывод, вход из активной игры неизвестен','Docs/BankStripArchiveConsumer.md'),
      ('scene1_pixel_planes',lambda r:r['path']=='Source/Resources/30_scene1po/PixelPairs.bin',
       'геометрия, внекаталожный загрузчик и копирование окна проверены, вход из активной игры неизвестен','Docs/Scene1PixelPairs.md'),
      ('embedded_author_notes',lambda r:r['path']=='Source/Resources/17_ACTION/EmbeddedAuthorNotes.bin',
       'текстовый формат и происхождение доказаны, потребитель во время игры не установлен','Docs/ActionEmbeddedNotes.md'),
      ('allocated_sector_suffixes',lambda r:r['path'] in suffixes,
       'физические границы по каталогу доказаны, чтение, запись или неиспользуемость игрой не установлены','Docs/AllocatedSectorSuffixes.md'),
      ('news_and_order_records',lambda r:r['path'] in ('Source/Action/Data/NewsState.asm','Source/Action/Data/DeliveryOrders.asm'),
       'исходные блоки совпадают с описанием NEWS и ORDER, игровой доступ к отдельным полям не установлен','Docs/ActionNewsOrdersAndJumpCost.md'),
      ('station_detached_text',lambda r:r['path'] in ('Source/Station/Resources/SubscriberSystemRows.bin','Source/Station/Resources/FuelAndDeliveryLabels.bin'),
       'границы и столбцы доказаны, F066 читает второй печататель, его штатный вызов и потребитель списка абонентов неизвестны','Docs/StationDetachedText.md'),
      ('object3d_tail_packets',lambda r:r['slot']==24 and 0x2469<=r['offset']<0x2954 and r['kind']=='typed_data',
       'семь пакетов разобраны по физическому формату, игровые потребители и имена не установлены','Docs/ActionModelTail.md'),
      ('object3d_tail_pointer_pairs',lambda r:r['path']=='Source/Action/Data/TailModelPointers.asm',
       'четырнадцать слов указывают на семь дополнительных пакетов, игровой потребитель неизвестен','Docs/ActionModelTail.md'),
      ('preview_root_samples',lambda r:r['path']=='Source/D3D/Data/PreviewRootSamples.asm',
       'числовая форма и исходные отличия проверены, штатный потребитель неизвестен','Docs/PreviewRootSamples.md'),
      ('action_extra_polygon_pairs',lambda r:r['path'].startswith('Source/Action/Data/PolygonExtraMasks/') or
       r.get('format')=='POLYGON_LITERAL_OR_OPERAND',
       'чтения AND и OR подтверждены для принудительных индексов 5..7, их штатный выбор не установлен','Docs/ActionPolygonExtraMaskPairs.md'),
      ('bd2_mask_pixel_tail',lambda r:r['path']=='Source/Resources/42_BD2/UnindexedMaskPixelPairs.bin',
       'проверены исходные пары маски и пикселей, геометрия и игровой потребитель не установлены','Docs/FighterAssets.md'),
      ('action_transferred_context',lambda r:r['path'] in ('Source/Action/Resources/InitialTransferredContextMiddle.bin',
        'Source/Action/Resources/InitialTransferredContextTail.bin','Source/Action/Data/ContextControlPairs.asm'),
       'установлено назначение переноса состояния, отдельные потребители ACTION ещё требуют подтверждения','Docs/ActionContextTail.md'),
      ('station_save_transfer_trailers',lambda r:r.get('format')=='INITIAL_STATION_SAVE_TRANSFER_TRAILER',
       'подтверждены сохранение и границы двух переносов, значение отдельных байтов остаётся открытым','Docs/SavedStateLayout.md'),
      ('station_order_compatible_slots',lambda r:r['path'].endswith('/OrderCompatibleSlots.asm'),
       'три записи совпадают с ORDER после переноса, потребитель и отдельные поля неизвестны','Docs/StationOrderCompatibleSlots.md'))
    covered=set()
    for name,predicate,limit,doc in definitions:
        rows=[r for r in sm if predicate(r)];assert rows
        for r in rows:
            key=r['slot'],r['offset'];assert key not in covered;covered.add(key)
            data=sources[r['slot']][r['offset']:r['offset']+r['length']]
            assert len(data)==r['length'] and hashlib.sha256(data).hexdigest()==r['sha256']
            if r['kind']=='binary_resource':assert (ROOT/r['path']).read_bytes()==data
        groups.append(dict(name=name,physical_bytes=sum(r['length'] for r in rows),ranges=len(rows),
            source_paths=[r['path'] for r in rows],limit=limit,document=doc,all_game_consumers_and_writers_proved=False))
    assert [g['physical_bytes'] for g in groups]==[89046,408,1200,528,18676,3729,2558,71,458,1259,28,256,175,720,252,203,336]
    result=dict(passed=True,method='explicit_separation_of_format_proof_and_game_use_proof',
        source_map_sha256=hashlib.sha256(raw).hexdigest(),groups=groups,
        classified_format_or_extent_bytes_with_unproved_game_use=sum(g['physical_bytes'] for g in groups),
        unclassified_bytes=sum(r['length'] for r in sm if r['kind']=='unclassified'),
        complete_unknown_resource_graph_proved=False,full_semantic_analysis_complete=False,assembly_executed=False,native_execution=False)
    (reports/'ResourceSemanticLimits.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2))


if __name__=='__main__':main()
