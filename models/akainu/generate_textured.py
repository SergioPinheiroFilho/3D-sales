"""Map supplied lava/mud STL relief onto the forearm shell. Run with FreeCAD Python."""

import hashlib
import json
from pathlib import Path
import struct

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import gaussian_filter, map_coordinates
from PIL import Image

from generate import build_shell, validate


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'v2'
OUTPUT.mkdir(exist_ok=True)
STL_DTYPE = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])


def source_heightmap(filename, crop):
    path = ROOT / filename
    triangles = np.fromfile(path, dtype=STL_DTYPE, offset=84)
    points = triangles['vertices'].reshape(-1, 3).astype(float)
    minimum, maximum = points.min(axis=0), points.max(axis=0)
    # Keep the upper-facing surface, discarding the pedestal underside and vertical rim.
    edges = triangles['vertices'][:, 1:] - triangles['vertices'][:, :1]
    normals = np.cross(edges[:, 0], edges[:, 1])
    points = triangles['vertices'][normals[:, 2] > 1e-8].reshape(-1, 3).astype(float)
    xy, inverse = np.unique(np.round(points[:, :2], 5), axis=0, return_inverse=True)
    top = np.full(len(xy), -np.inf)
    np.maximum.at(top, inverse, points[:, 2])
    interpolator = LinearNDInterpolator(xy, top)
    centre = (minimum[:2] + maximum[:2]) / 2
    x = np.linspace(centre[0] - crop[0] / 2, centre[0] + crop[0] / 2, 501)
    y = np.linspace(centre[1] - crop[1] / 2, centre[1] + crop[1] / 2, 501)
    xx, yy = np.meshgrid(x, y)
    height = interpolator(xx, yy)
    if not np.isfinite(height).all():
        raise ValueError(f'Incomplete source surface: {filename}')
    height = gaussian_filter(height, 0.6)
    low, high = np.percentile(height, [2, 98])
    height = np.clip((height - low) / (high - low), 0, 1)
    Image.fromarray((height[::-1] * 255).astype(np.uint8)).save(OUTPUT / f'{filename.split(".")[0]}_height.png')
    return height, {'filename': filename, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'source_triangles': len(triangles), 'crop_mm': crop,
                    'source_bounds_mm': (maximum - minimum).tolist()}


lava, lava_info = source_heightmap('Cracked_Lava_base_0.stl', (21, 21))
mud, mud_info = source_heightmap('120x92 mud 1.stl', (58, 78))


def textured_shell(start=0, end=1, rows=321, columns=181, sample=False):
    length, wrist, elbow, arc = (50, 35, 35, 65) if sample else (230, 38, 58, 140)
    vertices, faces = build_shell(length, wrist, elbow, arc, rows, columns, start, end)
    u, v = np.meshgrid(np.linspace(start, end, rows), np.linspace(-1, 1, columns), indexing='ij')
    radius = wrist + (elbow - wrist) * u
    angle = v * np.radians(arc / 2)
    transverse = angle * radius
    longitudinal = length * u
    lava_values = map_coordinates(lava, [longitudinal / 36 * 500, (transverse + 90) / 36 * 500],
                                  order=1, mode='mirror')
    mud_values = map_coordinates(mud, [(longitudinal + 17) / 100 * 500,
                                     (transverse + 65) / 75 * 500], order=1, mode='mirror')
    # Mud fissures modulate the larger plates; lava supplies local chipped relief.
    relief = (0.25 + 0.75 * mud_values) * lava_values
    # Fade only the overall ends, keeping both halves identical at their shared boundary.
    longitudinal_fade = np.minimum(np.minimum(u / 0.025, (1 - u) / 0.025), 1)
    lateral_fade = np.minimum((1 - np.abs(v)) / 0.06, 1)
    fade = np.clip(longitudinal_fade * lateral_fade, 0, 1)
    thickness = 2.0 + (5.0 * relief + 1.2 * mud_values) * fade
    outer_radius = radius + thickness
    inner = np.stack((radius * np.sin(angle), length * u, radius * np.cos(angle)), axis=-1)
    outer = np.stack((outer_radius * np.sin(angle), length * u, outer_radius * np.cos(angle)), axis=-1)
    vertices = np.concatenate((outer.reshape(-1, 3), inner.reshape(-1, 3)))
    # Common Z origin keeps the two exported halves aligned when assembled.
    vertices[:, 2] -= wrist * np.cos(np.radians(arc / 2))
    vertices[:, 1] -= length * start
    return vertices, faces, thickness


