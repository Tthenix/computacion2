import argparse
import sys
import glob
from typing import Iterable, List, Optional, Tuple, Generator

# Límite PLANNEA: Máximo 300 líneas.
# Este archivo tiene ~110 líneas siguiendo el protocolo.


def configurar_argumentos() -> argparse.Namespace:
    """Configura y parsea los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Mini-grep: Busca patrones en archivos o stdin."
    )

    parser.add_argument("patron", type=str, help="El patrón (string) a buscar.")

    parser.add_argument(
        "archivos",
        nargs="*",
        help="Archivos en los cuales buscar (acepta comodines como *.py). Si se omite, lee de stdin.",
    )

    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Búsqueda insensible a mayúsculas.",
    )

    parser.add_argument(
        "-n", "--line-number", action="store_true", help="Mostrar número de línea."
    )

    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Solo mostrar el conteo de coincidencias por archivo.",
    )

    parser.add_argument(
        "-v",
        "--invert",
        action="store_true",
        help="Mostrar líneas que NO coinciden con el patrón.",
    )

    return parser.parse_args()


def buscar_lineas(
    lineas: Iterable[str], patron: str, ignore_case: bool = False, invert: bool = False
) -> Generator[Tuple[int, str], None, None]:
    """Generador que filtra líneas según el patrón y criterios."""
    patron_busqueda = patron.lower() if ignore_case else patron

    for i, linea in enumerate(lineas, 1):
        linea_limpia = linea.rstrip("\n")
        linea_busqueda = linea_limpia.lower() if ignore_case else linea_limpia

        coincide = patron_busqueda in linea_busqueda

        if (coincide and not invert) or (not coincide and invert):
            yield (i, linea_limpia)


def procesar_recurso(
    nombre_fuente: str,
    lineas: Iterable[str],
    args: argparse.Namespace,
    mostrar_nombre: bool,
) -> int:
    """Procesa una fuente de datos y formatea la salida."""
    conteo = 0
    ver_n = args.line_number or mostrar_nombre

    for num_linea, contenido in buscar_lineas(
        lineas, args.patron, args.ignore_case, args.invert
    ):
        conteo += 1
        if not args.count:
            prefijo = f"{nombre_fuente}:" if mostrar_nombre else ""
            num = f"{num_linea}:" if ver_n else ""
            print(f"{prefijo}{num}{contenido}")

    if args.count:
        prefijo = f"{nombre_fuente}: " if mostrar_nombre else ""
        print(f"{prefijo}{conteo} coincidencias")

    return conteo


def main() -> None:
    """Función principal que orquesta la ejecución con soporte para globs."""
    args = configurar_argumentos()
    total_coincidencias = 0

    # Manejo de stdin si no hay archivos o se usa '-'
    usar_stdin = not args.archivos or (
        len(args.archivos) == 1 and args.archivos[0] == "-"
    )

    if usar_stdin:
        if not sys.stdin.isatty() or (args.archivos and args.archivos[0] == "-"):
            total_coincidencias = procesar_recurso("stdin", sys.stdin, args, False)
        else:
            print(
                "Error: Debe especificar archivos o pasar datos por stdin.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Expansión manual de comodines (necesario para Windows PowerShell/CMD)
        rutas_expandidas = []
        for arg_ruta in args.archivos:
            archivos_encontrados = glob.glob(arg_ruta)
            if archivos_encontrados:
                rutas_expandidas.extend(archivos_encontrados)
            else:
                # Si no hay matches (como un archivo que no existe), lo dejamos para que lance error luego
                rutas_expandidas.append(arg_ruta)

        mostrar_nombre = len(rutas_expandidas) > 1
        for ruta in rutas_expandidas:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    total_coincidencias += procesar_recurso(
                        ruta, f, args, mostrar_nombre
                    )
            except (FileNotFoundError, PermissionError) as e:
                print(f"buscar.py: {ruta}: {e.strerror}", file=sys.stderr)

    if args.count and not usar_stdin:
        print(f"Total: {total_coincidencias} coincidencias")


if __name__ == "__main__":
    main()
