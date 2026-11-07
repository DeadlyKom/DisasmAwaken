"""Текущая сводка после новых состояний, пользовательская сборка отделена от новых исходников."""
import argparse,hashlib,json,os,re,tempfile
from pathlib import Path
from CheckIntro import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='ActionStateProgress');args=parser.parse_args()
    assert re.fullmatch('[A-Za-z][A-Za-z0-9]*',args.tag)
    reports=ROOT/'Tools/Disasm/Reports'
    def read(stem):return json.loads((reports/(stem+'.json')).read_text('utf-8'))
    inventory=read('Inventory');labels=read('SourceLabelsVerification');placement=read('FilePlacementVerification')
    audit=read('ConformanceAudit');coverage=read('ObjectStateCoverage');mutation=read('ModifiedCodePathsVerification')
    assert inventory['fragments']==audit['registered_functions'] and labels['passed'] and placement['passed'] and mutation['passed']
    image=(ROOT/'Awakenv02.trd').read_bytes();original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert image==original and len(image)==655360
    assert read('BuildVerification')['byte_identical'] is True
    capsule=(f"Текущий срез содержит {inventory['fragments']} фрагментов. Описаны {inventory['described']}, остаются 2 Unknown и 1 недоказанный контракт именованного RunTemporaryModule. "
        f"Обе записи Unknown относятся к CF08 в Action и ThreeD, их табличная роль и условный эффект инструкций установлены, игровой вход неизвестен. "
        f"Неразмеченные физические диапазоны занимают {inventory['physical_bytes_by_kind']['unclassified']} байтов. "
        f"Статически сверены {inventory['instructions']} инструкций, {labels['labels_checked']} кодовых меток, {placement['ranges_checked']} диапазонов и {placement['physical_assertions_checked']} утверждения размещения. "
        "Пользователь подтвердил сборку 196226 строк за 2,468 с, 0 ошибок и 0 предупреждений, побайтовое совпадение всех 655360 байтов TRD. "
        "Эта сборка выполнена до последующих изменений исходников, новые изменения проверены статически и моделями без запуска сборки. Нативный запуск нового среза не подтверждён.")
    pending={}
    for filename in ('README.md','Docs/Validation.md','Docs/ConformancePlan.md'):
        path=ROOT/filename;text=path.read_text('utf-8')
        matches=list(re.finditer(r'^Текущий срез содержит [^\n]*',text,re.M));assert matches
        match=matches[-1];text=text[:match.start()]+capsule+text[match.end():]
        pattern=r'В исходной таблице из 22 состояний теперь отдельно оформлены (?:шесть|\d+) целей, \d+ остаются в сырых блоках\.'
        new=f"В исходной таблице из 22 состояний теперь отдельно оформлены {coverage['registered_entries']} целей, {coverage['unregistered_entries']} остаются в сырых блоках."
        text,count=re.subn(pattern,new,text);assert count==1
        prefix='Docs/' if filename=='README.md' else ''
        if '[Фазовые переходы](' not in text:
            text+='\n[Фазовые переходы]('+prefix+'ActionPhaseTransition.md), [выбор ближайшего кандидата]('+prefix+'ActionNearestCandidate.md) и [допуск связи]('+prefix+'ActionTargetTransition.md) разобраны по реальным байтам. '
            text+='Оформлены [State03 и State0F]('+prefix+'ActionNearPhase.md), [State07]('+prefix+'ActionTimedDecayState.md), [State00]('+prefix+'ActionIdleState.md) и [State04]('+prefix+'ActionFastPhaseState.md). '
            text+='Модели различают возврат старого индекса, последовательные состояния 13 и 14, оборачивание счётчиков и разные источники фаз. '
            text+='Все 26 элементов таблицы классов связаны с 11 отдельными процедурами, игровые названия всех классов пока не доказаны.\n'
        if '[State11](' not in text:
            text+='\nДополнительно разобраны [State11]('+prefix+'ActionTimedPhaseState.md), [State12]('+prefix+'ActionAcquireLocalState.md), [State0B]('+prefix+'ActionPeriodicClass3State.md), '
            text+='[создание класса 9]('+prefix+'ActionChildSpawn.md) и [загрузка связанных векторов]('+prefix+'ActionLinkedVectors.md). '
            text+='Проверены общий период вызовов, неуравновешенный EXX при отказе поиска, сохранение бита запроса и полные возвраты через вычислитель смещений.\n'
        if '[State0E](' not in text:
            text+='\nОформлены [State0E]('+prefix+'ActionLinkedProximity.md) и [общий повторный выбор класса]('+prefix+'ActionClassRefresh.md). '
            text+='Модель различает исходный бит 4 и перезаписанный ReuseByte, самовыбор записи, дальний подвод и границу входа в большой эффект. '
            text+='Тело большого эффекта этой моделью не исполняется, точный R дальнего вычислителя остаётся недоказанным.\n'
        if '[State06](' not in text:
            text+='\n[State06]('+prefix+'ActionSmallEffectState.md) проверен до полного возврата через настоящий малый эффект банка 3. '
            text+='Сверены режим из заголовка OBJECT3D, отказ выделения, переход к State07, точные регистры и R, все банки и четыре переключения 7FFD.\n'
        if '[State0A](' not in text:
            text+='\n[State0A]('+prefix+'ActionClass17Sweep.md) проверен до полного возврата с максимум тремя настоящими большими эффектами, подсчётом связей класса 3 и непосредственной поправкой. '
            text+='Для большого эффекта отдельно сверены все полные классы 16..255 с точными регистрами и R, эта проверка не распространяется на ветвь создания игровых детей классов ниже 16.\n'
        if '[State01](' not in text:
            text+='\n[State01]('+prefix+'ActionWideVectorState.md) проверен с точным R геометрии, всеми индексами широкого вектора и случайными переходами. '
            text+='[State10]('+prefix+'ActionTimedLinkedState.md) проверен с полным созданием либо XOR-выводом до общего F0F8. '
            text+='Разобраны [связанный экранный помощник]('+prefix+'ActionLinkedOverlay.md), [общий создатель класса 17]('+prefix+'ActionClass17Spawn.md) '
            text+='и [шаг третьей фазы]('+prefix+'ActionRandomPhaseStep.md). R растеризатора остаётся за пределами этих доказательств.\n'
        if '[State02](' not in text:
            text+='\n[State02]('+prefix+'ActionLinkedTargetState.md), [State05]('+prefix+'ActionLinkedPhaseState.md) и [State08]('+prefix+'ActionArrivalState.md) оформлены по исходным инструкциям. '
            text+='Все 22 цели таблицы состояний зарегистрированы, но полный игровой граф, неизвестные поля и данные ещё не разобраны. '
            text+='Для большого эффекта доказана также ветвь создания игровых детей классов 0..15 с точным R и синтетической ROM. '
            text+='Неограниченный экранный профиль индексов за массивом имеет сохранённое расхождение числового эталона, это не доказательство ошибки оригинальной игры.\n'
        text=text.replace('Тело большого эффекта этой моделью не исполняется, точный R дальнего вычислителя остаётся недоказанным.',
                          'Тело большого эффекта этой моделью не исполняется. Точный R дальнего подвода дополнительно проверен во всех 106496 сценариях State0E.')
        text=text.replace('Неограниченный экранный профиль индексов за массивом имеет сохранённое расхождение числового эталона, это не доказательство ошибки оригинальной игры.',
                          'Прежнее расхождение экранного профиля за массивом устранено в модели после установления записи обратной ссылки поверх JR NZ по C94B. Дополнительные 44656 профилей State02 и 44032 State05 прошли без принудительного маркера отказа, произвольные изменения кода и штатная игровая достижимость этих индексов не доказаны.')
        if '[Создание класса 20](' not in text:
            text+='\n[Создание класса 20]('+prefix+'ActionClass20Spawn.md) выделено из 132 исходных байтов и проверено в 66560 сценариях с настоящими поиском, случайным потоком и матричным преобразованием. '
            text+='Сохранено создание записи после переполнения преобразования, точные регистры, R, все банки и кратность записей. '
            text+='[Начальное содержимое рабочих областей]('+prefix+'ActionInitialStorage.md) отделено от неизвестных диапазонов на основании реальных очистки, генераторов и потребителей, исходные байты не заменены генерируемыми.\n'
        if '[Случайный допуск класса](' not in text:
            text+='\n[Случайный допуск класса]('+prefix+'ActionRandomClassGate.md) проверен в 65536 сценариях с настоящими обработчиками. '
            text+='Точный R дополнительно закрыт для подвода выбранной записи и State0C/0D/0E в пределах описанных профилей. '
            text+='[Встроенные заметки о данных]('+prefix+'ActionEmbeddedNotes.md) расшифрованы отдельно, их имена не перенесены автоматически на поля текущей версии.\n'
        pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8')
    text,count=re.subn(r'сверяет \d+ записей','сверяет '+str(mutation['records_checked'])+' записей',text);assert count==1
    text,count=re.subn(r'и \d+ целей с','и '+str(mutation['physical_target_ranges_checked'])+' целей с',text);assert count==1
    pending[path]=text.encode('utf-8')
    checkpoint=read('InteractionCheckpoint');build=read('BuildVerification')
    checkpoint['last_user_confirmed_build'].update(compiled_lines=196226,work_seconds=2.468,errors=0,warnings=0,
        full_image_byte_identical=True,size=655360,checked_at_utc=build['checked_at_utc'],
        source_changes_after_build=True,codex_assembler_executed=False,user_reported_byte_identity_line=True,
        observation='Пользователь сообщил успешную сборку 196226 строк и побайтовое совпадение до новых изменений текущего продолжения')
    checkpoint['manual_build_check'].update(status='passed_before_latest_source_changes',
        sha256=hashlib.sha256(image).hexdigest(),checked_at_utc=build['checked_at_utc'],
        source_changes_after_build=True,current_source_assembly_verified=False)
    checkpoint['last_verified_build_artifact'].update(checked_at_utc=build['checked_at_utc'],sha256=hashlib.sha256(image).hexdigest(),source_changes_after_build=True)
    pending[reports/'InteractionCheckpoint.json']=(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+args.tag)
    history=ROOT/('Tools/Disasm/Research/History/Before'+args.tag)
    assert not candidate.exists() and not history.exists()
    plan=[(path,path.read_bytes(),after) for path,after in pending.items()]
    # Подготовка отдельного кандидата и проверка всех исходных оснований перед публикацией сводки.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='progress-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(after)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(after)
    print(json.dumps(dict(passed=True,fragments=inventory['fragments'],registered_states=coverage['registered_entries'],
        user_build_lines=196226,new_sources_assembly_verified=False,assembly_executed=False),indent=2))


if __name__=='__main__':main()
