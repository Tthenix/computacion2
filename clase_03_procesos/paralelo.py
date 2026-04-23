#!/usr/bin/env python3
"""
Ejecutor de comandos en paralelo usando primitives de SO.
"""
import os
import sys
import time
from typing import Dict


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} comando1 [comando2 ...]")
        sys.exit(1)

    comandos = sys.argv[1:]
    pids: Dict[int, str] = {}
    inicio = time.time()

    # 1. Lanzar todos los procesos
    for cmd_str in comandos:
        args = cmd_str.split()
        try:
            pid = os.fork()
            if pid == 0:
                # HIJO: Reemplaza su imagen con el comando
                try:
                    os.execvp(args[0], args)
                except FileNotFoundError:
                    print(f"Error: comando '{args[0]}' no encontrado")
                    sys.exit(1)
            else:
                # PADRE: Guarda el PID para rastrearlo
                pids[pid] = cmd_str
                print(f"[{pid}] Iniciado: {cmd_str}")
        except OSError as e:
            print(f"Error al crear proceso para '{cmd_str}': {e}")

    # 2. Esperar a que terminen y recolectar resultados
    exitosos = 0
    fallidos = 0
    while pids:
        try:
            pid, status = os.wait()
            cmd = pids.pop(pid)
            codigo = os.WEXITSTATUS(status)

            if codigo == 0:
                exitosos += 1
            else:
                fallidos += 1
            print(f"[{pid}] Terminado: {cmd} (código: {codigo})")
        except ChildProcessError:
            break

    final = time.time()
    duracion = final - inicio

    print(f"\nResumen:")
    print(f"- Comandos ejecutados: {len(comandos)}")
    print(f"- Exitosos: {exitosos}")
    print(f"- Fallidos: {fallidos}")
    print(f"- Tiempo total: {duracion:.2f}s")


if __name__ == "__main__":
    main()
