# Demo Shop - smpub Example Application

Questo è l'esempio completo che dimostra come usare **smpub** per pubblicare un'applicazione Python come CLI/HTTP API.

## Struttura

```
demo_shop/
├── sample_shop/       # 📦 Libreria Python standalone
│   ├── sql/          # Sistema database generico
│   ├── tables/       # Manager per articoli, acquisti, ecc.
│   ├── shop.py       # Classe principale Shop
│   ├── example_*.py  # Esempi di uso diretto Python
│   └── test_*.py     # Tests
│
└── published_shop/    # 🚀 App pubblicata con smpub
    ├── main.py       # Publisher che espone Shop via CLI/HTTP
    ├── populate_db.py # Script per popolare il database
    └── shop.db       # Database SQLite
```

## Punti Chiave

### 1. Separazione di Responsabilità

- **sample_shop**: Libreria Python pura, senza dipendenze da smpub
  - Può essere usata direttamente (vedi `example_pythonic.py`)
  - Ha i suoi test, documentazione, esempi
  - Non sa nulla di CLI o HTTP

- **published_shop**: Layer sottile che usa smpub per esporre sample_shop
  - Importa Shop da sample_shop
  - La pubblica tramite smpub Publisher
  - Fornisce CLI e HTTP API automaticamente

### 2. Filosofia "Thin Publishing Layer"

smpub non è un framework intrusivo:
- La tua libreria rimane indipendente
- smpub aggiunge solo CLI/HTTP layer
- Puoi usare la libreria anche senza smpub

## Come Usare

### Usa sample_shop direttamente (Python puro)

```python
from examples.demo_shop.sample_shop.shop import Shop

# Istanzia e usa normalmente
shop = Shop("sqlite:myshop.db")
shop.db.table("types").add(name="electronics", description="Electronic devices")
```

Vedi `sample_shop/example_pythonic.py` per un esempio completo.

### Usa published_shop (CLI/HTTP)

```bash
# Popola il database
cd examples/demo_shop/published_shop
python populate_db.py

# Avvia il server HTTP
python main.py
```

Poi apri il browser:
- http://localhost:8000/ - Homepage con link alla documentazione
- http://localhost:8000/docs - Swagger UI interattivo
- http://localhost:8000/types/list?format=markdown_html - Lista tipi in markdown renderizzato

## Formati Supportati

Tutti i metodi `list()` supportano il parametro `format`:

- `json` - Risposta JSON (default)
- `markdown` - Tabella Markdown (testo)
- `html` - Tabella HTML (testo)
- `table` - Tabella ASCII (testo)
- `markdown_html` - Markdown renderizzato nel browser con marked.js + mermaid.js

Esempio:
```bash
# JSON
curl http://localhost:8000/articles/list

# Markdown renderizzato nel browser
curl http://localhost:8000/articles/list?format=markdown_html
```

## Features Dimostrate

### SmartSwitch
- Plugin chain (logging → pydantic → dbop)
- Validazione automatica parametri con Pydantic
- Gestione transazioni database automatica

### smpub Publisher
- Pubblicazione automatica di classi Python
- Generazione CLI/HTTP da switcher
- OpenAPI/Swagger automatico
- Supporto per metodi sync/async

### SQL Database System
- Adapter pattern per SQLite/PostgreSQL
- Table managers con CRUD operations
- Query builder con supporto transazioni
- Connection pooling thread-safe

## File Importanti

| File | Descrizione |
|------|-------------|
| `sample_shop/shop.py` | Classe principale Shop |
| `sample_shop/sql/table.py` | Classe base per table managers |
| `sample_shop/tables/*.py` | Manager per articoli, acquisti, ecc. |
| `published_shop/main.py` | Publisher smpub |
| `sample_shop/example_pythonic.py` | Esempio uso Python puro |

## Prossimi Passi

1. Esplora `sample_shop/example_pythonic.py` per vedere l'uso Python puro
2. Guarda `sample_shop/tables/*.py` per vedere i table managers
3. Leggi `published_shop/main.py` per capire il publisher pattern
4. Avvia il server e sperimenta con Swagger UI
5. Prova i diversi formati di output
