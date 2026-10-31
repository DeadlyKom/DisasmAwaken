"""Числовая композиция D54C..D818, отдельно от исполнения исходных инструкций."""
from PreviewModelMatrixOracle import product,corrected,arithmetic

SCENE=((0xD567,0xD574,0xD586),(0xD599,0xD5A6,0xD5B8),(0xD5CB,0xD5D8,0xD5EA))
MODEL=((0xD561,0xD5FD,0xD6A9),(0xD563,0xD5FF,0xD6AB),(0xD565,0xD601,0xD6AD))
OUTPUT=((0xD8C1,0xD8D1,0xD8C9),(0xD8D9,0xD8E9,0xD8E1),(0xD8F1,0xD901,0xD8F9))


def compose(scene,model,flags,angle):
 output=[[None]*3 for _ in range(3)];one=bool(flags&1)
 if one and angle&63==0:
  # Выбор исходных столбцов и знаков без табличного умножения на 127.
  selection=(((0,1),(2,1)),((2,-1),(0,1)),((0,-1),(2,-1)),((2,1),(0,-1)))[angle//64]
  for row in range(3):
   output[row][2]=scene[row][1]
   for column,(source,sign) in enumerate(selection):output[row][column]=(scene[row][source]*sign)&255
  last_negated=(scene[2][2] if angle in (64,128) else scene[2][0])
  f=0x54 if angle==0 else arithmetic(0,last_negated,True)[1]
  return dict(output=output,branch='quadrant'+str(angle//64),af=(output[2][1],f))
 # Последовательность двух отражаемых сложений сохраняется, одноосная ветвь пропускает средний член.
 columns=2 if one else 3
 for column in range(columns):
  for row in range(3):
   first=product(scene[row][0],model[0][column])[0]
   partial=first if one else corrected(first,product(scene[row][1],model[1][column])[0])[0]
   last,index,table_value=product(scene[row][2],model[2][column])
   output[row][column],f=corrected(last,partial)
 if one:
  for row in range(3):output[row][2]=scene[row][1]
  final_af=(scene[2][1],0x18|(f&1))
 else:final_af=(output[2][2],f)
 return dict(output=output,branch='one_axis' if one else 'general',af=final_af,hl=0xC300|index,bc=model[0][columns-1]*256+model[1][columns-1],de=model[2][columns-1]*256+table_value,ixh=partial,stack_return=0xD693 if one else 0xD72D)
