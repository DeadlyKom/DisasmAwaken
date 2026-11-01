"""Независимая арифметическая модель звукового ядра, без исполнения Z80-команд."""
PROFILES=(
 {'name':'A','disabled':0xDFEF,'sample':0xDFF6,'sample_pos':0xDFFA,'adjust':0xE011,'volume':0xE02D,'envelope':0xE037,'noise':0xE03E,'env_shift':0xE055,'tone_shift':0xE06C,'ornament':0xE078,'orn_pos':0xE07C,'note':0xE0BB,'slide':0xE098,'counter':0xE09F,'step':0xE0A8,'reload':0xE0CE,'branch':0xE0AF,'target':0xE0B3,'gate':0xE0D7,'off':0xE0E5,'on':0xE0E9},
 {'name':'B','disabled':0xE0EE,'sample':0xE0F5,'sample_pos':0xE0F9,'adjust':0xE110,'volume':0xE12C,'envelope':0xE136,'noise':0xE13D,'env_shift':0xE154,'tone_shift':0xE16C,'ornament':0xE178,'orn_pos':0xE17C,'note':0xE1BB,'slide':0xE198,'counter':0xE19F,'step':0xE1A8,'reload':0xE1CE,'branch':0xE1AF,'target':0xE1B3,'gate':0xE1D7,'off':0xE1E5,'on':0xE1E9},
 {'name':'C','disabled':0xE1EE,'sample':0xE1F5,'sample_pos':0xE1F9,'adjust':0xE20F,'volume':0xE22B,'envelope':0xE235,'noise':0xE23C,'env_shift':0xE253,'tone_shift':0xE26A,'ornament':0xE276,'orn_pos':0xE27A,'note':0xE2B9,'slide':0xE296,'counter':0xE29D,'step':0xE2A6,'reload':0xE2CC,'branch':0xE2AD,'target':0xE2B1,'gate':0xE2D5,'off':0xE2E3,'on':0xE2E7})


