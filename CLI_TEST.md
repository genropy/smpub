# CLI Test Commands - smpub

Comandi pronti da copiare per testare il CLI di smpub.

## Setup Iniziale

```bash
# Vai nella directory del progetto
cd /Users/gporcari/Sviluppo/genro_ng/meta-genro-libs/sub-projects/smpub

# Installa in development mode (se non già fatto)
pip install -e .
```

## Test Registry System

### Registry Locale

```bash
# Registra l'app di esempio localmente
smpub add sample_app --path ./examples/sample_app

# Lista app registrate localmente
smpub list

# Verifica file .published creato
cat .published
```

### Registry Globale

```bash
# Registra globalmente
smpub add sample_app --path ./examples/sample_app --global

# Lista app globali
smpub list --global

# Verifica registry globale
cat ~/.smartlibs/publisher/registry.json
```

## Test CLI con Calculator Example

### Metodo 1: Via Registry (RACCOMANDATO)

```bash
# Registra l'app calculator
smpub add calculator --path ./examples

# Usa tramite smpub command
smpub calculator calc add 10 20

# Test con float
smpub calculator calc multiply 5.5 2.0

# Test con default value
smpub calculator calc multiply 5.5
```

### Metodo 2: Esecuzione Diretta (per testing/sviluppo)

```bash
# Vai nella directory examples
cd examples

# Test diretto (senza registry)
python calculator_http.py calc add 10 20

# Test con float
python calculator_http.py calc multiply 5.5 2.0

# Test con default value
python calculator_http.py calc multiply 5.5
```

## Test Interactive Mode (se gum installato)

```bash
# Installa gum (se non già installato)
brew install gum

# NOTA: In zsh, quota le parentesi quadre
pip install 'smpub[gum]'

# Test interactive
python calculator_http.py calc add --interactive

# Short form
python calculator_http.py calc multiply -i
```

## Test Type Validation

```bash
# Valid integers
python calculator_http.py calc add 10 20

# Invalid input (should show validation error)
python calculator_http.py calc add ten twenty

# Valid float
python calculator_http.py calc multiply 3.14 2

# Invalid float
python calculator_http.py calc multiply abc 2
```

## Test HTTP Mode

```bash
# Avvia server HTTP
python calculator_http.py

# In un altro terminale, testa con curl:
curl -X POST http://localhost:8000/calc/add \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 20}'

curl -X POST http://localhost:8000/calc/multiply \
  -H "Content-Type: application/json" \
  -d '{"x": 5.5, "y": 2.0}'

# Apri Swagger UI nel browser
open http://localhost:8000/docs
```

## Test con Sample App (se disponibile)

```bash
# Torna alla root
cd ..

# Esegui tramite registry
smpub sample_app <handler> <method> [args...]

# Lista metodi disponibili (se implementato)
smpub sample_app --help
```

## Test Error Handling

```bash
# App non registrata
smpub nonexistent_app handler method

# Registry vuoto
rm .published
smpub list

# Path inesistente
smpub add test --path /nonexistent/path

# Rimozione app non registrata
smpub remove nonexistent_app
```

## Cleanup

```bash
# Rimuovi da registry locale
smpub remove sample_app

# Rimuovi da registry globale
smpub remove sample_app --global

# Verifica rimozione
smpub list
smpub list --global

# Pulisci file temporanei
rm -f .published
```

## Debug Mode (se implementato)

```bash
# Con verbose output
smpub --verbose sample_app handler method

# Con debug mode
smpub --debug sample_app handler method
```

## Test Publisher API Introspection

```bash
# Se implementato get_api_json
python -c "
from examples.calculator_http import CalculatorApp
app = CalculatorApp()
import json
print(json.dumps(app.calc.publisher.get_api_json(), indent=2))
"
```

## Verifica Installazione

```bash
# Verifica comando smpub disponibile
which smpub

# Verifica versione
smpub --version

# Help generale
smpub --help

# Help per add command
smpub add --help
```

## Notes

- **Registry locale**: `.published` nella directory corrente
- **Registry globale**: `~/.smartlibs/publisher/registry.json`
- **HTTP mode**: Avvia server se nessun argomento CLI
- **CLI mode**: Avvia CLI se argomenti presenti
- **Interactive mode**: Richiede `gum` installato

## Troubleshooting

```bash
# Se smpub command non trovato
pip install -e .

# Se registry non funziona
rm -f .published ~/.smartlibs/publisher/registry.json

# Se HTTP mode non parte (NOTA: quota in zsh!)
pip install '.[http]'

# Se interactive mode non parte (NOTA: quota in zsh!)
pip install '.[gum]'

# Check Python path
python -c "import smpub; print(smpub.__file__)"

# Errore "zsh: no matches found" - SEMPRE quota le parentesi quadre in zsh
pip install 'smpub[http]'
pip install 'smpub[gum]'
pip install '.[dev]'
```
