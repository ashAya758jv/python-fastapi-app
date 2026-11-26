# TP 8 – Stratégies GitHub Actions

**Achiban Aya — ENSAM Casablanca**

Dépôt personnel : [ashAya758jv/python-fastapi-app](https://github.com/ashAya758jv/python-fastapi-app).
Branche : [feature/tp-strategies](https://github.com/ashAya758jv/python-fastapi-app/tree/feature/tp-strategies).

## Préparation et déclenchement

L’énoncé Word a été lu intégralement. Le travail réutilise le fork personnel existant de `mrlabied/python-fastapi-app`. La branche a été créée depuis `main` au commit `ca8cd780844a122b5d01497d8c54875160c057df`. Les anciens fichiers et la branche `feature/tp-ci` ont été conservés. Aucune fusion ni modification de `main` n’a été effectuée.

Git 2.56.0, GitHub CLI 2.106.0 (copie portable locale) et l’authentification du compte `ashAya758jv` ont été vérifiés. Le premier commit contient exactement le squelette de la partie 0. Un commit séparé ajoute `-r requirements.txt` à `requirements-dev.txt` : les dépendances FastAPI manquaient dans l’installation demandée par le workflow.

La tentative réelle `gh workflow run tp-strategies.yml --ref feature/tp-strategies` a renvoyé `HTTP 404: workflow tp-strategies.yml not found on the default branch`. Le workflow n’était pas présent sur `main`. Le déclencheur `workflow_dispatch` est conservé et un déclencheur `push` limité à `feature/tp-strategies` permet les expériences sans modifier la branche par défaut. Les modifications portant uniquement sur `REPONSES.md` ou `preuves/**` ne relancent pas les six jobs. Les cinq exécutions ci-dessous ont été déclenchées par de vrais événements `push`.

Référence : [workflow_dispatch — documentation GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch).

## Q1. Combien de jobs sont générés ?

La matrice produit **6 jobs** : 2 systèmes × 3 versions de Python.

| Système | Version de Python |
| --- | --- |
| `ubuntu-latest` | `"3.11"` |
| `ubuntu-latest` | `"3.12"` |
| `ubuntu-latest` | `"3.13"` |
| `windows-latest` | `"3.11"` |
| `windows-latest` | `"3.12"` |
| `windows-latest` | `"3.13"` |

Observation réelle : 6 réussis, 0 échoués, 0 annulés. [Voir l’exécution](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905137337).

## Q2. Combien de jobs après exclude et include ?

Il reste **6 jobs** : 6 − 1 exclusion + 1 ajout. `windows-latest` avec Python 3.11 est supprimé. `ubuntu-latest` avec Python 3.14 et `experimental: true` est ajouté. Les autres jobs sont Ubuntu 3.11, 3.12, 3.13 et Windows 3.12, 3.13.

Au niveau du job, `continue-on-error: ${{ matrix.experimental == true }}` autorise un éventuel échec de la combinaison expérimentale sans faire échouer le workflow. Les cinq autres combinaisons restent bloquantes. Python 3.14 est désigné expérimental dans ce TP par la propriété de matrice ; cela ne signifie pas que sa version installée est une préversion.

Observation réelle : 6 réussis, 0 échoués, 0 annulés. [Voir l’exécution](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905410642).

## Q3. Peut-on exclure la combinaison Python 3.14 ?

Ajouter Python 3.14 dans `exclude` ne supprime pas le job ajouté dans `include`. GitHub traite `exclude` avant `include` : Python 3.14 n’existe pas dans la matrice de base, puis il est ajouté après les exclusions. Pour le supprimer ici, il faut retirer son entrée de `include`.

Référence : [ordre exclude / include — documentation GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstrategymatrixexclude).

## Q4. Quelle différence entre fail-fast: true et false ?

Le fichier temporaire `tests/test_break.py` contenait le test demandé :

```python
import sys

def test_break():
    assert sys.platform != "win32"
```

- Avec `fail-fast: true` : **4 réussis, 1 échoué, 1 annulé**. [Exécution](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905696487).
- Avec `fail-fast: false` : **4 réussis, 2 échoués, 0 annulés**. [Exécution](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905883791).

Dans l’exécution avec `true`, Windows/Python 3.12 échoue dans `Run tests` sur `assert sys.platform != "win32"`. Windows/Python 3.13 est annulé pendant `Install dependencies` : ses étapes `Run linter` et `Run tests` sont donc ignorées. Les quatre jobs Ubuntu ont déjà réussi. Dans l’exécution avec `false`, les deux jobs Windows terminent et révèlent chacun cet échec volontaire.

Avec `true`, un échec bloquant demande l’annulation des autres jobs encore en cours ou en attente. Les jobs déjà terminés gardent leur résultat ; le nombre exact d’annulations dépend de leur avancement. Avec `false`, tous les jobs peuvent terminer, ce qui donne le diagnostic de chaque combinaison. Un échec du job expérimental autorisé par `continue-on-error` ne déclenche pas l’annulation de la matrice.

Je choisirais `true` pour arrêter rapidement une validation devenue inutile et économiser des ressources. Je choisirais `false` pour étudier la compatibilité sur tous les systèmes et toutes les versions en une seule exécution. Les deux exécutions avec le test volontaire sont en échec global, car Windows reste bloquant. Le test temporaire a ensuite été supprimé dans le commit de la partie 4.

## Q5. Pourquoi utiliser max-parallel en entreprise ?

1. Limiter la consommation simultanée de runners, de CPU et de mémoire pour partager les ressources entre équipes.
2. Éviter de surcharger les services communs utilisés par les tests : base de données, API avec quotas ou licences limitées.

`max-parallel: 2` limite à deux le nombre de jobs simultanés de cette matrice. Ce réglage peut augmenter la durée totale et ne garantit pas une baisse du total de minutes facturées. Le workflow final conserve `fail-fast: false`.

Observation réelle : **6 réussis, 0 échoués, 0 annulés**, workflow final **success**. [Voir l’exécution finale](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45906085784). Le recoupement des horodatages des étapes exécutées donne un maximum observé de **2 jobs simultanés**.

| Job final | Début des étapes (UTC) | Fin des étapes (UTC) |
| --- | --- | --- |
| `test (ubuntu-latest, 3.11)` | 2026-11-26T22:38:36Z | 2026-11-26T22:38:49Z |
| `test (ubuntu-latest, 3.12)` | 2026-11-26T22:38:36Z | 2026-11-26T22:38:45Z |
| `test (ubuntu-latest, 3.13)` | 2026-11-26T22:38:49Z | 2026-11-26T22:39:02Z |
| `test (windows-latest, 3.12)` | 2026-11-26T22:38:54Z | 2026-11-26T22:39:31Z |
| `test (windows-latest, 3.13)` | 2026-11-26T22:39:06Z | 2026-11-26T22:39:33Z |
| `test (ubuntu-latest, 3.14, true)` | 2026-11-26T22:39:34Z | 2026-11-26T22:39:49Z |

Un relevé de l’API a également montré **2 jobs en cours et 1 en attente**. Les relevés bruts sont conservés dans les preuves.

## Résultats réels des exécutions

| Étape | Commit testé | Résultat du workflow | Résultats des jobs | Lien |
| --- | --- | --- | --- | --- |
| Partie 1 — Matrice de base | `ecdddea` | `success` | 6 réussis, 0 échoués, 0 annulés | [Actions](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905137337) |
| Partie 2 — Exclude / Include | `af236bf` | `success` | 6 réussis, 0 échoués, 0 annulés | [Actions](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905410642) |
| Partie 3 — fail-fast: true | `572347d` | `failure` | 4 réussis, 1 échoué, 1 annulé | [Actions](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905696487) |
| Partie 3 — fail-fast: false | `d1c3b40` | `failure` | 4 réussis, 2 échoués, 0 annulés | [Actions](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45905883791) |
| Partie 4 — max-parallel: 2 | `c77affc` | `success` | 6 réussis, 0 échoués, 0 annulés | [Actions](https://github.com/ashAya758jv/python-fastapi-app/actions/runs/45906085784) |

Détail par combinaison (`—` = combinaison absente de cette étape) :

| OS | Python | Base | Exclude / Include | Fail-fast true | Fail-fast false | Final |
| --- | --- | --- | --- | --- | --- | --- |
| `ubuntu-latest` | `3.11` | success | success | success | success | success |
| `ubuntu-latest` | `3.12` | success | success | success | success | success |
| `ubuntu-latest` | `3.13` | success | success | success | success | success |
| `ubuntu-latest` | `3.14` | — | success | success | success | success |
| `windows-latest` | `3.11` | success | — | — | — | — |
| `windows-latest` | `3.12` | success | success | failure | failure | success |
| `windows-latest` | `3.13` | success | success | cancelled | failure | success |

Les statuts `success`, `failure` et `cancelled` sont les conclusions retournées par GitHub, sans remplacement par des résultats attendus. Les étapes et leurs horodatages sont archivés dans [preuves/executions.json](preuves/executions.json).

## Vérification locale et état final

- `ruff check .` : réussi.
- `pytest` sous Windows / Python 3.13.2 : **18 tests réussis, couverture 100 %**, seuil requis 85 %.
- Journaux GitHub de l’exécution finale : **18 tests réussis et couverture 100 % dans chacun des six jobs**, avec Ruff réussi partout. Les extraits correspondants sont archivés dans les preuves.
- Le premier lancement local a révélé `DEBUG=release` dans l’environnement Windows. Cette valeur n’est pas un booléen accepté par Pydantic. Le lancement validé retire `DEBUG` uniquement de l’environnement du processus de test ; le code et la configuration Windows globale restent inchangés.
- Des avertissements de dépréciation Starlette/httpx sont présents localement et dans Actions. Les actions imposées par l’énoncé signalent aussi la dépréciation du module Node `punycode`. Ces avertissements ne font pas échouer les validations.
- `actionlint` : validation réussie du workflow final.
- `tests/test_break.py` est absent du résultat final.
- Le workflow final reprend checkout v4, setup-python v5, l’installation des dépendances, Ruff et pytest, avec les noms de steps en anglais.

## Captures d’écran à fournir

1. La partie 1 dans l’onglet Actions avec les six jobs Ubuntu/Windows et Python 3.11/3.12/3.13.
2. La partie 2 avec Ubuntu/Python 3.14 et l’absence de Windows/Python 3.11.
3. Les deux exécutions fail-fast, montrant les statuts réels, puis le détail d’un échec Windows dans `Run tests`.
4. L’exécution finale réussie avec les six jobs ; pour montrer les deux jobs en cours et les suivants en attente, ouvrir le lien final, cliquer sur `Re-run all jobs`, confirmer, puis prendre la capture pendant cette réexécution si nécessaire.
5. Le workflow final et ce fichier `REPONSES.md` sur la branche `feature/tp-strategies`.
