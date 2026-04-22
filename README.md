# Suivi_de_crise

Générateur Python de dashboard HTML standalone pour le fichier `Crise_Secteur_NRJ_Delais_Version interne_260413.xlsx`.

## Build

```bash
python -m crise_viz build --input "Data_source\Crise_Secteur_NRJ_Delais_Version interne_260413.xlsx" --output "dist\crise_dashboard.html" --default-variant power_bi_ready
```

Le HTML généré embarque:

- les agrégats de données utiles au front
- la géométrie cartographique nécessaire
- le runtime JS
- quatre variantes visuelles basculables sans rechargement

Les bibliothèques de visualisation sont chargées via CDN.

## Tests

```bash
python -m pytest -q -p no:tmpdir -p no:cacheprovider
```
