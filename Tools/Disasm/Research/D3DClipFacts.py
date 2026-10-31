"""Точная настройка существующих операндов границ D3D банка 4."""
FUNCTIONS={0xE011:('ConfigurePreviewClip','Настройка четырёх углов и повторённых операндов границ корабельного просмотра')}
LABELS={}
DOCUMENTS={('D3D',0xE011):('PreviewClipBounds','байтовые пределы, повторённые операнды, углы и сохранённый Carry')}
PATCHES={0xDAE7:'HalfXLow',0xDBA5:'HalfYLow',0xE7DB:'MaxCorner',0xE7BA:'MinCorner',0xE7D0:'MaxXMinY',0xE7C5:'MinXMaxY',0xDF7F:'AfterMaxX',0xDF64:'AfterMaxY'}
for prefix,addresses in (('MaxX',(0xE613,0xE6E0,0xE6F3,0xE72E,0xE78B)),('MinX',(0xE5F4,0xE695,0xE6A8,0xE73F,0xE79C)),('MaxY',(0xE646,0xE69D,0xE6E8,0xE788,0xE799,0xE7AB)),('MinY',(0xE627,0xE692,0xE6DD,0xE72B,0xE73C,0xE74E))):
 for i,address in enumerate(addresses):PATCHES[address]=prefix+str(i)
PATCH_FORMS={}
for address,name in PATCHES.items():
 if name in ('HalfYLow','MaxCorner','MinCorner','MaxXMinY','MinXMaxY'):opcode,kind=0x11,'LD DE,nn'
 elif name.startswith('After'):opcode,kind=0xFE,'CP n'
 elif name in ('HalfXLow','MaxX0','MinX0','MaxY0','MinY0'):opcode,kind=1,'LD BC,nn'
 elif name in ('MaxY1','MaxY2'):opcode,kind=0x2E,'LD L,n'
 else:opcode,kind=0x36,'LD (HL),n'
 PATCH_FORMS[address]=(opcode,kind,2 if name in ('MaxCorner','MinCorner','MaxXMinY','MinXMaxY') else 1)
CONTRACTS={('D3D',0xE011):(
 ['HL - H верхний предел X, L верхний предел Y, DE - D нижний предел X, E нижний предел Y, все компоненты байтовые',
  'подключён исходный D3D в банке 4, существующие операнды графического ядра доступны для записи'],
 ['HL - H исходный верхний X, L исходный нижний Y, DE - D исходный нижний X, E исходный верхний Y, BC сохранён',
  'AF - A исходный нижний Y, F от INC исходного верхнего Y, Carry равен биту 0 суммы верхний Y+1 по модулю 256',
  'четыре упакованных угла и повторённые граничные операнды настроены, полупределы равны ((верхняя компонента+1) AND FF) SHR 1',
  'альтернативные и индексные регистры, I, IFF и IM сохранены, SP обычного возврата равен входному SP+2'],
 ['HL, DE, AF'],
 ['верхний X берётся из ширины текстового окна минус 14, верхний Y из высоты минус 13 в исходном DrawItem26, нижние пределы там нулевые',
  'процедура не проверяет порядок границ и не включает нижние пределы в расчёт полупределов',
  'при верхнем пределе FF прибавление единицы оборачивается в ноль до деления, это исходное поведение',
  'полупределы и первые копии X и Y меняют младшие байты слов, остальные копии меняют байтовые операнды LD (HL),n или LD L,n',
  'всего меняются 34 байта существующих операндов в банке 4, экран, порт страниц и стековая память не записываются'])}
COMMENTS={0xE011:(['-----------------------------------------','Полупределы и четыре угла','-----------------------------------------','расчёт байтового полупредела X с исходным оборачиванием FF в ноль'],None),
 0xE018:(['расчёт байтового полупредела Y, младший бит суммы останется в Carry до возврата'],None),
 0xE01F:(['сохранение углов с одновременно верхними и одновременно нижними компонентами'],None),
 0xE026:(['перестановка только младших компонент для двух остальных углов'],None),
 0xE030:(['-----------------------------------------','Повторённые операнды пределов','-----------------------------------------','обновление копий верхнего X и исключённого предела X+1'],None),
 0xE044:(['обновление копий нижнего X, меняются только указанные байтовые операнды'],None),
 0xE054:(['обновление копий верхнего Y и исключённого предела Y+1'],None),
 0xE06B:(['обновление копий нижнего Y без изменения флагов последнего INC верхнего Y'],None)}


