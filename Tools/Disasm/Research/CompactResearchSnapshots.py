"""Удаление распакованных устаревших снимков только после побайтовой проверки их архива."""
from pathlib import Path
import hashlib,json,os,subprocess,time,zipfile
ROOT=Path(__file__).resolve().parents[3]
RESEARCH=ROOT/'Tools/Disasm/Research'
ARCHIVE=RESEARCH/'Archives/LegacySnapshots-20261031.zip'
KEEP={'EventActionCodeScoped','AnimatedVariantCodeScoped','PeriodicVariantCodeScoped'}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def active_hashes():
 result={}
 for base,dirs,files in os.walk(ROOT,followlinks=False):
  parent=Path(base);rel=parent.relative_to(ROOT).as_posix()
  dirs[:]=[name for name in dirs if name!='.git' and not (parent/name).is_symlink() and (parent/name) not in (RESEARCH/'Candidates',RESEARCH/'History',RESEARCH/'Archives')]
  for name in files:
   p=parent/name
   if p==ROOT/'Tools/Disasm/Reports/ResearchCleanupVerification.json':continue
   result[p.relative_to(ROOT).as_posix()]=digest(p)
 for name in KEEP:
  candidate=RESEARCH/'Candidates'/name
  for path in candidate.rglob('*'):
   if path.is_file():result[path.relative_to(ROOT).as_posix()]=digest(path)
 return result


def main():
 if ARCHIVE.exists() or ARCHIVE.with_suffix('.partial').exists():raise ValueError('Архив этой очистки уже существует, повторное применение запрещено')
 tracked=subprocess.run(['git','ls-files','-z','--','Tools/Disasm/Research/Candidates','Tools/Disasm/Research/History'],cwd=ROOT,capture_output=True,check=True).stdout
 if tracked:raise ValueError('Снимки содержат пользовательские отслеживаемые Git-файлы, очистка остановлена')
 roots=[p.resolve() for parent in ('Candidates','History') for p in (RESEARCH/parent).iterdir() if p.is_dir() and not (parent=='Candidates' and p.name in KEEP)]
 # Проверка конечных абсолютных корней удаления, каждый обязан оставаться строго внутри разрешённого каталога проекта.
 for root in roots:
  if not any(root.is_relative_to(RESEARCH/folder) and root!=RESEARCH/folder for folder in ('Candidates','History')):raise ValueError('Недопустимый корень удаления')
  if root.is_symlink():raise ValueError('Ссылка вместо каталога снимка')
 files=[]
 for root in roots:
  if (root/'ARCHIVED.json').exists():raise ValueError('Снимок уже архивирован')
 for root in roots:
  for base,dirs,names in os.walk(root,followlinks=False):
   for name in dirs+names:
    p=Path(base)/name
    if p.is_symlink() or not p.resolve().is_relative_to(root) or getattr(p.stat(),'st_file_attributes',0)&0x400:raise ValueError('Ссылка или точка повторного анализа в снимке')
   files.extend(Path(base)/name for name in names)
 print('Проверены границы, старых снимков',len(roots),'файлов',len(files),flush=True)
 before=active_hashes();ARCHIVE.parent.mkdir(exist_ok=True);temporary=ARCHIVE.with_suffix('.partial');entries=[];seen=set();original_bytes=unique_bytes=0
 with zipfile.ZipFile(temporary,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for i,path in enumerate(files):
   data=path.read_bytes();sha=hashlib.sha256(data).hexdigest();st=path.stat();entries.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha,size=len(data),mtime_ns=st.st_mtime_ns));original_bytes+=len(data)
   if sha not in seen:z.writestr('objects/'+sha,data);seen.add(sha);unique_bytes+=len(data)
   if (i+1)%15000==0:print('Архивировано файлов',i+1,flush=True)
  index=dict(format=1,snapshots=[p.relative_to(ROOT).as_posix() for p in roots],files=entries)
  z.writestr('index.json',json.dumps(index,ensure_ascii=False,separators=(',',':')))
 # Побайтовая проверка каждого уникального объекта и полного реестра до удаления любых исходных снимков.
 with zipfile.ZipFile(temporary) as z:
  if json.loads(z.read('index.json'))!=index:raise ValueError('Реестр не совпал после записи')
  expected_sizes={v['sha256']:v['size'] for v in entries}
  for sha in seen:
   data=z.read('objects/'+sha)
   if len(data)!=expected_sizes[sha] or hashlib.sha256(data).hexdigest()!=sha:raise ValueError('Не прошла проверка архивного объекта')
 if active_hashes()!=before:raise ValueError('Рабочие файлы изменились во время подготовки, удаление не начато')
 # Проверка прежнего содержимого каждого удаляемого файла защищает новые ручные изменения в старом снимке.
 for item,path in zip(entries,files):
  if digest(path)!=item['sha256']:raise ValueError('Снимок изменился, удаление не начато')
 temporary.rename(ARCHIVE);print('Архив проверен, удаление распакованных копий',flush=True)
 archive_relative=ARCHIVE.relative_to(ROOT).as_posix()
 for root in roots:
  (root/'ARCHIVED.json').write_text(json.dumps(dict(archive=archive_relative,snapshot=root.relative_to(ROOT).as_posix(),restoration='Tools/Disasm/Research/ResearchArchive.py',consumed_snapshot_directory_preserved=True),ensure_ascii=False,indent=2)+'\n','utf-8')
 # Удаление только проверенных файлов по Literal Path через pathlib, без рекурсивного удаления вычисленного каталога.
 for i,path in enumerate(files):
  if path.name=='ARCHIVED.json':raise ValueError('Входной архивный маркер неожиданно существовал')
  path.unlink()
  if (i+1)%20000==0:print('Удалено распакованных файлов',i+1,flush=True)
 for root in roots:
  for base,dirs,names in os.walk(root,topdown=False,followlinks=False):
   p=Path(base)
   if p!=root and not any(p.iterdir()):p.rmdir()
 after=active_hashes()
 if after!=before:raise ValueError('Контроль рабочих файлов после очистки не совпал')
 report=dict(passed=True,archived_snapshots=len(roots),removed_expanded_files=len(files),archived_logical_bytes=original_bytes,unique_content_objects=len(seen),unique_content_bytes=unique_bytes,archive_bytes=ARCHIVE.stat().st_size,archive=archive_relative,archive_sha256=digest(ARCHIVE),retained_candidates=sorted(KEEP),active_files_checked=len(before),active_files_unchanged=True,originals_and_research_scripts_preserved=True,snapshot_directory_guards_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ResearchCleanupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
