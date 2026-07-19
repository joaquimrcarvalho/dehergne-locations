# Data quality: date string in place field

Row in `locations_names_no_wikidata_with_candidates.xlsx` has the **place** column set to `17010220` (a date string `17010220`), for the attribute `jesuita-votos-local` of person `deh-manuel-da-mata` (Manuel da Mata).

This is a transcription/parsing artefact — a date leaked into the place-name field — not an unidentified toponym. The corresponding source `.cli` line should be checked:

```
ls$jesuita-votos-local/.../17220000>
```

Person: **Manuel da Mata** (`deh-manuel-da-mata`)

### Places in the biography (chronological)

| Date | Event | Place | Wikidata |
|------|-------|-------|----------|
| — | stay | Nanquim | — |
| — | stay | Macau | — |
| — | vows location | 17010220 | — |
| 1667-10-10 | birth | Lisboa | Q597 |
| 1697-10 | arrival | Macau | Q14773 |
| 1698 | stay | Shanghai | Q8686 |
| 1700 | stay | Changshu (Tch'ang-chou) | — |
| 1700 | stay | Shanghai | — |
| 1707-04-02 | stay | Cantão | Q16572 |
| 1721 | stay | Macau | Q14773 |
| 1722 | stay | Macau | Q14773 |
| 1724-08-25 | death | Macau | Q14773 |

**Task**: inspect the `.cli` source, fix the place value, and re-import. Then this row will leave the unidentified-locations set.