def synthesize(memory,sp,initial_alt_bc):
 m=list(memory);writes=set();events={};checkpoints=[];envelope=m[0xDFE4];noise=m[0xDFE9];mixer=m[0xDFE8];last_bc=initial_alt_bc
 def byte(a,v):m[a]=v&255;writes.add(a)
 def word(a,v):byte(a,v);byte(a+1,v>>8)
 def read(a):return m[a]+256*m[a+1]
 def advance(position,loop,length):
  next_pos=(position+1)&255
  return next_pos if next_pos<length else loop
 word(0xE30E,sp)
 for channel,p in enumerate(PROFILES):
  level=0;level_flags=None;active=m[p['disabled']]!=255;counter_result=None;exit_kind='disabled';data_sp=None
  if m[p['disabled']]!=255:
   assert m[p['disabled']]==0
   sample=read(p['sample']);pos=m[p['sample_pos']];byte(p['sample_pos'],advance(pos,m[sample],m[sample+1]))
   # A и B удваивают слово, затем только L, старший перенос второго удвоения теряется.
   sample_offset=(((pos*2)&0xFF00)|((pos*4)&255)) if channel<2 else pos*4
   address=sample+2+sample_offset;control=m[address];modes=m[address+1];tone_delta=read(address+2)
   adjust=m[p['adjust']]
   if control&128:
    adjust=adjust+int(adjust<31) if control&64 else max(adjust-1,0);byte(p['adjust'],adjust)
   volume=max(0,min(15,(modes&15)+adjust-16));level=m[0xDC00+((volume+m[p['volume']])&255)]
   if not control&1:level|=m[p['envelope']]
   shifted=control>>1
   flag_value=shifted if control&1 else level
   level_flags=(flag_value&0xA8)|(0x40 if not flag_value else 0)|(4 if flag_value.bit_count()%2==0 else 0)|(1 if control&1 else 0)
   if modes&128:
    delta=shifted&31;delta=delta-32 if delta&16 else delta;contribution=(m[p['env_shift']]+delta)&255
    if modes&32:byte(p['env_shift'],contribution)
    envelope=(envelope+contribution)&255
   else:
    noise=(m[p['noise']]+shifted)&255
    if modes&32:byte(p['noise'],noise)
   channel_mixer=((modes>>4)&1)<<channel | ((modes>>7)&1)<<(channel+3)
   mixer=channel_mixer if channel==0 else mixer|channel_mixer
   tone=(read(p['tone_shift'])+tone_delta)&65535
   if modes&64:word(p['tone_shift'],tone)
   ornament=read(p['ornament']);pos=m[p['orn_pos']];byte(p['orn_pos'],advance(pos,m[ornament],m[ornament+1]));note=(m[p['note']]+m[ornament+2+pos])&255;index=0 if note&128 else note
   period=read(0xDD00+index*2);old_slide=read(p['slide']);last_bc=old_slide;output=(period+tone+old_slide)&65535;word(0xDC00+2*channel,output);data_sp=0xDD00+index*2+2;exit_kind='restore'
   counter=m[p['counter']]
   if 1<=counter<=128:
    if counter>1:counter_result=counter-1;exit_kind='store'
    else:
     new_slide=(old_slide+read(p['step']))&65535;word(p['slide'],new_slide);reached=False
     if m[p['branch']]==0:
      target=m[p['target']];target_period=read(0xDD00+((target*2)&255));comparison=(new_slide+output)&65535;data_sp=0xDD00+((target*2)&255)+2
      if target>=m[p['note']]:difference=(target_period-comparison)&65535;reached=target_period>=comparison
      else:difference=(comparison-target_period-1)&65535;reached=comparison>target_period
      events['limited'] = events.get('limited',0)+1
      if reached:
       byte(p['note'],target);word(p['slide'],difference&0xFF00);events['limit_reached']=events.get('limit_reached',0)+1
       events['limit_reached_with_high_residue']=events.get('limit_reached_with_high_residue',0)+int(bool(difference&0xFF00))
     else:assert m[p['branch']]==0x1D
     counter_result=0 if reached else m[p['reload']];exit_kind='store' if reached else 'reload'
  checkpoints.append(dict(values={a:m[a] for a in writes},writes=set(writes),ix=noise*256+mixer,envelope=envelope,bc=last_bc,active=active,level=level,level_flags=level_flags,exit_kind=exit_kind,data_sp=data_sp,counter_result=counter_result))
  if counter_result is not None:byte(p['counter'],counter_result)
  byte(0xDC08+channel,level)
  counter=m[p['gate']]
  if 1<=counter<=128:
   if counter==1:
    state=m[p['disabled']]^255;byte(p['disabled'],state);byte(p['gate'],m[p['on']] if not state else m[p['off']])
   else:byte(p['gate'],counter-1)
 # Общий период записывается раньше шага огибающей, перенос младшего сложения отброшен.
 base=read(0xE2F1);offset=read(0xE2EE);period=(((base&0xFF00)|((base+envelope)&255))+offset)&65535;word(0xDC0B,period);counter=m[0xE2FA]
 if 1<=counter<=128:
  if counter==1:word(0xE2EE,offset+read(0xE302));byte(0xE2FA,m[0xE309])
  else:byte(0xE2FA,counter-1)
 byte(0xDFE9,noise);frame=m[0xDC00:0xDC0E];shape=frame[13];frame[6]=(frame[6]+noise)&255;frame[7]=mixer;ports=[]
 for register in range(14 if shape else 13):ports += [(0xFFFD,register),(0xBFFD if register in (6,7,13) else 0xBEFD,frame[register])]
 if shape:byte(0xDC0D,0)
 return dict(memory=m,writes=writes,ports=ports,ix=noise*256+mixer,last_bc=last_bc,shape=shape,events=events,checkpoints=checkpoints)
