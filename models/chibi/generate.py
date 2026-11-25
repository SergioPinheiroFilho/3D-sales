"""Generate editable FreeCAD risers and upside-down printing STL files."""

import json
from pathlib import Path

import FreeCAD as App
import Part
import MeshPart
from PIL import Image, ImageDraw
import numpy as np


DIRECTORY = Path(__file__).resolve().parent
document = App.newDocument('ChibiDisplay')
parameters = document.addObject('Spreadsheet::Sheet', 'Dimensions')
parameters.Label = 'Dimensoes editaveis (mm)'
for row, (name, value) in enumerate((('Width', 48), ('Depth', 48), ('Wall', 2.4),
                                   ('Top', 3), ('FrontHeight', 8), ('RearHeight', 38)), 1):
    parameters.set(f'A{row}', name)
    parameters.set(f'B{row}', f'{value} mm')
    parameters.setAlias(f'B{row}', name)

reports = {}
display_shapes = []
for name, height, y_offset in (('Front', 'FrontHeight', 0), ('Rear', 'RearHeight', 50)):
    outer = document.addObject('Part::Box', f'{name}Outer')
    outer.setExpression('Length', 'Dimensions.Width')
    outer.setExpression('Width', 'Dimensions.Depth')
    outer.setExpression('Height', f'Dimensions.{height}')
    outer.Placement.Base.y = y_offset
    cavity = document.addObject('Part::Box', f'{name}Cavity')
    cavity.setExpression('Length', 'Dimensions.Width - 2 * Dimensions.Wall')
    cavity.setExpression('Width', 'Dimensions.Depth - 2 * Dimensions.Wall')
    cavity.setExpression('Height', f'Dimensions.{height} - Dimensions.Top + 1 mm')
    cavity.setExpression('Placement.Base.x', 'Dimensions.Wall')
    cavity.setExpression('Placement.Base.y', f'{y_offset} mm + Dimensions.Wall')
    cavity.Placement.Base.z = -1
    result = document.addObject('Part::Cut', name)
    result.Label = 'Modulo baixo' if name == 'Front' else 'Modulo alto'
    result.Base = outer
    result.Tool = cavity
    document.recompute()
    if not result.Shape.isValid() or len(result.Shape.Solids) != 1:
        raise ValueError('Invalid riser solid')
    display_shapes.append(result.Shape.copy())
    shape = result.Shape.copy()
    shape.translate(App.Vector(0, -y_offset, 0))
    shape.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
    shape.translate(App.Vector(0, -shape.BoundBox.YMin, -shape.BoundBox.ZMin))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.2, Relative=False)
    if not mesh.isSolid():
        raise ValueError('STL mesh is not closed')
    mesh.write(str(DIRECTORY / f'chibi_{name.lower()}_print.stl'))
    reports[name] = {'solid': True, 'volume_mm3': round(result.Shape.Volume, 2),
                     'size_mm': [result.Shape.BoundBox.XLength, result.Shape.BoundBox.YLength,
                                 result.Shape.BoundBox.ZLength]}

document.recompute()
filename = str(DIRECTORY / 'chibi_display.FCStd')
document.saveAs(filename)
App.closeDocument(document.Name)
verified = App.openDocument(filename)
for name in reports:
    if not verified.getObject(name).Shape.isValid():
        raise ValueError('Reopened document is invalid')
App.closeDocument(verified.Name)

# Render actual CAD surfaces, plus circles showing the nominal 30 mm figure bases.
image = Image.new('RGB', (900, 800), '#eeeeec')
draw = ImageDraw.Draw(image)
rotation = np.array([[0.85, 0.53, 0], [0.28, -0.45, -0.85], [0.45, -0.72, 0.53]])
polygons = []
for index, shape in enumerate(display_shapes):
    vertices, faces = shape.tessellate(0.25)
    points = np.array([[p.x, p.y, p.z] for p in vertices]) @ rotation.T
    for face in faces:
        triangle = points[list(face)]
        normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        normal /= np.linalg.norm(normal)
        brightness = 0.55 + 0.45 * abs(float(normal @ np.array([0.2, -0.5, 0.84])))
        base = np.array([52, 57, 63]) if index == 0 else np.array([226, 225, 214])
        colour = tuple((base * brightness).astype(int))
        xy = [(float(p[0] * 5 + 300), float(p[1] * 5 + 430)) for p in triangle]
        polygons.append((float(triangle[:, 2].mean()), xy, colour))
for _, polygon, colour in sorted(polygons, key=lambda item: item[0]):
    draw.polygon(polygon, fill=colour)
for y_offset, height in ((0, 8), (50, 38)):
    angle = np.linspace(0, 2 * np.pi, 120)
    circle = np.column_stack((24 + 15 * np.cos(angle), y_offset + 24 + 15 * np.sin(angle),
                              np.full_like(angle, height + 0.1))) @ rotation.T
    draw.line([(float(p[0] * 5 + 300), float(p[1] * 5 + 430)) for p in circle], fill='#d28738', width=3)
image.save(DIRECTORY / 'preview.png')
(DIRECTORY / 'validation.json').write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
print(json.dumps(reports))
