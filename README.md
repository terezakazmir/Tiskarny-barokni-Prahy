# Tiskárny barokní Prahy
Tato interaktivní aplikace vznikla jako součást výzkumné části diplomové práce s názvem "Pražský barokní knihtisk pohledem digital humanities: efektivní využití dat o tiskařské produkci na území Prahy mezi lety 1621–1748". Obsahuje mapový nástroj určený k vizualizaci a analýze umístění pražských barokních tiskáren a grafový nástroj, který je možné využít k analýze dat o vydáních v Praze mezi lety 1621–1748 získaných z Bibliografické databáze bohemikálních tisků, rukopisů a moderní literatury.

## Instrukce ke spuštění aplikace
Otevřete terminál a naklonujte tento repozitář:
```bash
git clone https://github.com/terezakazmir/Tiskarny-barokni-Prahy.git
cd Tiskarny-barokni-Prahy
```
Další kroky závisí na tom, zda chcete aplikaci spustit v Dockeru nebo bez něj.

### Docker
Nainstalujte [Docker Desktop](https://docs.docker.com/desktop/) a spusťte aplikaci pomocí příkazu:
```bash
docker compose up
```

### Lokálni instalace
Vytvořte a aktivujte virtuální prostředí:

**`Windows (Příkazový řádek):`**
```ps1
python -m venv venv
venv\Scripts\activate
```
**`Windows (PowerShell):`**
```ps1
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**`Linux:`**
```ps1
python -m venv venv
source venv/bin/activate
```

Nainstalujte potřebné knihovny ze souboru `requirements.txt`:
```bash
pip install -r requirements.txt
```
Spusťte aplikaci:
```bash
python app.py
```

### Zobrazení aplikace

V obou případech se v terminálu zobrazí URL, na které bude aplikace dostupná. Standardně bude aplikace běžet na [http://127.0.0.1:8050/](http://127.0.0.1:8050/).


Aplikace dovoluje změnit pouzitý port a hostname pomocí argumentů `--port` a `--host`:

```bash
python app.py --port 8050 --host 0.0.0.0
```

Pro změnu portu a hostname při spuštení pomocí `docker compose` upravte sekci `command` v souboru `docker-compose.yaml`.
