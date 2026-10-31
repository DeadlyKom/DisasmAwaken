"""Выделение проверенного рисователя, допускается только восемь доказанных opcode-целей."""
import PreviewEdgeRasterFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewEdgeRaster','Source/Resources/06_D3D/BeforeVertexClass.bin',(
  (0x1E1C,0x1F46,0xDE1C,'Source/D3D/RasterizePreviewEdge.asm'),),
  'PreviewEdgeRasterVerification')
