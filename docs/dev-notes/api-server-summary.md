# Riepilogo Lavoro API Server e ApiSwitcher

## 1. Richieste Principali dell'Utente

1. **Implementare ApiSwitcher** per risolvere il problema dell'OpenAPI schema che non mostrava i parametri in Swagger UI
2. **Rendere ApiSwitcher obbligatorio** per l'esposizione HTTP/OpenAPI con messaggio di errore chiaro
3. **Creare pagina HTML home** con link cliccabili a Swagger UI, ReDoc e OpenAPI JSON
4. **Aggiungere comando `serve` al CLI** per avviare il server HTTP con sintassi: `smpub <appname> serve [port]`
5. **Sospendere il lavoro su interactive** (migrazione Textual) e concentrarsi sul ramo API server

## 2. Concetti Tecnici Chiave

- **ApiSwitcher**: Estensione di smartswitch.Switcher che crea modelli Pydantic al momento della decorazione
- **Decoration-time Model Creation**: I modelli Pydantic vengono creati quando la classe viene definita, non a runtime
- **FastAPI Introspection**: FastAPI usa l'introspezione dei type hints per generare lo schema OpenAPI
- **Pydantic Model Storage**: I modelli vengono salvati in `_pydantic_models` dict e recuperati con `get_pydantic_model()`
- **Enum Conversion**: I tipi `Literal` vengono convertiti in Enum per Pydantic
- **Closure Pattern**: Uso di closure con type annotations invece di exec() per creare endpoint
- **OpenAPI Schema Customization**: Schema OpenAPI personalizzato per gestire modelli dinamici
- **CLI Command Routing**: Pattern per aggiungere comandi al CLI mantenendo retrocompatibilità

## 3. File e Sezioni di Codice Modificati

### `src/smpub/apiswitcher.py`
**Importanza**: Classe fondamentale che risolve il problema OpenAPI creando modelli Pydantic al momento della decorazione.

**Codice chiave**:
```python
class ApiSwitcher(Switcher):
    """Switcher that automatically creates Pydantic models for decorated methods."""

    def __init__(self, prefix: str = ''):
        super().__init__(prefix=prefix)
        self._pydantic_models: dict[str, Any] = {}

    def __call__(self, func):
        """Decorate method and create Pydantic model."""
        decorated = super().__call__(func)
        if create_model is not None:
            model = self._create_pydantic_model(func)
            if model is not None:
                self._pydantic_models[func.__name__] = model
        return decorated

    def get_pydantic_model(self, method_name: str) -> Optional[Any]:
        """Get Pydantic model for a method."""
        return self._pydantic_models.get(method_name)
```

### `src/smpub/api_server.py`
**Importanza**: Integrazione FastAPI che usa ApiSwitcher e genera l'OpenAPI schema corretto.

**Modifiche principali**:
1. **Check obbligatorio ApiSwitcher** (righe 89-96)
2. **Recupero modelli pre-creati** (riga 99)
3. **Endpoint con closure** (righe 130-152)
4. **Homepage HTML** (righe 225-321)

### `src/smpub/cli.py`
**Importanza**: Aggiunto comando `serve` per avviare HTTP server dalla CLI.

**Modifiche** (righe 252-268):
```python
# Check if next argument is 'serve'
if len(sys.argv) >= 3 and sys.argv[2] == "serve":
    # HTTP mode: smpub <appname> serve [port]
    port = 8000  # default port
    if len(sys.argv) >= 4:
        try:
            port = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid port number '{sys.argv[3]}'")
            sys.exit(1)

    # Run in HTTP mode with specified port
    print(f"Starting {app_name} on http://0.0.0.0:{port}")
    print(f"Swagger UI available at http://localhost:{port}/docs")
    print(f"ReDoc available at http://localhost:{port}/redoc")
    app.run(mode="http", port=port)
    return
```

### `src/smpub/validation.py`
**Importanza**: Spostata funzione `parse_docstring_params` qui per risolvere import circolare.

### `examples/mail_app/main.py`
**Importanza**: Esempio aggiornato per usare ApiSwitcher.

**Modifiche**:
```python
from smartpublisher.apiswitcher import ApiSwitcher

class AccountHandler(PublishedClass):
    api = ApiSwitcher(prefix='account_')  # Era: Switcher

class MailHandler(PublishedClass):
    api = ApiSwitcher(prefix='mail_')  # Era: Switcher
```

### `src/smpub/__init__.py`
**Modifiche**: Aggiunto ApiSwitcher agli export.

## 4. Problemi Risolti

1. ✅ **OpenAPI Schema Parametri Invisibili**: Risolto con ApiSwitcher che crea modelli al decoration time
2. ✅ **Uso exec()**: Sostituito con pattern closure + type annotations
3. ✅ **ApiSwitcher Non Obbligatorio**: Aggiunto check TypeError con messaggio esplicativo
4. ✅ **Import Circolare**: Risolto spostando funzione condivisa in validation.py
5. ✅ **Homepage Testuale**: Sostituita con HTML elegante con link cliccabili
6. ✅ **Avvio Server Manuale**: Aggiunto comando `smpub <app> serve [port]`

## 5. Task Pendenti

### Task Sospesi (da non fare ora):
- ❌ Aggiornare `test_interactive.py` per Textual (12 test falliti)
- ❌ Aggiornare documentazione da questionary a Textual

### Task da Considerare:
- Verificare pytest su tutto il progetto prima di commit
- Eseguire ruff check
- Scrivere test per ApiSwitcher
- Scrivere test per comando `serve`
- Aggiornare documentazione con esempi di ApiSwitcher

## 6. Comando per Ripartire

Per continuare il lavoro in una nuova sessione Claude:

```bash
# Naviga nella directory del progetto
cd /Users/gporcari/Sviluppo/genro_ng/meta-genro-libs/sub-projects/smpub

# Leggi questo documento di riepilogo
cat RIEPILOGO_API_SERVER.md

# Verifica stato git
git status

# Controlla che i file chiave esistano
ls -la src/smpub/api_server.py src/smpub/apiswitcher.py

# Testa il comando serve
smpub mailapp serve 8084
```

**Contesto da fornire a Claude**:
"Sto continuando il lavoro su smpub. Ho implementato ApiSwitcher per risolvere i problemi OpenAPI e aggiunto il comando `serve` al CLI. Leggi il file RIEPILOGO_API_SERVER.md per il contesto completo."

**File chiave da leggere per il contesto**:
1. [src/smpub/api_server.py](src/smpub/api_server.py) - Integrazione FastAPI
2. [src/smpub/apiswitcher.py](src/smpub/apiswitcher.py) - Classe core per modelli Pydantic
3. [src/smpub/cli.py](src/smpub/cli.py) - Comando serve
4. [examples/mail_app/main.py](examples/mail_app/main.py) - Esempio di utilizzo
5. [CLAUDE.md](CLAUDE.md) - Regole workflow

## 7. Stato Corrente

**Branch**: main
**Ultimo test eseguito**:
```bash
smpub mailapp serve 8084
# ✅ Funzionante - server avviato su porta 8084
# ✅ Homepage HTML con link funzionanti
# ✅ Swagger UI accessibile
# ✅ Schema OpenAPI mostra correttamente i parametri
```

**Prossimi step suggeriti**:
1. Eseguire `pytest` per verificare regressioni
2. Eseguire `ruff check .` per code quality
3. Committare il lavoro API server
4. Eventualmente riprendere lavoro su Textual (test_interactive.py)

---

**Data**: 2025-11-10
**Ultima modifica**: Implementazione comando `serve` completata
