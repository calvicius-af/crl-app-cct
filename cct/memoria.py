"""A memória deste processo, em MB, em Linux, macOS e Windows, só com a biblioteca padrão.

Serve o gate de desempenho (#26, o pico) e o limite de memória da extração
(#25, a memória atual, vigiada durante a conversão). As estações do CRL são
Windows, onde o módulo `resource` não existe: aí os números vêm de
`GetProcessMemoryInfo`, com os tipos Win32 declarados (sem eles, o
identificador do processo, de 64 bits, ia como int de 32 e dava
OverflowError — revisão do PR #94).
"""
from __future__ import annotations

import os
import subprocess
import sys


def _contadores_windows():
    import ctypes
    from ctypes import wintypes

    class Contadores(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.K32GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(Contadores), wintypes.DWORD]
    kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
    contadores = Contadores()
    contadores.cb = ctypes.sizeof(contadores)
    if not kernel32.K32GetProcessMemoryInfo(kernel32.GetCurrentProcess(),
                                            ctypes.byref(contadores), contadores.cb):
        raise OSError(ctypes.get_last_error(),
                      "GetProcessMemoryInfo falhou")
    return contadores


def pico_mb() -> float:
    """A memória máxima que este processo usou até agora (o Linux dá KB, o macOS bytes)."""
    if sys.platform.startswith("win"):
        return _contadores_windows().PeakWorkingSetSize / (1024 * 1024)
    import resource
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return pico / (1024 * 1024) if sys.platform == "darwin" else pico / 1024


def atual_mb() -> float:
    """A memória residente deste processo agora.

    No Windows, o conjunto de trabalho; no Linux, `/proc/self/statm`; no macOS,
    que não tem nenhum dos dois na biblioteca padrão, o `ps` do sistema.
    """
    if sys.platform.startswith("win"):
        return _contadores_windows().WorkingSetSize / (1024 * 1024)
    if os.path.exists("/proc/self/statm"):
        with open("/proc/self/statm") as f:
            residentes = int(f.read().split()[1])
        return residentes * os.sysconf("SC_PAGE_SIZE") / (1024 * 1024)
    saida = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())],
                           capture_output=True, text=True, check=True).stdout
    return int(saida.strip()) / 1024
