"""Generate closed magma shells in millimetres. Requires NumPy."""

import json
from pathlib import Path
import struct
import zlib

import numpy as np


def build_shell(length, wrist_radius, elbow_radius, arc_degrees, rows, columns):
    u, v = np.meshgrid(np.linspace(0, 1, rows), np.linspace(-1, 1, columns), indexing="ij")
    angle = v * np.radians(arc_degrees / 2)
    radius = wrist_radius + (elbow_radius - wrist_radius) * u
    # Offset centres create interleaved molten lobes along the forearm.
    relief = np.zeros_like(u)
    for row in range(5):
        for column in range(4):
            centre_u = 0.08 + row * 0.21 + 0.025 * np.sin(column * 2)
            centre_v = -0.83 + column * 0.55 + 0.1 * np.sin(row * 2)
            curved_v = v - centre_v - 0.14 * np.sin((u - centre_u) * 14)
            lobe = np.exp(-((u - centre_u) / 0.105) ** 2 - (curved_v / 0.24) ** 2)
            relief = np.maximum(relief, lobe)
    edge = np.sin(np.pi * u) ** 0.45 * np.cos(v * np.pi / 2) ** 0.5
    thickness = 2.0 + 7.0 * relief * edge
    outer_radius = radius + thickness
    inner = np.stack((radius * np.sin(angle), length * u, radius * np.cos(angle)), axis=-1)
    outer = np.stack((outer_radius * np.sin(angle), length * u, outer_radius * np.cos(angle)), axis=-1)
    count = rows * columns
    vertices = np.concatenate((outer.reshape(-1, 3), inner.reshape(-1, 3)))
    vertices[:, 2] -= vertices[:, 2].min()
    faces = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            a = row * columns + column
            b, c, d = a + columns, a + columns + 1, a + 1
            faces.extend(((a, b, c), (a, c, d)))
            faces.extend(((a + count, c + count, b + count), (a + count, d + count, c + count)))
    boundary = list(range(columns))
    boundary += [row * columns + columns - 1 for row in range(1, rows)]
    boundary += list(range(count - 2, count - columns - 1, -1))
    boundary += [row * columns for row in range(rows - 2, 0, -1)]
    for index, a in enumerate(boundary):
        b = boundary[(index + 1) % len(boundary)]
        faces.extend(((a, b, b + count), (a, b + count, a + count)))
    return vertices, np.asarray(faces, dtype=np.int32)


def validate(vertices, faces):
    triangles = vertices[faces]
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    if np.any(np.linalg.norm(cross, axis=1) < 1e-9):
        raise ValueError("Degenerate triangle")
    edges = np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    unique, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
    if not np.all(counts == 2):
        raise ValueError("Mesh is not closed")
    directed = np.where(edges[:, 0] < edges[:, 1], 1, -1)
    _, inverse = np.unique(np.sort(edges, axis=1), axis=0, return_inverse=True)
    if np.any(np.bincount(inverse, weights=directed)):
        raise ValueError("Inconsistent winding")
    volume = np.einsum("ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])).sum() / 6
    if volume < 0:
        faces = faces[:, ::-1].copy()
        volume = -volume
    if len(vertices) - len(unique) + len(faces) != 2:
        raise ValueError("Unexpected topology")
    return faces, {"triangles": len(faces), "closed": True, "volume_mm3": round(float(volume), 1),
                   "bounds_mm": np.round(np.ptp(vertices, axis=0), 2).tolist()}


def save_mesh(directory, name, vertices, faces):
    faces, report = validate(vertices, faces)
    with (directory / f"{name}.stl").open("wb") as stream:
        stream.write(b"Magma prototype; units mm".ljust(80, b"\0"))
        stream.write(struct.pack("<I", len(faces)))
        for triangle in vertices[faces]:
            normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            normal /= np.linalg.norm(normal)
            stream.write(struct.pack("<12fH", *normal, *triangle.flatten(), 0))
    with (directory / f"{name}.obj").open("w", encoding="utf-8") as stream:
        stream.write("# Units mm; geometry only\n")
        for vertex in vertices:
            stream.write("v {:.5f} {:.5f} {:.5f}\n".format(*vertex))
        for face in faces + 1:
            stream.write("f {} {} {}\n".format(*face))
    return report


def save_preview(directory):
    vertices, faces = build_shell(150, 30, 43, 140, 76, 51)
    # Orthographic illustration of the actual mesh, with illustrative surface colours.
    rotation_x = np.array([[1, 0, 0], [0, 0.75, -0.66144], [0, 0.66144, 0.75]])
    rotation_z = np.array([[0.92, -0.392, 0], [0.392, 0.92, 0], [0, 0, 1]])
    transformed = (vertices - vertices.mean(axis=0)) @ rotation_z.T @ rotation_x.T
    pixels = np.full((800, 800, 3), (231, 233, 236), dtype=np.uint8)
    depth = np.full((800, 800), -np.inf)
    projected = transformed[:, :2] * 4.0 + 400
    for face in faces:
        points = projected[face]
        low = np.maximum(np.floor(points.min(axis=0)).astype(int), 0)
        high = np.minimum(np.ceil(points.max(axis=0)).astype(int), 799)
        xx, yy = np.meshgrid(np.arange(low[0], high[0] + 1), np.arange(low[1], high[1] + 1))
        a, b, c = points
        denominator = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(denominator) < 1e-8:
            continue
        first = ((xx - a[0]) * (c[1] - a[1]) - (yy - a[1]) * (c[0] - a[0])) / denominator
        second = ((b[0] - a[0]) * (yy - a[1]) - (b[1] - a[1]) * (xx - a[0])) / denominator
        z = transformed[face[0], 2] + first * (transformed[face[1], 2] - transformed[face[0], 2]) + second * (transformed[face[2], 2] - transformed[face[0], 2])
        mask = (first >= 0) & (second >= 0) & (first + second <= 1) & (z > depth[yy, xx])
        normal = np.cross(transformed[face[1]] - transformed[face[0]], transformed[face[2]] - transformed[face[0]])
        normal /= np.linalg.norm(normal)
        shade = 0.35 + 0.65 * abs(np.dot(normal, np.array([0.25, -0.4, 0.88])))
        colour = np.array([175, 31, 21]) if face.max() < 76 * 51 else np.array([90, 55, 50])
        pixels[yy[mask], xx[mask]] = np.clip(colour * shade, 0, 255)
        depth[yy[mask], xx[mask]] = z[mask]
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\0' + row.tobytes() for row in pixels[::-1])
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 800, 800, 8, 2, 0, 0, 0))
    (directory / 'preview.png').write_bytes(png + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    reports = {}
    for name, parameters in {
        "forearm_concept": (150, 30, 43, 140, 151, 101),
        "magma_sample": (50, 35, 35, 65, 71, 61),
    }.items():
        vertices, faces = build_shell(*parameters)
        reports[name] = save_mesh(directory, name, vertices, faces)
    (directory / "validation.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(reports, indent=2))
    save_preview(directory)