def name_operands(region,address,operation):
 if region=='D3D' and address==0xE011:
  for value,name in PATCHES.items():operation=operation.replace('(#'+format(value,'04X')+')','(@D3DClipState.'+name+')')
 return operation

from D3DThirdFacts import COMMENTS as THIRD_COMMENTS
COMMENTS.update(THIRD_COMMENTS)

from D3DSetupFacts import COMMENTS as SETUP_COMMENTS
COMMENTS.update(SETUP_COMMENTS)

from D3DDescriptionFacts import COMMENTS as DESCRIPTION_COMMENTS
COMMENTS.update(DESCRIPTION_COMMENTS)

from D3DPriceFacts import COMMENTS as PRICE_COMMENTS
COMMENTS.update(PRICE_COMMENTS)

from PreviewMultiplyFacts import COMMENTS as PREVIEW_MULTIPLY_COMMENTS
COMMENTS.update(PREVIEW_MULTIPLY_COMMENTS)

from PreviewTransformFacts import COMMENTS as PREVIEW_TRANSFORM_COMMENTS
COMMENTS.update(PREVIEW_TRANSFORM_COMMENTS)

from PreviewQueueFacts import COMMENTS as PREVIEW_QUEUE_COMMENTS
COMMENTS.update(PREVIEW_QUEUE_COMMENTS)

from PreviewLookupProductFacts import COMMENTS as PREVIEW_LOOKUP_COMMENTS
COMMENTS.update(PREVIEW_LOOKUP_COMMENTS)

from PreviewBoundsFacts import COMMENTS as PREVIEW_BOUNDS_COMMENTS
COMMENTS.update(PREVIEW_BOUNDS_COMMENTS)

from PreviewQueueBuildFacts import COMMENTS as PREVIEW_QUEUE_BUILD_COMMENTS
COMMENTS.update(PREVIEW_QUEUE_BUILD_COMMENTS)

from PreviewModelMatrixFacts import COMMENTS as PREVIEW_MODEL_MATRIX_COMMENTS
COMMENTS.update(PREVIEW_MODEL_MATRIX_COMMENTS)

from PreviewMatrixComposeFacts import COMMENTS as PREVIEW_MATRIX_COMPOSE_COMMENTS
COMMENTS.update(PREVIEW_MATRIX_COMPOSE_COMMENTS)

from PreviewProjectionScaleFacts import COMMENTS as PREVIEW_PROJECTION_SCALE_COMMENTS
COMMENTS.update(PREVIEW_PROJECTION_SCALE_COMMENTS)

from PreviewPerspectiveFacts import COMMENTS as PREVIEW_PERSPECTIVE_COMMENTS
COMMENTS.update(PREVIEW_PERSPECTIVE_COMMENTS)

from PreviewVertexGroupFacts import COMMENTS as PREVIEW_VERTEX_GROUP_COMMENTS
COMMENTS.update(PREVIEW_VERTEX_GROUP_COMMENTS)

from PreviewVertexProductsFacts import COMMENTS as PREVIEW_VERTEX_PRODUCTS_COMMENTS
COMMENTS.update(PREVIEW_VERTEX_PRODUCTS_COMMENTS)

from PreviewModelWalkFacts import COMMENTS as PREVIEW_MODEL_WALK_COMMENTS
COMMENTS.update(PREVIEW_MODEL_WALK_COMMENTS)

from PreviewVertexClassFacts import COMMENTS as PREVIEW_VERTEX_CLASS_COMMENTS
COMMENTS.update(PREVIEW_VERTEX_CLASS_COMMENTS)

from PreviewFaceMathFacts import COMMENTS as PREVIEW_FACE_MATH_COMMENTS
COMMENTS.update(PREVIEW_FACE_MATH_COMMENTS)

