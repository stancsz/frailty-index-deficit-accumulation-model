"""Privacy-safe identity for the installed serving process."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import PackageNotFoundError, distribution, distributions
import os
from pathlib import Path
import re
import sys
from typing import Mapping


PROJECT_DISTRIBUTION = "frailty-index-deficit-accumulation-model"
RUNTIME_ENVIRONMENT_NAMES = (
    "FRAILTY_API_KEY",
    "FRAILTY_MAX_REQUEST_BYTES",
    "FRAILTY_MODEL_PATH",
    "FRAILTY_MODEL_APPROVAL_PATH",
    "FRAILTY_REFERENCE_PANEL_PATH",
    "FRAILTY_REQUIRE_PRODUCTION",
)
_DEFAULT_MAX_REQUEST_BYTES = 64 * 1024
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _package_tree_manifest() -> list[tuple[str, str]] | None:
    """Hash the installed distribution files without exposing their paths.

    This is deliberately called a package-tree digest rather than a wheel hash:
    an already-installed process does not retain the wheel archive. It still
    binds the serving process to the bytes and relative file names resolved by
    the installed distribution, and returns ``None`` when that evidence cannot
    be established (for example, a broken editable installation).
    """

    try:
        installed = distribution(PROJECT_DISTRIBUTION)
    except PackageNotFoundError:
        return None
    files = installed.files
    if not files:
        return _source_package_manifest()
    manifest: list[tuple[str, str]] = []
    for package_path in files:
        path = Path(package_path.locate())
        try:
            if not path.is_file():
                return _source_package_manifest()
            relative_name = package_path.as_posix()
            manifest.append((relative_name, _sha256_bytes(path.read_bytes())))
        except OSError:
            return _source_package_manifest()
    return sorted(manifest)


def _source_package_manifest() -> list[tuple[str, str]] | None:
    """Provide a bounded source-tree fallback for editable/source execution."""

    package_root = Path(__file__).resolve().parent
    try:
        source_files = sorted(package_root.rglob("*.py"))
        if not source_files:
            return None
        return sorted(
            (
                f"frailty_engine/{path.relative_to(package_root).as_posix()}",
                _sha256_bytes(path.read_bytes()),
            )
            for path in source_files
        )
    except OSError:
        return None


def package_tree_sha256() -> str | None:
    """Return a deterministic digest of the installed project distribution."""

    manifest = _package_tree_manifest()
    if manifest is None:
        return None
    encoded = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def package_installation_mode() -> str:
    """Describe whether the digest came from an installed distribution."""

    try:
        installed = distribution(PROJECT_DISTRIBUTION)
        files = installed.files
        if files and all(Path(item.locate()).is_file() for item in files):
            return "installed_distribution"
    except (OSError, PackageNotFoundError):
        pass
    return "source_tree" if _source_package_manifest() is not None else "unavailable"


def dependency_set_sha256() -> str:
    """Return a stable digest of installed distribution names and versions."""

    entries = sorted(
        (
            _canonical_distribution_name(name),
            str(installed.version),
        )
        for installed in distributions()
        if (name := installed.metadata.get("Name"))
    )
    encoded = json.dumps(entries, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _boolean_config_value(raw: str | None) -> bool | str:
    if raw is None:
        return False
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return f"invalid:{_sha256_bytes(raw.encode('utf-8'))}"


def _configuration_snapshot(
    environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if environment is None else environment
    snapshot: dict[str, object] = {}
    for name in RUNTIME_ENVIRONMENT_NAMES:
        raw = values.get(name)
        if name == "FRAILTY_API_KEY":
            # Never hash or retain a credential. Authentication presence is the
            # only property that affects the serving contract here.
            snapshot[name] = {"configured": bool(raw)}
        elif name.endswith("_PATH"):
            snapshot[name] = {
                "configured": bool(raw),
                "value_sha256": (
                    _sha256_bytes(raw.encode("utf-8")) if raw is not None else None
                ),
            }
        elif name == "FRAILTY_MAX_REQUEST_BYTES":
            if raw is None:
                snapshot[name] = _DEFAULT_MAX_REQUEST_BYTES
            else:
                try:
                    snapshot[name] = int(raw)
                except ValueError:
                    snapshot[name] = f"invalid:{_sha256_bytes(raw.encode('utf-8'))}"
        elif name == "FRAILTY_REQUIRE_PRODUCTION":
            snapshot[name] = _boolean_config_value(raw)
    return snapshot


def configuration_sha256(
    environment: Mapping[str, str] | None = None,
) -> str:
    """Digest only the effective, non-secret runtime configuration shape."""

    encoded = json.dumps(
        _configuration_snapshot(environment), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def runtime_provenance(
    *, environment: Mapping[str, str] | None = None
) -> dict[str, object]:
    """Return non-secret process/build identity suitable for health metadata."""

    version = sys.version_info
    return {
        "package_tree_sha256": package_tree_sha256(),
        "package_installation_mode": package_installation_mode(),
        "dependency_set_sha256": dependency_set_sha256(),
        "python_runtime": {
            "implementation": sys.implementation.name,
            "version": f"{version.major}.{version.minor}.{version.micro}",
            "cache_tag": sys.implementation.cache_tag,
        },
        "configuration_sha256": configuration_sha256(environment),
    }


def provenance_is_well_formed(provenance: Mapping[str, object]) -> bool:
    """Return whether the runtime identity is structurally well-formed."""

    package_digest = provenance.get("package_tree_sha256")
    installation_mode = provenance.get("package_installation_mode")
    dependency_digest = provenance.get("dependency_set_sha256")
    configuration_digest = provenance.get("configuration_sha256")
    python_runtime = provenance.get("python_runtime")
    return bool(
        isinstance(package_digest, str)
        and _SHA256_PATTERN.fullmatch(package_digest)
        and installation_mode in {"installed_distribution", "source_tree"}
        and isinstance(dependency_digest, str)
        and _SHA256_PATTERN.fullmatch(dependency_digest)
        and isinstance(configuration_digest, str)
        and _SHA256_PATTERN.fullmatch(configuration_digest)
        and isinstance(python_runtime, Mapping)
        and all(
            isinstance(python_runtime.get(field), str)
            and bool(python_runtime.get(field))
            for field in ("implementation", "version", "cache_tag")
        )
    )


def provenance_is_installed(provenance: Mapping[str, object]) -> bool:
    """Return whether package identity came from complete distribution files."""

    return provenance.get("package_installation_mode") == "installed_distribution"


def provenance_is_ready_for_strict_admission(
    provenance: Mapping[str, object],
) -> bool:
    """Return whether a well-formed identity is backed by installed files."""

    return provenance_is_well_formed(provenance) and provenance_is_installed(provenance)
