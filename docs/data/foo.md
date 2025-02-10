```sql
SELECT product_name
FROM products 
LIMIT 5;
```
```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                           product_name                                                                                            │
│                                                                              struct(lang varchar, "text" varchar)[]                                                                               │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [{'lang': main, 'text': Organic Vermont Maple Syrup Grade A Dark Color Robust Taste}, {'lang': en, 'text': Organic Vermont Maple Syrup Grade A Dark Color Robust Taste}, {'lang': fr, 'text': 1…  │
│ [{'lang': main, 'text': Imitation vanilla flavor}, {'lang': en, 'text': Imitation vanilla flavor}]                                                                                                │
│ [{'lang': main, 'text': 1% low-fat milk}, {'lang': en, 'text': 1% low-fat milk}]                                                                                                                  │
│ [{'lang': main, 'text': Fresh udon bowl}, {'lang': fr, 'text': Fresh udon bowl}]                                                                                                                  │
│ [{'lang': main, 'text': Seto fumi furikake}, {'lang': en, 'text': Seto fumi furikake}]                                                                                                            │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```