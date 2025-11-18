# Autocompletion Implementation Plan

Questo documento elenca, in ordine logico, i passi necessari per introdurre un sistema di shell completion dinamico e multi-shell integrato con SmartRoute.

## 1. Definizione del protocollo di completion
- Stabilire un sottocomando o flag dedicato (`smpub --complete <shell> <cursor> <args...>`) che, dato il contesto corrente, restituisca un payload JSON con i suggerimenti.
- Definire la struttura del payload (tipo di suggerimento, testo da inserire, descrizione, eventuale hint inline).
- Documentare i livelli di completamento: handler, metodi, parametri e valori speciali (`_system`, comandi interni).

## 2. Integrazione con SmartRoute
- Creare un helper (es. `CompletionEngine`) che utilizzi `publisher.api.describe()` e gli `api.describe()` degli handler per costruire i suggerimenti.
- Mappare i livelli di profondità del comando ai nodi del router SmartRoute e ai metadati presenti nello schema (metodi, parametri, required/optional).
- Garantire che il comando di completion lavori sull’istanza attiva (quindi sullo stesso processo CLI) per riflettere lo stato runtime.

## 3. Estensione di `CLIChannel`
- Aggiungere un metodo dedicato (`complete()` o simile) che riceva i token e il cursore e restituisca il JSON definito al punto 1.
- Assicurarsi che la modalità completion bypassi ogni output umano (niente logging/formatter) e termini con codice 0 anche quando non ci sono suggerimenti.
- Gestire eventuali errori (handler inesistente, metodo non trovato) restituendo suggerimenti vuoti e messaggi diagnostici nel payload.

## 4. Script shell specifici
- **bash**: creare una funzione `_smpub_complete` che usa `COMP_LINE/COMP_POINT`, invoca `smpub --complete bash ...` e popola `COMPREPLY`.
- **zsh**: definire un widget `_smpub_complete` che sfrutta `$words`/`$CURRENT`, chiama il sottocomando e usa `compadd` con descrizioni.
- **fish**: aggiungere `complete -c smpub -a '(smpub --complete fish ...)'` e formattare l’output `testo<TAB>descrizione`.
- In ogni script, convertire il JSON restituito dal CLI in un elenco di stringhe secondo il protocollo della shell.

## 5. Supporto agli hint inline
- Includere nel payload un campo `inline_hint` o similare per ciascun suggerimento.
- Per le shell che lo supportano (zsh, fish), usare il campo per visualizzare il testo grigio; in bash si può usare `compopt -o nospace` o `COMPREPLY` descrittivo se necessario.

## 6. Distribuzione e installazione
- Prevedere un comando (`smpub install-completion <shell>`) o documentare come `source`/`complete` i file generati.
- Collocare gli script in `scripts/completion/<shell>.sh` o simile e includerli nel pacchetto.
- Aggiornare il README e la documentazione (`docs/user-guide/cli-mode.md`) con istruzioni per l’attivazione.

## 7. Test manuale e validazione
- Verificare in ogni shell che il completamento sia contestuale e che reagisca ai cambiamenti dell’API (aggiunta/rimozione handler).
- Testare casi limite: nessun handler, handler senza API, metodi asincroni, parametri obbligatori/facoltativi.
- Assicurarsi che la modalità completion sia veloce e non interferisca con lo stato dell’app (nessuna esecuzione di business logic).

Seguendo questi punti si ottiene un sistema di autocompletamento dinamico, coerente con l’architettura SmartRoute e compatibile con bash, zsh e fish.
