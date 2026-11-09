"""Проверка именованных соседних правил рынка и отклонения неверного размера смещения."""
import contextlib,io,json,sys
from pathlib import Path
from unittest.mock import patch
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
import VerifySources


def main():
    target=ROOT/'Source/Station/GenerateMarket.asm';before=target.read_bytes()
    text=before.decode('utf-8');needle='2 * @FMarketRule + @FMarketRule.BasePrice'
    assert text.count(needle)==1 and text.count('IX + @FMarketRule + @FMarketRule.BasePrice')==1
    # Проверка настоящего положительного текста всех исходников до отрицательного опыта.
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    report_path=ROOT/'Tools/Disasm/Reports/SourceVerification.json';report_before=report_path.read_bytes()
    read_text=Path.read_text

    def altered(path,*args,**kwargs):
        result=read_text(path,*args,**kwargs)
        if path.resolve()==target.resolve():result=result.replace(needle,'3 * @FMarketRule + @FMarketRule.BasePrice')
        return result

    # Подмена только прочитанного текста в памяти, пользовательский исходник не записывается.
    rejected=False
    with patch.object(Path,'read_text',altered),contextlib.redirect_stdout(io.StringIO()):
        try:VerifySources.main()
        except ValueError as error:
            assert 'Текст инструкций отличается' in str(error) and 'Source/Station/GenerateMarket.asm' in str(error)
            rejected=True
    assert rejected and target.read_bytes()==before and report_path.read_bytes()==report_before
    result=dict(passed=True,first_rule_index=27,subsequent_rule_indices=[28,29],
        physical_rule_size=2,base_price_field_offset=0,original_displacements=[2,4],
        actual_source_full_verification_passed=True,wrong_multiplier_probe_rejected=True,
        probe_changed_source_file=False,failed_probe_changed_verification_report=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/MarketRuleOffsetsVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