def save_stl(name, vertices, faces):
    faces, report = validate(vertices, faces)
    triangle = vertices[faces]
    normals = np.cross(triangle[:, 1] - triangle[:, 0], triangle[:, 2] - triangle[:, 0])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    values = np.zeros(len(faces), dtype=STL_DTYPE)
    values['normal'], values['vertices'] = normals, triangle
    with (OUTPUT / f'{name}.stl').open('wb') as stream:
        stream.write(b'Akainu v2 source mesh relief; millimetres'.ljust(80, b'\0'))
        stream.write(struct.pack('<I', len(faces)))
        stream.write(values.tobytes())
    # Check the exported float32 mesh, where thin/degenerate triangles could appear.
    exported = np.fromfile(OUTPUT / f'{name}.stl', dtype=STL_DTYPE, offset=84)['vertices']
    points, mapping = np.unique(exported.reshape(-1, 3), axis=0, return_inverse=True)
    validate(points.astype(float), mapping.reshape(-1, 3))
    report['export_reloaded_valid'] = True
    return report


def render(vertices, faces, thickness, filename):
    # Z-buffer render of the actual geometry; colour illustrates a future paint scheme.
    rotation = np.array([[0.94, -0.342, 0], [0.2, 0.55, -0.81], [0.277, 0.761, 0.585]])
    points = vertices @ rotation.T
    scale = min(800 / np.ptp(points[:, 0]), 1100 / np.ptp(points[:, 1]))
    projected = points[:, :2] * scale
    projected -= (projected.min(axis=0) + projected.max(axis=0)) / 2
    projected += [500, 650]
    pixels = np.full((1300, 1000, 3), (235, 234, 230), dtype=np.uint8)
    depth = np.full((1300, 1000), -np.inf)
    count = thickness.size
    for face in faces:
        a, b, c = projected[face]
        low = np.maximum(np.floor(np.minimum(np.minimum(a, b), c)).astype(int), 0)
        high = np.minimum(np.ceil(np.maximum(np.maximum(a, b), c)).astype(int), [999, 1299])
        xx, yy = np.meshgrid(np.arange(low[0], high[0] + 1), np.arange(low[1], high[1] + 1))
        denominator = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(denominator) < 1e-9:
            continue
        first = ((xx - a[0]) * (c[1] - a[1]) - (yy - a[1]) * (c[0] - a[0])) / denominator
        second = ((b[0] - a[0]) * (yy - a[1]) - (b[1] - a[1]) * (xx - a[0])) / denominator
        z = points[face[0], 2] + first * (points[face[1], 2] - points[face[0], 2]) + second * (points[face[2], 2] - points[face[0], 2])
        mask = (first >= 0) & (second >= 0) & (first + second <= 1) & (z > depth[yy, xx])
        normal = np.cross(points[face[1]] - points[face[0]], points[face[2]] - points[face[0]])
        normal /= np.linalg.norm(normal)
        shade = 0.3 + 0.7 * abs(float(normal @ np.array([0.3, -0.4, 0.866])))
        colour = np.array([173, 44, 26])
        if face.max() < count:
            value = thickness.ravel()[face].mean()
            colour = np.array([236, 100, 20]) if value < 3.4 else np.array([113, 27, 21])
        pixels[yy[mask], xx[mask]] = np.clip(colour * shade, 0, 255)
        depth[yy[mask], xx[mask]] = z[mask]
    Image.fromarray(pixels).save(OUTPUT / filename)


reports = {}
for name, parameters in {'forearm_full_v2': {}, 'forearm_wrist_v2': {'end': 0.5, 'rows': 161},
                         'forearm_elbow_v2': {'start': 0.5, 'rows': 161},
                         'magma_sample_v2': {'sample': True, 'rows': 101, 'columns': 101}}.items():
    vertices, faces, thickness = textured_shell(**parameters)
    reports[name] = save_stl(name, vertices, faces)
    print(name, reports[name], flush=True)

# Exact correspondence of both sides of the split, before STL quantisation.
wrist, _, _ = textured_shell(end=0.5, rows=161)
elbow, _, _ = textured_shell(start=0.5, rows=161)
for offset in (0, 161 * 181):
    if not np.allclose(wrist[offset + 160 * 181:offset + 161 * 181],
                       elbow[offset:offset + 181] + [0, 115, 0]):
        raise ValueError('Split boundary mismatch')
reports['sources'] = [lava_info, mud_info]
reports['seam_matches'] = True
(OUTPUT / 'validation.json').write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
vertices, faces, thickness = textured_shell(rows=161, columns=121)
render(vertices, faces, thickness, 'preview.png')
print('Rendering complete', flush=True)
