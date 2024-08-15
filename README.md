# Tiskárny barokní Prahy
Tato interaktivní aplikace vznikla jako součást výzkumné části diplomové práce s názvem "Pražský barokní knihtisk pohledem digital humanities: efektivní využití dat o tiskařské produkci na území Prahy mezi lety 1621–1748". Obsahuje mapový nástroj určený k vizualizaci a analýze umístění pražských barokních tiskáren a grafový nástroj, který je možné využít k analýze dat o vydáních v Praze mezi lety 1621–1748 získaných z Bibliografické databáze bohemikálních tisků, rukopisů a moderní literatury.

## Instrukce ke spuštění aplikace
Otevřete terminál a naklonujte tento repozitář:
```bash
git clone https://github.com/terezakazmir/Tiskarny-barokni-Prahy.git
cd Tiskarny-barokni-Prahy
```
Vytvořte a aktivujte virtuální prostředí:

**`Windows:`**
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
Otevřete zobrazené URL. Standardně bude aplikace běžet na [http://127.0.0.1:8050/](http://127.0.0.1:8050/).
