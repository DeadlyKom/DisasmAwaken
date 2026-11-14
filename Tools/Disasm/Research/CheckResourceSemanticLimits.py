"""Распознанный формат не означает доказанного игрового потребителя, эти границы считаются отдельно."""
import hashlib,json
import re
from CheckIntro import ROOT
from AllocatedSectorSuffixResources import RANGES


def model_name_provenance(sources):
    # Сверка имён по реальному авторскому исходнику и двум неизменённым наборам игровых байтов.
    from zipfile import ZipFile
    from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256
    from CheckActionArchivedObjectTable import read_table
    from CheckControlsArchivedHyperEffect import read_entry
    from ActionModelPhysicalData import model_name, model_path, AUTHORED_MODEL_NAMES
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(ARCHIVE) as archive:
        disk = archive.read('awk1.trd')
    _, text, _ = read_entry(disk, b'3DTABS  a')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    _, models, _ = read_entry(disk, b'OBJECT3DC')
    rows = read_table(text, labels)
    words = [target['address'] for row in rows for target in row['targets']]
    assert len(words) == 142
    assert b''.join(word.to_bytes(2, 'little') for word in words) == sources[17][0x3E00:0x3F1C]
    assert len(models) == 10580 and models == sources[24][:len(models)]
    author_names = {}
    for row in rows:
        for target in row['targets']:
            offset = target['address'] - 0xC000
            assert model_name(offset).replace('_', '').casefold() == target['symbol'].replace('_', '').casefold()
            assert target['address'] not in author_names or author_names[target['address']] == target['symbol']
            author_names[target['address']] = target['symbol']
    assert len(author_names) == len(AUTHORED_MODEL_NAMES) == 102
    tail = [row for row in rows if row['table_offset'] >= 256]
    expected = (('St16', 0xE469), ('St_pirat', 0xE51F), ('Prison', 0xE5C1),
                ('St_u1', 0xE66B), ('St_u2', 0xE7AB), ('St_scince', 0xE707), ('Gip_pl', 0xE859))
    assert len(tail) == len(expected)
    for row, (name, address) in zip(tail, expected):
        assert row['targets'] == [dict(symbol=name, address=address)] * 2
        assert model_name(address - 0xC000).casefold() == name.replace('_', '').casefold()
    return dict(archive_sha256=ARCHIVE_SHA256, source_member='awk1.trd',
        table_source='3DTABS.a', label_source='LABELS.a', matching_model_bytes=len(models),
        matching_pointer_words=len(words), named_tail_models=[dict(name=name, address=address,
            source_label='ActionModels.' + model_name(address - 0xC000), source_path=model_path(address - 0xC000))
            for name, address in expected],
        named_models=[dict(name=name, address=address, source_label='ActionModels.' + model_name(address - 0xC000),
            source_path=model_path(address - 0xC000)) for address, name in sorted(author_names.items())],
        current_game_callers_proved=False)


def subscriber_base_words(disk, entries, source_map):
    hits = []
    for match in re.finditer(b'\xE4\xE0', disk):
        offset = match.start()
        entry = next(row for row in entries if row['offset'] <= offset < row['offset'] + row['allocated_length'])
        slot = entry['slot']
        file_offset = offset - entry['offset']
        owner = next((row['path'] for row in source_map if row['slot'] == slot
                      and row['offset'] <= file_offset < row['offset'] + row['length']), None)
        hits.append(dict(slot=slot, file_offset=file_offset, source_path=owner))
    assert [(row['slot'], row['file_offset']) for row in hits] == [
        (0, 0x8A31), (3, 0x1BA0), (4, 0x8254), (4, 0x8268), (4, 0x8295),
        (7, 0x1160), (9, 0x7B63), (23, 0x0602), (35, 0x28FC), (35, 0x2AFD),
    ]
    assert hits[5]['source_path'] == 'Source/Map/SetupMapRasterWindow.asm'
    assert hits[7]['source_path'] == 'Source/Controls/UpdateGlyphIndicators.asm'
    return hits


