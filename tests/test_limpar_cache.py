from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.limpar_cache import candidatos


def test_candidatos_limita_a_cache_antiga(tmp_path):
    cache = tmp_path / "data" / "interim" / "cache_modelo"
    cache.mkdir(parents=True)
    antigo = cache / "antigo.json"
    antigo.write_text("x", encoding="utf-8")
    recente = cache / "recente.json"
    recente.write_text("x", encoding="utf-8")
    interm = tmp_path / "data" / "interim" / "docs" / "preservar.txt"
    interm.parent.mkdir(parents=True)
    interm.write_text("x", encoding="utf-8")

    data_antiga = (datetime.now(timezone.utc) - timedelta(days=31)).timestamp()
    import os
    os.utime(antigo, (data_antiga, data_antiga))

    assert candidatos(tmp_path, 30) == [antigo]