from PreviewFaceCodesFacts import COMMENTS as PREVIEW_FACE_CODES_COMMENTS
COMMENTS.update(PREVIEW_FACE_CODES_COMMENTS)

from PreviewEdgeRasterFacts import COMMENTS as PREVIEW_EDGE_RASTER_COMMENTS
COMMENTS.update(PREVIEW_EDGE_RASTER_COMMENTS)

from PreviewSlopeDivisionFacts import COMMENTS as PREVIEW_SLOPE_DIVISION_COMMENTS
COMMENTS.update(PREVIEW_SLOPE_DIVISION_COMMENTS)

from PreviewPolygonRowsFacts import COMMENTS as PREVIEW_POLYGON_ROWS_COMMENTS
COMMENTS.update(PREVIEW_POLYGON_ROWS_COMMENTS)

from PreviewPolygonEdgesFacts import COMMENTS as PREVIEW_POLYGON_EDGES_COMMENTS
COMMENTS.update(PREVIEW_POLYGON_EDGES_COMMENTS)

from PreviewPolygonPreparationFacts import COMMENTS as PREVIEW_POLYGON_PREPARATION_COMMENTS
COMMENTS.update(PREVIEW_POLYGON_PREPARATION_COMMENTS)

from PreviewInsideFaceStreamFacts import COMMENTS as PREVIEW_INSIDE_FACE_STREAM_COMMENTS
COMMENTS.update(PREVIEW_INSIDE_FACE_STREAM_COMMENTS)

from PreviewClipUnwindFacts import COMMENTS as PREVIEW_CLIP_UNWIND_COMMENTS
COMMENTS.update(PREVIEW_CLIP_UNWIND_COMMENTS)

from PreviewClipTailFacts import COMMENTS as PREVIEW_CLIP_TAIL_COMMENTS
COMMENTS.update(PREVIEW_CLIP_TAIL_COMMENTS)

from PreviewClipProductDifferenceFacts import COMMENTS as PREVIEW_CLIP_PRODUCT_DIFFERENCES_COMMENTS
COMMENTS.update(PREVIEW_CLIP_PRODUCT_DIFFERENCES_COMMENTS)

from PreviewClipProductBuilderFacts import COMMENTS as PREVIEW_CLIP_PRODUCT_BUILDERS_COMMENTS
COMMENTS.update(PREVIEW_CLIP_PRODUCT_BUILDERS_COMMENTS)

from PreviewClipDivisionFacts import COMMENTS as PREVIEW_CLIP_DIVISION_COMMENTS
COMMENTS.update(PREVIEW_CLIP_DIVISION_COMMENTS)

from PreviewClipIntersectionFacts import COMMENTS as PREVIEW_CLIP_INTERSECTIONS_COMMENTS
COMMENTS.update(PREVIEW_CLIP_INTERSECTIONS_COMMENTS)

from PreviewClipCaseFacts import COMMENTS as PREVIEW_CLIP_CASES_COMMENTS
COMMENTS.update(PREVIEW_CLIP_CASES_COMMENTS)

from PreviewClipDispatchFacts import COMMENTS as PREVIEW_CLIP_DISPATCH_COMMENTS
COMMENTS.update(PREVIEW_CLIP_DISPATCH_COMMENTS)

from PreviewClipPolygonFacts import COMMENTS as PREVIEW_CLIP_POLYGON_COMMENTS
COMMENTS.update(PREVIEW_CLIP_POLYGON_COMMENTS)

from PreviewClippedFaceStreamFacts import COMMENTS as PREVIEW_CLIPPED_FACE_STREAM_COMMENTS
COMMENTS.update(PREVIEW_CLIPPED_FACE_STREAM_COMMENTS)

from PreviewQueueRenderFacts import COMMENTS as PREVIEW_QUEUE_RENDER_COMMENTS
COMMENTS.update(PREVIEW_QUEUE_RENDER_COMMENTS)

from PreviewFrameFacts import COMMENTS as PREVIEW_FRAME_COMMENTS
COMMENTS.update(PREVIEW_FRAME_COMMENTS)