def main():
    reports=ROOT/'Tools/Disasm/Reports';raw=(reports/'SourceMap.json').read_bytes();sm=json.loads(raw);groups=[]
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries']}
    model_names = model_name_provenance(sources)
    from BankScreenStrips import verify_published
    verify_published(sources,sm)
    from ClassifyControlsLegacyContextPrefix import compare_adjacent_header, verify_prefix
    verify_prefix(sources[23], sources[4])
    adjacent_control_header = compare_adjacent_header(sources[23], sources[4])
    basic_run=json.loads((reports/'AwakenBasicRunVerification.json').read_bytes())
    buffer_tail=basic_run['first_sector_tail']
    assert basic_run['passed'] and buffer_tail['file_offsets']==[0x7C,0x100]
    assert buffer_tail['overwritten_before_usr']==132 and buffer_tail['original_reads_until_usr']==0
    subscriber_words=subscriber_base_words((ROOT/'Tools/Disasm/Disk/original.trd').read_bytes(),manifest['entries'],sm)
    suffixes={path for slot,start,end,path,declared in RANGES}
    definitions=(('bank_screen_strips',lambda r:r['slot'] in range(33,39) and r['kind']=='typed_data' and not r['path'].endswith(('/PartialStripCopy.asm','/ArchiveRouteCopies.asm')),
      'заголовки и растры доказаны, внекаталожный загрузчик и рисователь проверены, вход из активной игры неизвестен','Docs/BankScreenStrips.md'),
      ('bank_partial_strip_copies',lambda r:r['path'].endswith('/PartialStripCopy.asm'),
       'точные заголовки и неполные копии растров установлены, штатные потребители неизвестны','Docs/BankScreenStrips.md'),
      ('bank_archive_route_copies',lambda r:r['path'].endswith('/ArchiveRouteCopies.asm'),
       'формат маршрутов установлен по исходному архивному рисователю, чтение копий внутри BANK неизвестно','Docs/BankArchiveRouteCopies.md'),
      ('bank_strip_staging_tails',lambda r:r.get('format')=='BANK_STRIP_STAGING_TAIL',
       'исходный LDIR читает хвосты за растром, их подмена не меняет вывод, вход из активной игры неизвестен','Docs/BankStripArchiveConsumer.md'),
      ('bank_archive_tile_copies',lambda r:r.get('format')=='BANK_ARCHIVE_TILE_LAYER_COPY',
       'исходный растровый слой и его чтения подтверждены, использование копий внутри BANK не установлено','Docs/BankArchiveTileLayers.md'),
      ('scene1_pixel_planes',lambda r:r['path']=='Source/Resources/30_scene1po/PixelPairs.bin',
       'исходное ПЗУ загрузило сцену, архивный вывод и восстановление из двух расширенных страниц сверены, вход из активной игры неизвестен','Docs/Scene1PixelPairs.md'),
      ('embedded_author_notes',lambda r:r['path']=='Source/Resources/17_ACTION/EmbeddedAuthorNotes.bin',
       'установлена токенизированная редакция 3DTABS.a и её отличия от архива, причина размещения и игровой потребитель неизвестны','Docs/ActionEmbeddedNotes.md'),
      ('allocated_sector_suffixes',lambda r:r['path'] in suffixes,
       'физические границы доказаны, загрузка HELP, D3D и LANG проверена, дальнейшие обращения к суффиксам остаются открытыми','Docs/AllocatedSectorSuffixes.md'),
      ('news_and_order_records',lambda r:r['path'] in ('Source/Action/Data/NewsState.asm','Source/Action/Data/DeliveryOrders.asm'),
       'исходные блоки совпадают с описанием NEWS и ORDER, игровой доступ к отдельным полям не установлен','Docs/ActionNewsOrdersAndJumpCost.md'),
      ('station_news_transfer',lambda r:r['path'].endswith('/NewsTransfer.asm'),
       'семь копий тела NEWS в STATIONF и SAVE, перенос в ACTION доказан, отдельные потребители полей неизвестны','Docs/StationNewsTransfer.md'),
      ('station_detached_text',lambda r:r['path'] in ('Source/Station/Resources/SubscriberSystemRows.bin','Source/Station/Resources/FuelAndDeliveryLabels.bin'),
       'границы и столбцы доказаны, F066 читает второй печататель, его штатный вызов и потребитель списка абонентов неизвестны','Docs/StationDetachedText.md'),
      ('object3d_tail_packets',lambda r:r['slot']==24 and 0x2469<=r['offset']<0x2954 and r['kind']=='typed_data',
       'семь пакетов разобраны по физическому формату, авторские имена подтверждены совпадением OBJECT3D и таблицы указателей, штатные игровые потребители не установлены','Docs/ActionModelTail.md'),
      ('object3d_tail_pointer_pairs',lambda r:r['path']=='Source/Action/Data/TailModelPointers.asm',
       'четырнадцать слов указывают на семь дополнительных пакетов, игровой потребитель неизвестен','Docs/ActionModelTail.md'),
      ('preview_root_samples',lambda r:r['path']=='Source/D3D/Data/PreviewRootSamples.asm',
       'числовая форма и исходные отличия проверены, штатный потребитель неизвестен','Docs/PreviewRootSamples.md'),
      ('action_extra_polygon_pairs',lambda r:r['path'].startswith('Source/Action/Data/PolygonExtraMasks/') or
       r.get('format')=='POLYGON_LITERAL_OR_OPERAND',
       'чтения AND и OR подтверждены для принудительных индексов 5..7, их штатный выбор не установлен','Docs/ActionPolygonExtraMaskPairs.md'),
      ('bd2_mask_pixel_tail',lambda r:r['path']=='Source/Resources/42_BD2/UnindexedMaskPixelPairs.bin',
       'проверены исходные пары маски и пикселей, геометрия и игровой потребитель не установлены','Docs/FighterAssets.md'),
      ('action_transferred_context',lambda r:r['path'] in ('Source/Action/Data/ContextMapAndOptions.asm',
        'Source/Action/Resources/InitialTransferredContextTail.bin','Source/Action/Data/ContextControlPairs.asm'),
       'установлено назначение переноса состояния, отдельные потребители ACTION ещё требуют подтверждения','Docs/ActionContextTail.md'),
      ('action_transferred_player_fields',lambda r:r['path'] in ('Source/Action/Data/PlayerIndices.asm',
        'Source/Action/Data/PlayerMoney.asm'),
       'установлены поля станции и их перенос, самостоятельные потребители ACTION неизвестны','Docs/ActionTransferredPlayerFields.md'),
      ('station_save_transfer_trailers',lambda r:r.get('format')=='INITIAL_STATION_SAVE_TRANSFER_TRAILER',
       'подтверждены сохранение и границы двух переносов, значение отдельных байтов остаётся открытым','Docs/SavedStateLayout.md'),
      ('station_order_compatible_slots',lambda r:r['path'].endswith('/OrderCompatibleSlots.asm'),
       'три записи совпадают с ORDER после переноса, потребитель и отдельные поля неизвестны','Docs/StationOrderCompatibleSlots.md'),
      ('control_legacy_context_prefix',lambda r:r.get('format')=='CONTROL_LEGACY_CONTEXT_PREFIX',
       'совпадают физические байты двух частей префикса STATIONF, потребитель CONTROL и его рабочая разметка неизвестны','Docs/ControlsTemporaryModule.md'),
      ('control_archived_reset_context_tail',lambda r:r.get('format')=='CONTROL_LEGACY_RESET_CONTEXT_TAIL',
       '109 байтов совпадают с шаблоном NDATA архивного CONTROL, читатель в Awakenv02 не установлен','Docs/ControlsTemporaryModule.md'),
      ('control_archived_reset_revised_header',lambda r:r.get('format')=='CONTROL_LEGACY_RESET_REVISED_HEADER',
       'восемь байтов лежат в изменённом заголовке NDATA, назначение полей и потребитель Awakenv02 не установлены','Docs/ControlsTemporaryModule.md'),
      ('voxel_teleport_resource_tail',lambda r:r.get('format')=='VOXEL_TELEPORT_RESOURCE_TAIL',
       'исходный хвост HIPERJMP.van, два полных цикла эффектов его не читают, другие обращения не исключены','Docs/VoxelPhysicalResources.md'),
      ('d3d_authored_reserves',lambda r:r.get('format')=='D3D_AUTHORED_RESERVE',
       'авторские резервы рабочих страниц и записей объектов, обращения за пределами проверенных кадров открыты','Docs/PreviewRenderWorkspace.md'),
      ('object3d_authored_target_tail',lambda r:r.get('format')=='OBJECT3D_AUTHORED_TARGET_TAIL',
       'хвост исходного TARGET после двух ограничителей, отдельное чтение не установлено','Docs/ActionModelPackets.md'),
      ('control0_authored_dot_buffer_tail',lambda r:r.get('format')=='CONTROL0_AUTHORED_DOT_BUFFER_TAIL',
       'часть исходного DOTB после 35 известных пар, отдельное чтение не установлено','Docs/ControlsBufferPoints.md'),
      ('control0_authored_star_workspace',lambda r:r.get('format') in ('CONTROL0_AUTHORED_TXTR_PAIR','CONTROL0_AUTHORED_SMALL_MASK_TAIL'),
       'TXTR и резерв LA8FA объявлены в STARHSUN, обращения к двум парам и хвосту при штатных радиусах не установлены','Docs/ControlsSmallMasks.md'),
      ('action_authored_object_buffer_tail',lambda r:r.get('format')=='ACTION_AUTHORED_OBJECT_BUFFER_TAIL',
       'хвост OBJBUF с исходной границей из 3DTABS, условные обращения по нечётным индексам проверены отдельно','Docs/ActionObjectStreamStorage.md'),
      ('action_authored_render_page_tails',lambda r:r.get('format')=='ACTION_AUTHORED_RENDER_PAGE_TAIL',
       'исходные резервы L9C и L9D за доказанными записями, чтения за штатными пределами не установлены','Docs/ActionInitialStorage.md'),
      ('action_authored_eye_state',lambda r:r['path']=='Source/Action/Data/ArchivedEyeState.asm',
       'ширина и адреса EYE и STP совпадают с исходным 3DTABS, потребители не установлены','Docs/ActionInputContextData.md'),
      ('action_authored_spawn_chances',lambda r:r['path']=='Source/Action/Data/ArchivedSpawnChances.asm',
       'хвост PLANDICTAT и поля WERPO доказаны по исходному 3DTABS, потребители не установлены','Docs/ActionQueueParameterPhysicalData.md'),
      ('lang_authored_assignment_buffer_tail',lambda r:r.get('format')=='LANG_AUTHORED_ASSIGNMENT_BUFFER_TAIL',
       'хвост ARGD, чтения и записи доказаны при вложении от семи уровней, штатный путь с такой глубиной не установлен','Docs/ExpressionStack.md'),
      ('station_authored_job_list',lambda r:r['path']=='Source/Station/Data/ArchivedJobList.asm',
       'десять записей JLIST с полями из DATA_M и BLOCK2, отдельный потребитель в Awakenv02 не установлен','Docs/StationArchivedJobs.md'),
      ('station_authored_market_tables',lambda r:r['path'] in ('Source/Station/Data/MarketCategories.asm','Source/Station/Data/MarketRules.asm'),
       'исходные категории и правила совпадают с DATA_M, генератор пропускает три последние категории и отдельный нулевой байт','Docs/MarketGeneration.md'),
      ('detached_basic_number',lambda r:r['path']=='Source/Basic/Data/DetachedSectorNumber.asm',
       'равенство печатного и двоичного целого доказано, исходная команда и потребитель неизвестны','Docs/BasicProgram.md'),
      ('object_stream_extended_tail',lambda r:r.get('format')=='INITIAL_OBJECT_STREAM_EXTENDED_TAIL',
       'запись и чтение хвоста подтверждены с дополнительным пакетом E859, штатный путь его выбора не установлен','Docs/ActionObjectStreamStorage.md'),
      ('detached_spawn_model_pairs',lambda r:r['path']=='Source/Action/Data/DetachedSpawnModelChoices.asm',
       'запись полей подтверждена при подстановке указателя, выбор строки из активной игры не установлен','Docs/ActionSpawnPhysicalRows.md'),
      ('station_script_fields',lambda r:r['path']=='Source/Station/Data/ScriptFields.asm',
       'проверены байтовые режимы и поиск разделителей, игровые значения записей остаются открытыми','Docs/StationScriptFields.md'),
      ('detached_basic_line_suffix',lambda r:r['path']=='Source/Basic/Data/DetachedLineSuffix.asm',
       'токен LINE и цифры 20 подтверждены, начало команды и назначение соседнего байта неизвестны','Docs/BasicProgram.md'),
      ('basic_first_sector_buffer_tail',lambda r:r.get('format')=='BASIC_FIRST_SECTOR_BUFFER_TAIL',
       'при RUN хвост записан в буфер и вытеснен до входа USR, происхождение исходных байтов неизвестно','Docs/BasicProgram.md'),
      ('station_conditional_rebuild_shift_tail',lambda r:r.get('format')=='INITIAL_STATION_CONDITIONAL_REBUILD_SHIFT_TAIL',
       'физические обращения установлены для списка из 47..63 исходных указателей с повторами, штатная достижимость неизвестна','Docs/RebuildInterface.md'),
      ('action_noise_irq_aliases',lambda r:r.get('format')=='INITIAL_ACTION_NOISE_IRQ_ALIAS',
       'ROM читает и пишет эти байты банка 0 при смещённом IY, подтверждение всех сочетаний в нативной игре отсутствует','Docs/ActionNoiseExit.md'),
      ('action_archived_body_and_speed',lambda r:r.get('format') in ('ACTION_LEGACY_BODY_INDEX_LOAD','ACTION_ARCHIVED_SKIMMER_SPEED'),
       'подтверждены остаток архивного LD A,E и второй байт пары SPEED, штатное исполнение и потребитель текущего поля неизвестны','Docs/ActionArchivedBodyContext.md'),
      ('action_archived_player_panel',lambda r:r['path'] in ('Source/Action/Data/PlayerPanelWord.asm','Source/Action/Data/PlayerPanelType.asm'),
       'байты подтверждены объявлением PLAYER, читатели TypeCode в цепочке ракетного попадания установлены, слово после ACTION и два соседних байта остаются открытыми','Docs/ActionPanelPhysicalData.md'),
      ('intro_stack_sample_bytes',lambda r:r['path'] in ('Source/Intro/Data/StackSampleBefore.asm','Source/Intro/Data/StackSampleAfter.asm'),
       'физическая выборка и перезапись копии подтверждены, исходное назначение соседних нулей неизвестно','Docs/IntroStationTransition.md'),
      ('station_legacy_mission_return_pair',lambda r:r.get('format')=='STATION_LEGACY_MISSION_RETURN_PAIR',
       'два RET соответствуют раскладке WMISS2 перед пустым наведением, штатный вход в текущей версии не установлен','Docs/PassivePanelHovers.md'),
      ('station_conditional_popup_shift_tail',lambda r:r.get('format')=='INITIAL_STATION_CONDITIONAL_POPUP_SHIFT_TAIL',
       'чтение подтверждено при удалении последнего из 64 исходных указателей с повторами, штатная достижимость неизвестна','Docs/PopupItems.md'),
      ('action_object_table_alignment',lambda r:r.get('format')=='ACTION_OBJECT_TABLE_ALIGNMENT',
       'выравнивание подтверждено макросом ADRXX00 и тремя машинными версиями, косвенные обращения в игре остаются открытыми','Docs/ActionObjectPointers.md'))
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
    assert [g['physical_bytes'] for g in groups]==[89046,408,1200,528,1524,18676,3729,2558,71,42,458,1259,28,256,175,720,252,4,203,336,13,109,8,832,305,4,186,24,5,60,9,10,10,160,91,12,13,16,29,9,112,34,41,2,5,2,2,2,67]
    result=dict(passed=True,method='explicit_separation_of_format_proof_and_game_use_proof',
        source_map_sha256=hashlib.sha256(raw).hexdigest(),groups=groups,
        classified_format_or_extent_bytes_with_unproved_game_use=sum(g['physical_bytes'] for g in groups),
        unclassified_bytes=sum(r['length'] for r in sm if r['kind']=='unclassified'),
        adjacent_control_header=adjacent_control_header,
        model_name_provenance=model_names,
        subscriber_base_literal_matches=subscriber_words,
        complete_unknown_resource_graph_proved=False,full_semantic_analysis_complete=False,assembly_executed=False,native_execution=False)
    (reports/'ResourceSemanticLimits.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2))


if __name__=='__main__':main()
