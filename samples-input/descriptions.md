# Real datasets

- Flanders' Mandatendatabank, available at https://mandaten.lokaalbestuur.vlaanderen.be/
- Rijksmuseum Amsterdam's heritage collection, available at https://data.rijksmuseum.nl/docs/data-dumps/ as suggested in https://github.com/DiSHACLed/shape-generation/issues/1
- VLIZ' MarineRegions dataset, obtained by syncing their LDES feed at https://www.marineregions.org/feed
- TODO: Riooloverstorten Aquafin, not in production just yet. Snippet available at https://informatievlaanderen.github.io/OSLO-mapping/water/Aquafin%20-%20Overstort%20In%20Vlaanderen/0_4_examples_overstort

## rijksmuseum-X

https://data.rijksmuseum.nl/docs/data-dumps/

ttl obtained by extracting X.tar.tar and merging to ttl file

## mandaten-fix

https://mandaten.lokaalbestuur.vlaanderen.be/

## lblod-big-fix

dump lblod

## lblod-small-fix

## marine-regions

# artificial datasets

## people files

All `people-*.ttl` files share a canonical set of 10 people (alice–jack) with consistent names and birthdays. Each file introduces one specific quirk to test (not-so-)special cases in shape generation.

**Canonical people** (used across all files):

### people.ttl

Baseline dataset. All 10 people have `foaf:birthday` typed as `xsd:date`. No quirks.

### people-without-birthday.ttl

9 people have `foaf:birthday^^xsd:date`; `ex:jack` has no birthday property at all.

### people-two-birthday.ttl

9 people have exactly one `foaf:birthday^^xsd:date`; `ex:jack` has two `foaf:birthday` triples (cardinality > 1).

### people-string.ttl

9 people have `foaf:birthday^^xsd:date`; `ex:jack` has `foaf:birthday "28th of february"`.

### people-foaf-schema.ttl

9 people use `foaf:birthday^^xsd:date`; `ex:jack` uses `schema:birthDate^^xsd:date` instead.

### people-datetime.ttl

9 people have `foaf:birthday^^xsd:date`; `ex:jack` has `foaf:birthday^^xsd:dateTime`.

### people-all.ttl

Combines all quirks in one file. First 6 people (alice–frank) are well-formed. Last 4 each have a distinct anomaly:

| Person | Quirk |
|---|---|
| `ex:grace` | no birthday property |
| `ex:henry` | uses `schema:birthDate` instead of `foaf:birthday` |
| `ex:iris` | birthday typed as `xsd:dateTime` instead of `xsd:date` |
| `ex:jack` | birthday is a plain string (`"28th of february"`) |
