"""Проверяемое восстановление одного старого исследовательского снимка, обычной сборке не требуется."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[3]
ARCHIVE_REL='Tools/Disasm/Research/Archives/LegacySnapshots-20261031.zip'


def restore_snapshot(project,target):
 project=Path(project).resolve();target=Path(target).resolve();research=project/'Tools/Disasm/Research'
 if not any(target.is_relative_to(research/folder) and target!=research/folder for folder in ('Candidates','History')):raise ValueError('Снимок должен находиться внутри Candidates либо History')
 marker=target/'ARCHIVED.json'
 if not marker.is_file():return target
 info=json.loads(marker.read_text('utf-8'));archive=(project/info['archive']).resolve()
 if not archive.is_relative_to(research/'Archives'):raise ValueError('Архив вне каталога исследовательских архивов')
 with zipfile.ZipFile(archive) as z:
  index=json.loads(z.read('index.json'));prefix=target.relative_to(project).as_posix()+'/'
  records=[v for v in index['files'] if v['path'].startswith(prefix)]
  if not records:raise ValueError('Снимок отсутствует в реестре архива')
  # Проверка всех путей, контрольных сумм и существующих ручных файлов до восстановления первого файла.
  for item in records:
   dst=(project/item['path']).resolve()
   if not dst.is_relative_to(target):raise ValueError('Недопустимый путь снимка')
   data=z.read('objects/'+item['sha256'])
   if len(data)!=item['size'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Повреждён архивный объект')
   if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Существующий файл отличается, ручные изменения сохранены, '+item['path'])
  for item in records:
   dst=project/item['path']
   if not dst.exists():
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read('objects/'+item['sha256']));os.utime(dst,ns=(item['mtime_ns'],item['mtime_ns']))
 return target


def main():
 parser=argparse.ArgumentParser(description='Восстановить один архивный снимок без перезаписи изменённых файлов')
 parser.add_argument('snapshot',help='Например History/BeforeStoredPointProceduresSplit либо Candidates/GlyphRelease2')
 args=parser.parse_args();target=ROOT/'Tools/Disasm/Research'/args.snapshot
 restore_snapshot(ROOT,target);print(target.relative_to(ROOT).as_posix())


if __name__=='__main__':main()
