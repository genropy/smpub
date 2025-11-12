# Design Evolution - Shop Database Operations

Questo documento traccia l'evoluzione del design delle operazioni database dal pattern iniziale fino all'implementazione finale con DbopPlugin.

## Fase 0: Versione Iniziale (Prima della Discussione)

**Problema**: Ogni metodo gestiva autonomamente connection e commit.

```python
class ArticleTypes:
    def add(self, name: str, description: str = "") -> dict:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check duplicati
            cursor.execute("SELECT id FROM article_types WHERE name = ?", (name,))
            if cursor.fetchone():
                return {"success": False, "error": "already exists"}

            # Insert
            cursor.execute(
                "INSERT INTO article_types (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()  # ← Commit immediato

            return {"success": True, "id": cursor.lastrowid}
```

**Limitazioni**:
- ❌ Impossibile fare transazioni atomiche multiple
- ❌ Ogni metodo fa il proprio commit
- ❌ Non thread-safe per transazioni complesse

## Fase 1: Identificazione del Problema Transazionale

**Osservazione chiave**: Se vuoi fare operazioni atomiche su tabelle diverse, non puoi perché ogni metodo fa il proprio commit:

```python
# PROBLEMA: Operazioni NON atomiche
shop.types.add("electronics", "Electronics")      # ← commit!
shop.articles.add(1, "LAPTOP", "...", 999.00)     # ← commit!
shop.purchases.add(1, 5)                           # ← commit!
# Se la terza fallisce, le prime due sono già committate! 💥
```

**Domanda posta**: "però se io volessi fare due add in una tabella e un add in un'altra poi un remove in una terza mica voglio i commit"

## Fase 2: Connection Manager Centralizzato

**Soluzione proposta**: Shop gestisce le connection per thread, le classi chiedono alla shop la connection corrente.

```python
import threading

class Shop:
    def __init__(self):
        self._thread_local = threading.local()
        self.types = ArticleTypes(self)  # ← Passa self!
        self.articles = Articles(self)
        self.purchases = Purchases(self)

    @property
    def current_connection(self):
        """Get or create connection for current thread."""
        if not hasattr(self._thread_local, 'conn') or self._thread_local.conn is None:
            self._thread_local.conn = get_connection().__enter__()
            self._thread_local.owns_conn = True
        return self._thread_local.conn

    def commit(self):
        """Commit current connection."""
        if hasattr(self._thread_local, 'conn') and self._thread_local.conn:
            self._thread_local.conn.commit()

class ArticleTypes:
    def __init__(self, shop):
        self.shop = shop  # ← Riferimento a Shop

    def add(self, name: str, description: str = "", autocommit: bool = True) -> dict:
        conn = self.shop.current_connection  # ← Chiede a Shop
        cursor = conn.cursor()

        # Business logic...

        if autocommit:
            self.shop.commit()  # ← Commit centralizzato

        return result
```

**Vantaggi**:
- ✅ Connection thread-safe
- ✅ Controllo transazionale con `autocommit` parameter
- ✅ Shop gestisce il lifecycle

**Uso**:
```python
# Modalità normale (autocommit)
shop.types.add("electronics")

# Modalità transazionale
shop.types.add("electronics", autocommit=False)
shop.articles.add(1, "LAPTOP", ..., autocommit=False)
shop.commit()  # Un solo commit!
```

## Fase 3: Aggiunta di Switcher (SmartSwitch)

**Motivazione**: Le classi devono usare Switcher per:
- Validazione automatica con PydanticPlugin
- Enumerazione dei metodi per CLI/HTTP
- Call-by-name dispatch

```python
from smartswitch import Switcher

class ArticleTypes:
    dbop = Switcher(name="types")  # ← Switcher per DB operations

    def __init__(self, shop):
        self.shop = shop

    @dbop  # ← Decorato per essere un "metodo principale"
    def add(self, name: str, description: str = "", autocommit: bool = True) -> dict:
        conn = self.shop.current_connection
        cursor = conn.cursor()

        # PydanticPlugin valida automaticamente i parametri!
        # name: str → validato come stringa
        # description: str = "" → validato con default
        # autocommit: bool = True → validato come booleano

        cursor.execute("SELECT id FROM article_types WHERE name = ?", (name,))
        if cursor.fetchone():
            return {"success": False, "error": "exists"}

        cursor.execute(
            "INSERT INTO article_types (name, description) VALUES (?, ?)",
            (name, description)
        )

        if autocommit:
            self.shop.commit()

        return {"success": True, "id": cursor.lastrowid}
```

**Vantaggi**:
- ✅ Validazione automatica tipo con Pydantic
- ✅ Metodi enumerabili per CLI/API
- ✅ Nessun boilerplate di validazione manuale

## Fase 4: DbopPlugin - Transaction Management Automatico

**Insight**: L'handling di connection/commit/rollback è identico in ogni metodo → può essere un plugin!

```python
# dbop_plugin.py
from smartswitch.plugin import BasePlugin

class DbopPlugin(BasePlugin):
    """
    Plugin per operazioni database con gestione automatica di:
    - Connection via self.shop.current_connection
    - Commit automatico se autocommit=True
    - Rollback automatico su eccezione
    """

    def _wrap_handler(self, func, switcher):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler_instance = args[0]
            shop = handler_instance.shop

            # Get connection
            conn = shop.current_connection

            # Get autocommit parameter
            autocommit = kwargs.get('autocommit', True)

            try:
                # Call original function
                result = func(*args, **kwargs)

                # Auto-commit on success
                if autocommit:
                    shop.commit()

                return result

            except Exception:
                # Auto-rollback on error
                conn.rollback()
                raise

        return wrapper
```

