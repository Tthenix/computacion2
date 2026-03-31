#!/usr/bin/env python3
"""
inspector.py: Una herramienta para extraer metadatos detallados de archivos en Linux.
"""

import os
import stat
import argparse
import datetime
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Módulos Unix-only (manejados con fallback para robustez)
try:
    import pwd
    import grp
except ImportError:
    pwd = None  # type: ignore
    grp = None  # type: ignore


def formatear_permisos(modo: int) -> str:
    """Convierte el modo decimal a un string tipo 'rwxr-xr-x'."""
    caracteres = ["-", "r", "w", "x"]
    res = ""
    # Permisos de dueño, grupo y otros (3 bits cada uno)
    for i in range(2, -1, -1):
        perm = (modo >> (i * 3)) & 0o7
        res += caracteres[1] if perm & 4 else caracteres[0]
        res += caracteres[2] if perm & 2 else caracteres[0]
        res += caracteres[3] if perm & 1 else caracteres[0]
    return res


def formatear_tamano(n_bytes: int) -> str:
    """Convierte bytes a formato humano (KB, MB, GB)."""
    for unidad in ["B", "KB", "MB", "GB", "TB"]:
        if n_bytes < 1024:
            return f"{n_bytes:.2f} {unidad}" if unidad != "B" else f"{n_bytes} B"
        n_bytes //= 1024
    return f"{n_bytes} PB"


def obtener_identidad(uid: int, gid: int) -> tuple[str, str]:
    """Resuelve UID/GID a nombres de usuario/grupo si el sistema lo permite."""
    usuario = str(uid)
    grupo = str(gid)

    if pwd:
        try:
            usuario = f"{pwd.getpwuid(uid).pw_name} (uid: {uid})"
        except KeyError:
            pass
    if grp:
        try:
            grupo = f"{grp.getgrgid(gid).gr_name} (gid: {gid})"
        except KeyError:
            pass

    return usuario, grupo


def detectar_tipo(ruta: Path, metadata: os.stat_result) -> str:
    """Identifica el tipo de archivo y detalles adicionales (ej: symlinks)."""
    modo = metadata.st_mode
    if stat.S_ISLNK(modo):
        try:
            destino = os.readlink(ruta)
            return f"enlace simbólico -> {destino}"
        except OSError:
            return "enlace simbólico (roto)"
    elif stat.S_ISDIR(modo):
        return "directorio"
    elif stat.S_ISCHR(modo):
        return "dispositivo de caracteres"
    elif stat.S_ISBLK(modo):
        return "dispositivo de bloques"
    elif stat.S_ISFIFO(modo):
        return "tubería (FIFO)"
    elif stat.S_ISSOCK(modo):
        return "socket"
    return "archivo regular"


def inspeccionar(path_str: str) -> None:
    """Extrae y muestra los metadatos de la ruta especificada."""
    p = Path(path_str)
    if not p.exists() and not p.is_symlink():
        print(f"Error: No se pudo encontrar '{path_str}'", file=sys.stderr)
        sys.exit(1)

    # Nota: usamos lstat para no seguir symlinks y ver sus propios metadatos
    try:
        metadata = p.lstat()
    except OSError as e:
        print(f"Error al acceder a '{path_str}': {e.strerror}", file=sys.stderr)
        sys.exit(1)

    tipo = detectar_tipo(p, metadata)
    permisos_str = formatear_permisos(metadata.st_mode)
    permisos_oct = oct(metadata.st_mode & 0o777)[2:]
    usr, grp_name = obtener_identidad(metadata.st_uid, metadata.st_gid)

    print(f"Archivo: {p.absolute()}")
    print(f"Tipo: {tipo}")
    print(f"Tamaño: {formatear_tamano(metadata.st_size)}")
    print(f"Permisos: {permisos_str} ({permisos_oct})")
    print(f"Propietario: {usr}")
    print(f"Grupo: {grp_name}")
    print(f"Inodo: {metadata.st_ino}")
    print(f"Enlaces duros: {metadata.st_nlink}")

    # Timestamps
    fmt_time = lambda t: datetime.datetime.fromtimestamp(t).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(f"Última modificación: {fmt_time(metadata.st_mtime)}")
    print(f"Último acceso: {fmt_time(metadata.st_atime)}")

    if p.is_dir():
        try:
            elementos = len(list(p.iterdir()))
            print(f"Contenido: {elementos} elementos")
        except PermissionError:
            print("Contenido: [Permiso denegado]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspector de metadatos de archivos (Linux)."
    )
    parser.add_argument("ruta", help="Ruta del archivo o directorio a inspeccionar.")
    args = parser.parse_args()
    inspeccionar(args.ruta)


if __name__ == "__main__":
    main()
