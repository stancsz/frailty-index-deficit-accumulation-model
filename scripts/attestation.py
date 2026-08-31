"""Deterministic SHA-256 sidecar helpers for committed artifacts.

A sidecar is a small ``*.sha256`` text file written next to a checked-in
artifact. The sidecar records the canonical lowercase hex SHA-256 of the
artifact's bytes. Generating and checking the sidecar never embeds the
digest in the artifact itself, so the sidecar's hash is stable even when
the same byte sequence is hashed again.

The format is the standard ``<hex>  <relative-name>`` shape used by
``sha256sum`` so reviewers can verify the file with ``sha256sum -c``::

    a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e  docs/demo-data.json

The two-space separator and the relative POSIX path are required for
deterministic regeneration across operating systems. The artifact itself
must never embed a digest field; if you need a self-describing digest,
add it to a sidecar instead.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    """Return the lowercase hex SHA-256 digest of the file at ``path``."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sidecar_path(target: Path) -> Path:
    """Return the conventional ``<target>.sha256`` sidecar path."""

    return target.with_name(target.name + ".sha256")


def render_sidecar(target: Path, *, root: Path | None = None) -> str:
    """Render the sidecar text for ``target``.

    The relative path is computed against ``root`` when supplied, otherwise
    against the artifact's parent directory. The format mirrors
    ``sha256sum`` so reviewers can run ``sha256sum -c <sidecar>``.
    """

    digest = sha256_file(target)
    base = root if root is not None else target.parent
    relative = target.resolve().relative_to(base.resolve())
    return f"{digest}  {relative.as_posix()}\n"


def write_sidecar(target: Path, *, root: Path | None = None) -> Path:
    """Write the sidecar text for ``target`` next to the artifact.

    The artifact is read fully (and hashed) before the sidecar is written,
    so the helper never embeds a digest inside the hashed file. Existing
    sidecars are overwritten with the deterministic canonical text.
    """

    sidecar = sidecar_path(target)
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(render_sidecar(target, root=root), encoding="utf-8")
    return sidecar


def verify_sidecar(target: Path, *, root: Path | None = None) -> tuple[bool, str]:
    """Return ``(ok, message)`` for the sidecar that accompanies ``target``.

    A missing sidecar, an unexpected digest, or an unexpected relative path
    all fail closed. The check is intentionally byte-for-byte so a
    whitespace or line-ending drift is reported.
    """

    sidecar = sidecar_path(target)
    if not target.is_file():
        return False, f"artifact is missing: {target}"
    if not sidecar.is_file():
        return False, f"sidecar is missing: {sidecar}"
    expected = render_sidecar(target, root=root)
    actual = sidecar.read_text(encoding="utf-8")
    if actual != expected:
        return False, f"sidecar mismatch: {sidecar}"
    return True, f"sidecar verified: {sidecar}"