**Uso con plugin**:
```python
class ArticleTypes:
    dbop = Switcher(name="types").plug(DbopPlugin())  # ← Plugin attivo!

    def __init__(self, shop):
        self.shop = shop

    @dbop
    def add(self, name: str, description: str = "", autocommit: bool = True) -> dict:
        conn = self.shop.current_connection
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM article_types WHERE name = ?", (name,))
        if cursor.fetchone():
            return {"success": False, "error": "exists"}

        cursor.execute(
            "INSERT INTO article_types (name, description) VALUES (?, ?)",
            (name, description)
        )

        # ← Niente più if autocommit / try-except!
        # ← Plugin gestisce commit/rollback automaticamente!

        return {"success": True, "id": cursor.lastrowid}
```

**Vantaggi**:
- ✅ Zero boilerplate per commit/rollback
- ✅ Gestione errori consistente
- ✅ Codice focalizzato sulla business logic

## Fase 5: Cursor Injection (Versione Finale)

**Insight finale**: Anche `conn.cursor()` è boilerplate ripetuto → il plugin può iniettare il cursor!

```python
class DbopPlugin(BasePlugin):
    def _wrap_handler(self, func, switcher):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler_instance = args[0]
            shop = handler_instance.shop

            conn = shop.current_connection
            autocommit = kwargs.get('autocommit', True)

            # ← INJECT CURSOR automaticamente!
            if 'cursor' not in kwargs or kwargs['cursor'] is None:
                kwargs['cursor'] = conn.cursor()

            try:
                result = func(*args, **kwargs)

                if autocommit:
                    shop.commit()

                return result
            except Exception:
                conn.rollback()
                raise

        return wrapper
```

**Metodo finale (massima semplicità)**:
```python
class ArticleTypes:
    dbop = Switcher(name="types").plug(DbopPlugin())

    def __init__(self, shop):
        self.shop = shop

    @dbop
    def add(self, name: str, cursor=None, autocommit: bool = True) -> dict:
        # cursor iniettato automaticamente dal plugin!

        cursor.execute("SELECT id FROM article_types WHERE name = ?", (name,))
        if cursor.fetchone():
            return {"success": False, "error": "exists"}

        cursor.execute(
            "INSERT INTO article_types (name, description) VALUES (?, ?)",
            (name, description)
        )

        return {"success": True, "id": cursor.lastrowid}
```

**Confronto Finale**:

```python
# FASE 0 (iniziale) - 15 righe
def add(self, name: str) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ...")
        if cursor.fetchone():
            return {"error": ...}
        cursor.execute("INSERT ...")
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}

# FASE 5 (finale) - 7 righe
@dbop
def add(self, name: str, cursor=None, autocommit: bool = True) -> dict:
    cursor.execute("SELECT ...")
    if cursor.fetchone():
        return {"error": ...}
    cursor.execute("INSERT ...")
    return {"success": True, "id": cursor.lastrowid}
```

**Risparmio**:
- **8 righe di boilerplate eliminate** per metodo
- **×30+ metodi** = ~240 righe risparmiate
- **Più importante**: Codice focalizzato sulla business logic

## Vantaggi Architetturali della Soluzione Finale

### 1. Separation of Concerns
- **Shop**: gestisce connection lifecycle
- **DbopPlugin**: gestisce transaction management
- **Handler classes**: solo business logic

### 2. Testabilità
```python
# Test con mock cursor
def test_add():
    mock_cursor = MagicMock()
    types = ArticleTypes(shop)
    types.add("test", cursor=mock_cursor, autocommit=False)
    mock_cursor.execute.assert_called()
```

### 3. Thread Safety
- Connection per thread via `threading.local()`
- Nessuna race condition

### 4. Flessibilità Transazionale
```python
# Uso normale (autocommit)
shop.types.add("electronics")

# Transazione esplicita
shop.types.add("electronics", autocommit=False)
shop.articles.add(1, "LAPTOP", ..., autocommit=False)
shop.commit()

# Test con mock
shop.types.add("test", cursor=mock_cursor)
```

### 5. Composizione di Plugin
```python
dbop = (
    Switcher(name="types")
    .plug("logging", mode="silent")   # Log delle chiamate
    .plug("pydantic")                  # Validazione parametri
    .plug(DbopPlugin())                # Transaction management
    .plug(SmartasyncPlugin())          # Async wrapping
)
```

Ogni plugin aggiunge una funzionalità ortogonale!

## Conclusioni

L'evoluzione mostra come identificare pattern ripetuti e astrarre progressivamente:

1. **Fase 0→1**: Identificare il problema (commit non controllabile)
2. **Fase 1→2**: Centralizzare la gestione (Shop.current_connection)
3. **Fase 2→3**: Aggiungere dispatch e validazione (Switcher)
4. **Fase 3→4**: Automatizzare transaction management (DbopPlugin)
5. **Fase 4→5**: Eliminare ultimo boilerplate (cursor injection)

Risultato: **Codice pulito, testabile, manutenibile** con zero boilerplate ripetuto.
