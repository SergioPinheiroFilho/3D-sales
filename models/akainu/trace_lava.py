"""Trace orange channels into an editable FreeCAD Sketcher sketch."""

from pathlib import Path
import json
import sys

import FreeCAD as App
import Part
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage


def thin(mask):
    image = np.pad(mask.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            p = image[1:-1, 1:-1]
            neighbours = [image[:-2, 1:-1], image[:-2, 2:], image[1:-1, 2:], image[2:, 2:],
                          image[2:, 1:-1], image[2:, :-2], image[1:-1, :-2], image[:-2, :-2]]
            count = sum(neighbours)
            transitions = sum((neighbours[i] == 0) & (neighbours[(i + 1) % 8] == 1) for i in range(8))
            n, _, e, _, s, _, w, _ = neighbours
            if step == 0:
                clear = (n * e * s == 0) & (e * s * w == 0)
            else:
                clear = (n * e * w == 0) & (n * s * w == 0)
            remove = (p == 1) & (count >= 2) & (count <= 6) & (transitions == 1) & clear
            changed |= bool(remove.any())
            p[remove] = 0
    return image[1:-1, 1:-1].astype(bool)


def simplify(points, tolerance=2.0):
    if len(points) <= 2:
        return points
    values = np.asarray(points, dtype=float)
    direction = values[-1] - values[0]
    length = np.linalg.norm(direction)
    if length < 1e-9:
        distances = np.linalg.norm(values - values[0], axis=1)
    else:
        offsets = values - values[0]
        distances = np.abs(direction[0] * offsets[:, 1] - direction[1] * offsets[:, 0]) / length
    index = int(distances.argmax())
    if distances[index] <= tolerance:
        return [points[0], points[-1]]
    return simplify(points[:index + 1], tolerance)[:-1] + simplify(points[index:], tolerance)


def trace(mask):
    pixels = {tuple(map(int, point)) for point in np.argwhere(mask)}
    adjacency = {}
    for y, x in pixels:
        neighbours = []
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            other = (y + dy, x + dx)
            if other not in pixels:
                continue
            if dy and dx and ((y + dy, x) in pixels or (y, x + dx) in pixels):
                continue
            neighbours.append(other)
        adjacency[(y, x)] = neighbours
    visited = set()
    paths = []
    starts = [p for p in sorted(pixels) if len(adjacency[p]) != 2]
    starts += [p for p in sorted(pixels) if len(adjacency[p]) == 2]
    for start in starts:
        for neighbour in adjacency[start]:
            edge = tuple(sorted((start, neighbour)))
            if edge in visited:
                continue
            path = [start, neighbour]
            visited.add(edge)
            previous, current = start, neighbour
            while len(adjacency[current]) == 2 and current != start:
                following = next(p for p in adjacency[current] if p != previous)
                edge = tuple(sorted((current, following)))
                if edge in visited:
                    break
                visited.add(edge)
                path.append(following)
                previous, current = current, following
            if len(path) >= 9:
                paths.append(simplify(path))
    return paths


def main(source):
    directory = Path(__file__).resolve().parent
    image = Image.open(source).convert('RGB').crop((4, 4, 902, 533))
    values = np.asarray(image, dtype=float)
    r, g, b = values.transpose(2, 0, 1)
    mask = (r > 160) & (g > 65) & (g < r * 0.96) & (b < g * 0.65)
    mask = ndimage.binary_closing(mask, iterations=2)
    labels, _ = ndimage.label(mask)
    sizes = np.bincount(labels.ravel())
    mask &= sizes[labels] > 80
    paths = trace(thin(mask))
    scale = 140 / image.width
    drawing_height = image.height * scale
    offset_y = (150 - drawing_height) / 2
    document = App.newDocument('LavaSketch')
    plate = document.addObject('Part::Box', 'Plate')
    plate.Label = 'Placa 150 x 150 x 2 mm'
    plate.Length = 150
    plate.Width = 150
    plate.Height = 2
    sketch = document.addObject('Sketcher::SketchObject', 'LavaSketch')
    sketch.Label = 'Lava - linhas centrais editaveis'
    sketch.Placement.Base.z = 2.05
    geometry = []
    for path in paths:
        for a, b in zip(path, path[1:]):
            p = App.Vector(5 + a[1] * scale, offset_y + (image.height - a[0]) * scale, 0)
            q = App.Vector(5 + b[1] * scale, offset_y + (image.height - b[0]) * scale, 0)
            if (p - q).Length > 1e-6:
                geometry.append(Part.LineSegment(p, q))
    sketch.addGeometry(geometry, False)
    document.recompute()
    if not plate.Shape.isValid() or sketch.GeometryCount != len(geometry):
        raise ValueError('Document validation failed')
    filename = str(directory / 'lava_sketch_plate.FCStd')
    document.saveAs(filename)
    App.closeDocument(document.Name)
    reopened = App.openDocument(filename)
    if reopened.getObject('LavaSketch').GeometryCount != len(geometry):
        raise ValueError('Reopen validation failed')
    App.closeDocument(reopened.Name)
    # Preview the traced centre lines at the source image scale.
    preview = Image.new('RGB', (image.width, image.height), '#eeeeee')
    draw = ImageDraw.Draw(preview)
    for path in paths:
        draw.line([(x, y) for y, x in path], fill='#e76513', width=2)
    preview.save(directory / 'lava_sketch_preview.png')
    (directory / 'lava_trace.json').write_text(json.dumps({'paths': paths, 'segments': len(geometry),
        'plate_mm': [150, 150, 2], 'drawing_mm': [140, drawing_height]}, indent=2), encoding='utf-8')
    print(json.dumps({'paths': len(paths), 'segments': len(geometry), 'file': filename}))


if __name__ == '__main__':
    main(sys.argv[1])
