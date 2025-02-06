
### List all tables in the database
```sql
-- List all tables in the database
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'main';
```
```text
┌────────────┐
│ table_name │
│  varchar   │
├────────────┤
│ products   │
└────────────┘
```
### List all tables in the database
```sql
-- List all tables in the database
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'main';
```
```text
┌────────────┐
│ table_name │
│  varchar   │
├────────────┤
│ products   │
└────────────┘
```
### Show columns in the products table
```sql
-- Show columns in the products table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'products';
```
| column_name | data_type |
| --- | --- |
| additives_n | INTEGER |
| additives_tags | VARCHAR[] |
| allergens_tags | VARCHAR[] |
| brands_tags | VARCHAR[] |
| brands | VARCHAR |
| categories | VARCHAR |
| categories_tags | VARCHAR[] |
| checkers_tags | VARCHAR[] |
| ciqual_food_name_tags | VARCHAR[] |
| cities_tags | VARCHAR[] |
| code | VARCHAR |
| compared_to_category | VARCHAR |
| complete | INTEGER |
| completeness | FLOAT |
| correctors_tags | VARCHAR[] |
| countries_tags | VARCHAR[] |
| created_t | BIGINT |
| creator | VARCHAR |
| data_quality_errors_tags | VARCHAR[] |
| data_quality_info_tags | VARCHAR[] |
| data_quality_warnings_tags | VARCHAR[] |
| data_sources_tags | VARCHAR[] |
| ecoscore_data | VARCHAR |
| ecoscore_grade | VARCHAR |
| ecoscore_score | INTEGER |
| ecoscore_tags | VARCHAR[] |
| editors | VARCHAR[] |
| emb_codes_tags | VARCHAR[] |
| emb_codes | VARCHAR |
| entry_dates_tags | VARCHAR[] |
| food_groups_tags | VARCHAR[] |
| generic_name | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| images | STRUCT("key" VARCHAR, imgid INTEGER, sizes STRUCT("100" STRUCT(h INTEGER, w INTEGER), "200" STRUCT(h INTEGER, w INTEGER), "400" STRUCT(h INTEGER, w INTEGER), "full" STRUCT(h INTEGER, w INTEGER)), uploaded_t BIGINT, uploader VARCHAR)[] |
| informers_tags | VARCHAR[] |
| ingredients_analysis_tags | VARCHAR[] |
| ingredients_from_palm_oil_n | INTEGER |
| ingredients_n | INTEGER |
| ingredients_original_tags | VARCHAR[] |
| ingredients_percent_analysis | INTEGER |
| ingredients_tags | VARCHAR[] |
| ingredients_text | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| ingredients_with_specified_percent_n | INTEGER |
| ingredients_with_unspecified_percent_n | INTEGER |
| ingredients_without_ciqual_codes_n | INTEGER |
| ingredients_without_ciqual_codes | VARCHAR[] |
| ingredients | VARCHAR |
| known_ingredients_n | INTEGER |
| labels_tags | VARCHAR[] |
| labels | VARCHAR |
| lang | VARCHAR |
| languages_tags | VARCHAR[] |
| last_edit_dates_tags | VARCHAR[] |
| last_editor | VARCHAR |
| last_image_t | BIGINT |
| last_modified_by | VARCHAR |
| last_modified_t | BIGINT |
| last_updated_t | BIGINT |
| link | VARCHAR |
| main_countries_tags | VARCHAR[] |
| manufacturing_places_tags | VARCHAR[] |
| manufacturing_places | VARCHAR |
| max_imgid | INTEGER |
| minerals_tags | VARCHAR[] |
| misc_tags | VARCHAR[] |
| new_additives_n | INTEGER |
| no_nutrition_data | BOOLEAN |
| nova_group | INTEGER |
| nova_groups_tags | VARCHAR[] |
| nova_groups | VARCHAR |
| nucleotides_tags | VARCHAR[] |
| nutrient_levels_tags | VARCHAR[] |
| nutriments | STRUCT("name" VARCHAR, "value" FLOAT, "100g" FLOAT, serving FLOAT, unit VARCHAR, prepared_value FLOAT, prepared_100g FLOAT, prepared_serving FLOAT, prepared_unit VARCHAR)[] |
| nutriscore_grade | VARCHAR |
| nutriscore_score | INTEGER |
| nutrition_data_per | VARCHAR |
| obsolete | BOOLEAN |
| origins_tags | VARCHAR[] |
| origins | VARCHAR |
| owner_fields | STRUCT(field_name VARCHAR, "timestamp" BIGINT)[] |
| owner | VARCHAR |
| packagings_complete | BOOLEAN |
| packaging_recycling_tags | VARCHAR[] |
| packaging_shapes_tags | VARCHAR[] |
| packaging_tags | VARCHAR[] |
| packaging_text | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| packaging | VARCHAR |
| packagings | STRUCT(material VARCHAR, number_of_units BIGINT, quantity_per_unit VARCHAR, quantity_per_unit_unit VARCHAR, quantity_per_unit_value VARCHAR, recycling VARCHAR, shape VARCHAR, weight_measured FLOAT)[] |
| photographers | VARCHAR[] |
| popularity_key | BIGINT |
| popularity_tags | VARCHAR[] |
| product_name | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| product_quantity_unit | VARCHAR |
| product_quantity | VARCHAR |
| purchase_places_tags | VARCHAR[] |
| quantity | VARCHAR |
| rev | INTEGER |
| scans_n | INTEGER |
| serving_quantity | VARCHAR |
| serving_size | VARCHAR |
| states_tags | VARCHAR[] |
| stores_tags | VARCHAR[] |
| stores | VARCHAR |
| traces_tags | VARCHAR[] |
| unique_scans_n | INTEGER |
| unknown_ingredients_n | INTEGER |
| unknown_nutrients_tags | VARCHAR[] |
| vitamins_tags | VARCHAR[] |
| with_non_nutritive_sweeteners | INTEGER |
| with_sweeteners | INTEGER |

Total number of rows: 109
### Count all rows in the products table
```sql
-- Count all rows in the products table 
SELECT COUNT(*) AS count FROM products;
```
```text
┌───────┐
│ count │
│ int64 │
├───────┤
│ 94802 │
└───────┘
```
### Product names sample and type
```sql
-- Product names sample and type
SELECT 
    product_name,
    typeof(product_name) AS type_colonne
FROM products 
LIMIT 20;
```
```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────┐
│                                                                       product_name                                                                       │              type_colonne              │
│                                                          struct(lang varchar, "text" varchar)[]                                                          │                varchar                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────┤
│ [{'lang': main, 'text': Organic Vermont Maple Syrup Grade A Dark Color Robust Taste}, {'lang': en, 'text': Organic Vermont Maple Syrup Grade A Dark Co…  │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Imitation vanilla flavor}, {'lang': en, 'text': Imitation vanilla flavor}]                                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': 1% low-fat milk}, {'lang': en, 'text': 1% low-fat milk}]                                                                         │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Fresh udon bowl}, {'lang': fr, 'text': Fresh udon bowl}]                                                                         │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Seto fumi furikake}, {'lang': en, 'text': Seto fumi furikake}]                                                                   │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Assaisonnement pour riz}, {'lang': fr, 'text': Assaisonnement pour riz}]                                                         │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Sushi Ginger Gari}, {'lang': en, 'text': Sushi Ginger Gari}]                                                                     │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Chef d'oeuf™avec fromage sur muffin anglais}, {'lang': fr, 'text': Chef d'oeuf™avec fromage sur muffin anglais}]                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ []                                                                                                                                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ []                                                                                                                                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Organic Blue Agave}, {'lang': fr, 'text': Organic Blue Agave Syrup}, {'lang': en, 'text': Organic Blue Agave}]                   │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text':  Gâteau double chocolat }, {'lang': fr, 'text':  Gâteau double chocolat }]                                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Macaroni & Cheese Classic Cheddar}, {'lang': en, 'text': Macaroni & Cheese Classic Cheddar}]                                     │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Truvia}, {'lang': fr, 'text': Truvia}]                                                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Goldfish Baked Snack Cracker Flavour Blasted Xtreme Chedar}, {'lang': en, 'text': Goldfish Baked Snack Cracker Flavour Blasted…  │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Goldfish Cheddar Baked Snack Cracker}, {'lang': en, 'text': Goldfish Cheddar Baked Snack Cracker}, {'lang': fr, 'text': Goldfi…  │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Craquelins Goldfish Trio Fromage}, {'lang': fr, 'text': Craquelins Goldfish Trio Fromage}]                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Gmills hny nut cheerios sweetened whl grn oat cereal}, {'lang': en, 'text': Gmills hny nut cheerios sweetened whl grn oat cere…  │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Nature Valley Crunchy Oats 'N Honey}, {'lang': en, 'text': Nature Valley Crunchy Oats 'N Honey}]                                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lychee}, {'lang': fr, 'text': Lychee}, {'lang': en, 'text': Lychee in Syrup}]                                                    │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────┤
│ 20 rows                                                                                                                                                                                 2 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Gets distinct data types from the products table
```sql
-- Gets distinct data types from the products table
SELECT DISTINCT data_type
FROM information_schema.columns 
WHERE table_name = 'products'
ORDER BY data_type;
```
```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                             data_type                                                                                             │
│                                                                                              varchar                                                                                              │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BIGINT                                                                                                                                                                                            │
│ BOOLEAN                                                                                                                                                                                           │
│ FLOAT                                                                                                                                                                                             │
│ INTEGER                                                                                                                                                                                           │
│ STRUCT("key" VARCHAR, imgid INTEGER, sizes STRUCT("100" STRUCT(h INTEGER, w INTEGER), "200" STRUCT(h INTEGER, w INTEGER), "400" STRUCT(h INTEGER, w INTEGER), "full" STRUCT(h INTEGER, w INTEGE…  │
│ STRUCT("name" VARCHAR, "value" FLOAT, "100g" FLOAT, serving FLOAT, unit VARCHAR, prepared_value FLOAT, prepared_100g FLOAT, prepared_serving FLOAT, prepared_unit VARCHAR)[]                      │
│ STRUCT(field_name VARCHAR, "timestamp" BIGINT)[]                                                                                                                                                  │
│ STRUCT(lang VARCHAR, "text" VARCHAR)[]                                                                                                                                                            │
│ STRUCT(material VARCHAR, number_of_units BIGINT, quantity_per_unit VARCHAR, quantity_per_unit_unit VARCHAR, quantity_per_unit_value VARCHAR, recycling VARCHAR, shape VARCHAR, weight_measured …  │
│ VARCHAR                                                                                                                                                                                           │
│ VARCHAR[]                                                                                                                                                                                         │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              11 rows                                                                                              │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products with milk category (French/English)
```sql
-- Products with milk category (French/English)
SELECT
    code,
    unnest(
        list_filter (product_name, x -> x.lang == 'main')
    )['text'] AS product_name,
categories_tags
FROM products
WHERE array_to_string(categories_tags, ',') LIKE 'en:%milk%' 
   OR array_to_string(categories_tags, ',') LIKE 'fr:%lait%' 
```
```text
┌────────────────┬──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│      code      │     product_name     │                                                                      categories_tags                                                                      │
│    varchar     │       varchar        │                                                                         varchar[]                                                                         │
├────────────────┼──────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0016229001704  │ COCONUT MILK         │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:dairy-substitutes, en:milk-substit…  │
│ 0025293001008  │ Almond Original Be…  │ [en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:dairy-substitutes, en:milk-substitutes, en:nuts-and-their-products, en:plan…  │
│ 0025293001503  │ Almond, Unsweetene…  │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:dairy-substitutes, en:milk-substit…  │
│ 0025293001886  │ Almond Vanilla, Un…  │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:dairy-substitutes, en:milk-substit…  │
│ 0025293003903  │ Unsweetened Cultur…  │ [en:dairies, en:fermented-foods, en:fermented-milk-products, en:desserts, en:dairy-desserts, en:fermented-dairy-desserts, en:yogurts]                     │
│ 0025293600713  │ Soy Original Organ…  │ [en:plant-based-foods-and-beverages, en:beverages, en:dairies, en:plant-based-foods, en:legumes-and-their-products, en:dairy-substitutes, en:milk-subst…  │
│ 0025293600737  │ Soy Vanilla Organi…  │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:legumes-and-their-products, en:dai…  │
│ 0025293600751  │ Soy Chocolate Fort…  │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:legumes-and-their-products, en:dai…  │
│ 0037014242317  │ 48% Milk Chocolate…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:chocolates, en:milk-chocolates]                      │
│ 0037466019871  │ Hazelnut Swiss Cla…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:chocolates, en:milk-chocolates, en:chocolates-with-hazelnuts, en:milk-chocolates-with-hazeln…  │
│    ·           │          ·           │                                                                             ·                                                                             │
│    ·           │          ·           │                                                                             ·                                                                             │
│    ·           │          ·           │                                                                             ·                                                                             │
│ 09000810       │ Goodfood table salt  │ [en:dairies, en:fermented-foods, en:fermented-milk-products, en:desserts, en:dairy-desserts, en:fermented-dairy-desserts, en:yogurts, en:groceries, en:…  │
│ 0059749998468  │ Oat Milk Original    │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:dairy-substitutes, en:milk-substitutes, en:plant-based-b…  │
│ 0063667201197  │ Barista avoine san…  │ [en:beverages-and-beverages-preparations, en:plant-based-foods-and-beverages, en:beverages, en:plant-based-foods, en:cereals-and-potatoes, en:dairy-sub…  │
│ 0850050030294  │ Good Start Plus Re…  │ [en:baby-foods, en:baby-milks, en:infant-formulas, en:ready-to-feed-baby-milks, en:ready-to-feed-baby-first-milk]                                         │
│ 0056796905913  │ Ready to Feed Milk…  │ [en:baby-foods, en:baby-milks]                                                                                                                            │
│ 10055325577499 │ Similac Advance St…  │ [en:baby-foods, en:baby-milks, en:infant-formulas, en:ready-to-feed-baby-milks]                                                                           │
│ 0056796906699  │ Enfamil A+ Neuro Pro │ [en:baby-foods, en:baby-milks, en:infant-formulas, en:ready-to-feed-baby-milks, en:ready-to-feed-baby-first-milk]                                         │
│ 0060383715540  │ 2% MF Cow’s Milk     │ [en:beverages-and-beverages-preparations, en:beverages, en:dairies, en:dairy-drinks, en:organic-2-percent-mf-cow-s-milk]                                  │
│ 4980655952021  │ Memorial Pure        │ [en:cookies-biscuits-individually-wrapped, en:milk-flavour-sweets-wafer-cookies-rolls]                                                                    │
│ 5900102025794  │ Malaga Smietankowa…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:chocolates, en:milk-chocolates, en:filled-chocolates, en:filled-milk-chocolates]               │
├────────────────┴──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1958 rows (20 shown)                                                                                                                                                                    3 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Search categories with 'chocolat' or 'chocolate'
```sql

-- Search categories with 'chocolat' or 'chocolate'
SELECT DISTINCT
    unnest AS category
FROM products,
    unnest(categories_tags) AS unnest 
WHERE category LIKE 'fr:%chocolat%' 
OR category LIKE 'en:%chocolate%'
ORDER BY category
LIMIT 10;
```
```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                                    category                                    │
│                                    varchar                                     │
├────────────────────────────────────────────────────────────────────────────────┤
│ en:70-dark-chocolate-topped-butter-biscuits-cookies                            │
│ en:70-dk-chocolate-topped-butter-cookies-biscuits                              │
│ en:animal-crackers-covered-in-peanut-butter-candy-and-dipped-in-milk-chocolate │
│ en:assorted-chocolate-candies                                                  │
│ en:assorted-chocolates                                                         │
│ en:assorted-luxury-chocolates-in-a-clear-gift-box                              │
│ en:bars-covered-with-chocolate                                                 │
│ en:biscuit-cookie-snack-w-chocolate-filling                                    │
│ en:biscuit-with-a-chocolate-bar-covering                                       │
│ en:biscuit-with-a-milk-chocolate-bar-covering                                  │
├────────────────────────────────────────────────────────────────────────────────┤
│                                    10 rows                                     │
└────────────────────────────────────────────────────────────────────────────────┘
```
### Products containing 'chocolat' or 'chocolate' in their French/English categories
```sql
-- Products containing 'chocolat' or 'chocolate' in their French/English categories
SELECT DISTINCT
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    categories_tags
FROM products
WHERE array_to_string(categories_tags, ',') LIKE 'fr:%chocolat%' 
OR array_to_string(categories_tags, ',') LIKE 'en:%chocolate%'
LIMIT 10;
```
```text
┌───────────────┬──────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     code      │           name           │                                                                    categories_tags                                                                     │
│    varchar    │         varchar          │                                                                       varchar[]                                                                        │
├───────────────┼──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0037466082714 │ Swiss Classic Milk Cho…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:chocolates, en:milk-chocolates]                                                             │
│ 0058496434175 │ Mars Bites               │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                      │
│ 0060383042400 │ 40% Dark Chocolate       │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:chocolates, en:dark-chocolates]                                                             │
│ 0060383197520 │ Cocoa Powder             │ [en:cocoa-and-its-products, en:cocoa-and-chocolate-powders, en:cocoa-powders]                                                                          │
│ 0062020000842 │ Nutella                  │ [en:breakfasts, en:spreads, en:sweet-spreads, fr:pates-a-tartiner, en:hazelnut-spreads, en:chocolate-spreads, en:cocoa-and-hazelnuts-spreads]          │
│ 0063675007392 │ Tartinade Chocolat Noir  │ [en:breakfasts, en:spreads, en:sweet-spreads, fr:pates-a-tartiner, en:hazelnut-spreads, en:chocolate-spreads, en:cocoa-and-hazelnuts-spreads]          │
│ 0066721020581 │ Snak Paks Mini Oreo      │ [en:snacks, en:sweet-snacks, en:biscuits-and-cakes, en:biscuits, en:filled-biscuits, en:chocolate-sandwich-cookies]                                    │
│ 0067300860758 │ Maple Crunch milk choc…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:bars, en:chocolate-candies, en:candies, en:bars-covered-with-chocolate] │
│ 0068000702270 │ Cherry Blossom           │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:bonbons]                                          │
│ 0070221011116 │ Swiss milk chocolate bar │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:chocolates, en:candies, en:milk-chocolates]       │
├───────────────┴──────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                                                                 3 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Search in the list `allergen_tags` values containing `fr`
```sql
-- Search in the list `allergen_tags` values containing `fr`
SELECT count(code) AS nb, ANY_VALUE(code) AS code, allergens_tags
FROM products
WHERE regexp_matches(array_to_string(allergens_tags, ','), 'fr:')
GROUP BY allergens_tags
ORDER BY nb DESC
LIMIT 10
```
```text
┌───────┬───────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────┐
│  nb   │     code      │                                          allergens_tags                                           │
│ int64 │    varchar    │                                             varchar[]                                             │
├───────┼───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
│     3 │ 0064100111257 │ [en:gluten, fr:avoine]                                                                            │
│     2 │ 0061077765667 │ [en:gluten, en:soybeans, fr:avoine]                                                               │
│     1 │ 0774756204905 │ [en:celery, en:gluten, en:milk, en:peanuts, en:sesame-seeds, en:soybeans, fr:citron]              │
│     1 │ 0062639333164 │ [fr:avertissement-peut-contenir-des-noyaux]                                                       │
│     1 │ 0055577105450 │ [en:gluten, en:milk, en:nuts, en:soybeans, fr:avoine]                                             │
│     1 │ 0065633074712 │ [en:peanuts, en:soybeans, fr:avoine]                                                              │
│     1 │ 0071921689568 │ [en:gluten, en:milk, en:soybeans, en:milk, fr:substance-laitiere, en:milk, fr:substance-laitiere] │
│     1 │ 0626114120023 │ [en:gluten, en:orange, fr:avoine]                                                                 │
│     1 │ 0067311020332 │ [fr:ki]                                                                                           │
│     1 │ 0855005872474 │ [en:soybeans, fr:coconut]                                                                         │
├───────┴───────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                         3 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products with peanut allergies
```sql
-- Products with peanut allergies
SELECT
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
allergens_tags
FROM products
WHERE list_contains(allergens_tags, 'en:peanuts') 
OR list_contains(allergens_tags, 'fr:arachides')
LIMIT 10;
```
```text
┌───────────────┬─────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│     code      │                          name                           │                             allergens_tags                             │
│    varchar    │                         varchar                         │                               varchar[]                                │
├───────────────┼─────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 0018627100997 │ Dark chocolate Almond and Sea salt                      │ [en:gluten, en:nuts, en:peanuts, en:soybeans]                          │
│ 0018627104858 │ Cherry Dark Chocolate                                   │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans]                 │
│ 0031146033324 │ Zha Wang Chajang noodle dish with oyster flavored sauce │ [en:crustaceans, en:fish, en:gluten, en:milk, en:peanuts, en:soybeans] │
│ 0055000681834 │ Strawberry Ice Cream                                    │ [en:eggs, en:milk, en:nuts, en:peanuts]                                │
│ 0055577110218 │ Barres tendres au quinoa chocolat et noix               │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans, fr:avoine]      │
│ 0055653170259 │ Ultimate Maple Creme Filled Cookies                     │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans]                 │
│ 0055653670506 │ Vivant Italian Bruschetta                               │ [en:celery, en:gluten, en:milk, en:peanuts, en:soybeans]               │
│ 0055742348279 │ Smooth Peanut Butter                                    │ [en:peanuts, en:soybeans]                                              │
│ 0055742539462 │ Naturally Simple Smooth Peanut Butter                   │ [en:peanuts]                                                           │
│ 0056600620742 │ Reese's  minis                                          │ [en:milk, en:peanuts, en:soybeans]                                     │
├───────────────┴─────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                3 columns │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Number of products per NOVA group
```sql
-- Number of products per NOVA group
SELECT nova_group, count(*) AS count
FROM products
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;
```
```text
┌────────────┬───────┐
│ nova_group │ count │
│   int32    │ int64 │
├────────────┼───────┤
│          1 │  1278 │
│          2 │  1349 │
│          3 │  1783 │
│          4 │ 10317 │
└────────────┴───────┘
```
### Average Nutri-Score by brand with more than 100 products
```sql
-- Average Nutri-Score by brand with more than 100 products
SELECT 
    unnest AS brand,
    avg(nutriscore_score) AS avg_score,
    count(*) AS products
FROM products,
     unnest(brands_tags) AS unnest
GROUP BY brand
HAVING count(*) > 100
ORDER BY avg_score;
```
```text
┌────────────────┬────────────────────┬──────────┐
│     brand      │     avg_score      │ products │
│    varchar     │       double       │  int64   │
├────────────────┼────────────────────┼──────────┤
│ bob-s-red-mill │              0.375 │      102 │
│ danone         │               1.66 │      113 │
│ liberte        │ 2.9523809523809526 │      130 │
│ naturalia      │ 3.1666666666666665 │      118 │
│ prana          │  4.894736842105263 │      102 │
│ del-monte      │  5.071428571428571 │      104 │
│ starbucks      │  5.785714285714286 │      107 │
│ cedar          │            6.09375 │      156 │
│ ilios          │  6.142857142857143 │      111 │
│ metro          │  6.885714285714286 │      151 │
│   ·            │          ·         │       ·  │
│   ·            │          ·         │       ·  │
│   ·            │          ·         │       ·  │
│ christie       │  15.51923076923077 │      157 │
│ club-house     │  15.88888888888889 │      173 │
│ knorr          │            16.8125 │      140 │
│ kraft          │ 17.552083333333332 │      248 │
│ dare           │ 18.945205479452056 │      209 │
│ nestle         │  21.62406015037594 │      375 │
│ leclerc        │               22.6 │      183 │
│ lindt          │ 25.589473684210525 │      179 │
│ hershey-s      │ 28.457142857142856 │      129 │
│ cadbury        │ 30.678571428571427 │      104 │
├────────────────┴────────────────────┴──────────┤
│ 41 rows (20 shown)                   3 columns │
└────────────────────────────────────────────────┘
```
### Products without palm oil and good Nutri-Score
```sql
-- Products without palm oil and good Nutri-Score
SELECT code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    nutriscore_grade
FROM products 
WHERE ingredients_from_palm_oil_n = 0
AND nutriscore_grade IN ('a','b')
LIMIT 10;
```
```text
┌───────────────┬────────────────────────────────────┬──────────────────┐
│     code      │                name                │ nutriscore_grade │
│    varchar    │              varchar               │     varchar      │
├───────────────┼────────────────────────────────────┼──────────────────┤
│ 0030000012000 │ Quick 1-minute Oats imp            │ a                │
│ 0033383653259 │ Celery                             │ a                │
│ 0040822027045 │ Classic Hummus                     │ a                │
│ 0041390050039 │ Panko                              │ a                │
│ 0041508963985 │ Carbonated natural mineral water   │ a                │
│ 0051651092869 │ Beurre d'amandes                   │ a                │
│ 0052603054379 │ Low Sodium Organic Vegetable Broth │ a                │
│ 0055577101018 │ Large Flake Oats (Canada)          │ a                │
│ 0055577102053 │ 1-Minute Oats (Canada)             │ a                │
│ 0055577102459 │ Oat Bran                           │ a                │
├───────────────┴────────────────────────────────────┴──────────────────┤
│ 10 rows                                                     3 columns │
└───────────────────────────────────────────────────────────────────────┘
```
### Products by ecoscore grade
```sql
-- Products by ecoscore grade
SELECT 
    ecoscore_grade,
    count(*) as count,
    avg(ecoscore_score) as avg_score
FROM products
WHERE ecoscore_grade IS NOT NULL
GROUP BY ecoscore_grade
ORDER BY avg_score DESC;
```
```text
┌────────────────┬───────┬────────────────────┐
│ ecoscore_grade │ count │     avg_score      │
│    varchar     │ int64 │       double       │
├────────────────┼───────┼────────────────────┤
│ a-plus         │   159 │  95.12578616352201 │
│ a              │  1664 │   78.6454326923077 │
│ b              │  3088 │  68.37402849740933 │
│ c              │  1791 │  52.03740926856505 │
│ d              │  2403 │ 37.943820224719104 │
│ e              │  1829 │  21.74302897758338 │
│ f              │   773 │ 3.4139715394566625 │
│ unknown        │ 79208 │               NULL │
│ not-applicable │   825 │               NULL │
└────────────────┴───────┴────────────────────┘
```
### Products with palm oil
```sql
-- Products with palm oil
SELECT 
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    ingredients_from_palm_oil_n
FROM products 
WHERE ingredients_from_palm_oil_n > 0;
```
```text
┌───────────────┬─────────────────────────────────────────────┬─────────────────────────────┐
│     code      │                    name                     │ ingredients_from_palm_oil_n │
│    varchar    │                   varchar                   │            int32            │
├───────────────┼─────────────────────────────────────────────┼─────────────────────────────┤
│ 0012009012168 │ Chef d'oeuf™avec fromage sur muffin anglais │                           1 │
│ 00109031      │ Crispy Crunchy Oatmeal Raisin Cookies       │                           1 │
│ 0051651293716 │ Tartinade aux amandes et au Chocolat noir   │                           1 │
│ 0055577109632 │ Chewy Raspberry Fruit Crumble Granola Bars  │                           1 │
│ 0055577110218 │ Barres tendres au quinoa chocolat et noix   │                           1 │
│ 0055598977609 │ Mini Chocolatine                            │                           1 │
│ 0055742528411 │ Biscuit avoine et raisins secs              │                           1 │
│ 0056600620742 │ Reese's  minis                              │                           1 │
│ 0056600816190 │ Twists torsades                             │                           1 │
│ 0056600902053 │ Tartinades Chocolat et Beurre d'Arachides   │                           1 │
│       ·       │            ·                                │                           · │
│       ·       │            ·                                │                           · │
│       ·       │            ·                                │                           · │
│ 0008563995085 │ Belgium Coconut Cookies                     │                           1 │
│ 69905971      │ caramel                                     │                           1 │
│ 0006120001216 │ caramilk                                    │                           1 │
│ 0006840036409 │ becel margarine                             │                           1 │
│ 09000439      │ Biscuits miniatures pépites de chocolat     │                           1 │
│ 09000530      │ Margarine                                   │                           1 │
│ 09000597      │ Tartinade aux noisettes                     │                           1 │
│ 09001102      │ Biscuits sandwich canne de bonbon           │                           1 │
│ 09001184      │ Assortiment de biscuits                     │                           1 │
│ 00290616      │ Salade Cesar                                │                           1 │
├───────────────┴─────────────────────────────────────────────┴─────────────────────────────┤
│ 482 rows (20 shown)                                                             3 columns │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products with most ingredients
```sql
-- Products with most ingredients
SELECT 
    code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    ingredients_n
FROM products
WHERE ingredients_n IS NOT NULL
ORDER BY ingredients_n DESC
LIMIT 10;
```
```text
┌───────────────┬──────────────────────────────────┬───────────────┐
│     code      │               name               │ ingredients_n │
│    varchar    │             varchar              │     int32     │
├───────────────┼──────────────────────────────────┼───────────────┤
│ 06481016      │ Kellogg’s nutri grain            │           289 │
│ 8904004440263 │ Punnjabi Samosa                  │           188 │
│ 0658010120449 │ All in one nutritional shake     │           185 │
│ 0066701010328 │ Millefeuille                     │           165 │
│ 0628456570054 │ Pizza internationale Mike's      │           163 │
│ 0670452777074 │ Red Dragon Roll                  │           156 │
│ 0055577331071 │ Chewy fruity fun                 │           151 │
│ 0065000570106 │ Chocolat chaud                   │           147 │
│ 0060383647384 │ Cheese H'ors Douevres Collection │           146 │
│ 8801073142961 │ Kimchi Budak                     │           143 │
├───────────────┴──────────────────────────────────┴───────────────┤
│ 10 rows                                                3 columns │
└──────────────────────────────────────────────────────────────────┘
```
### Most common vitamins
```sql
-- Most common vitamins
SELECT 
    unnest AS vitamin,
    count(*) AS count
FROM products,
    unnest(vitamins_tags) AS unnest
GROUP BY vitamin
ORDER BY count DESC;
```
```text
┌─────────────────────────────┬───────┐
│           vitamin           │ count │
│           varchar           │ int64 │
├─────────────────────────────┼───────┤
│ en:l-ascorbic-acid          │   852 │
│ en:riboflavin               │   486 │
│ en:niacin                   │   460 │
│ en:pyridoxine-hydrochloride │   449 │
│ en:folic-acid               │   445 │
│ en:vitamin-c                │   370 │
│ en:retinyl-palmitate        │   360 │
│ en:cholecalciferol          │   338 │
│ en:vitamin-b6               │   309 │
│ en:vitamin-b12              │   307 │
│       ·                     │     · │
│       ·                     │     · │
│       ·                     │     · │
│ en:phylloquinone            │    10 │
│ en:nicotinamide             │    10 │
│ en:d-biotin                 │     7 │
│ en:vitamin-k                │     6 │
│ en:calcium-l-ascorbate      │     5 │
│ en:d-alpha-tocopherol       │     4 │
│ en:folacin                  │     2 │
│ en:pyridoxine-dipalmitate   │     1 │
│ en:vitamin-b8               │     1 │
│ en:nicotinic-acid           │     1 │
├─────────────────────────────┴───────┤
│ 37 rows (20 shown)        2 columns │
└─────────────────────────────────────┘
```
### Products by serving size
```sql
-- Products by serving size
SELECT serving_size, count(*) AS count
FROM products
WHERE serving_size IS NOT NULL
GROUP BY serving_size
ORDER BY count DESC
LIMIT 10;
```
```text
┌───────────────────┬───────┐
│   serving_size    │ count │
│      varchar      │ int64 │
├───────────────────┼───────┤
│ 30 g              │   393 │
│ 1 portion (100 g) │   380 │
│ 40 g              │   363 │
│ 50 g              │   275 │
│ 30g               │   200 │
│ 250 mL            │   184 │
│ 85 g              │   166 │
│ 188 mL            │   163 │
│ 355 mL            │   160 │
│ 100 g             │   157 │
├───────────────────┴───────┤
│ 10 rows         2 columns │
└───────────────────────────┘
```
### Most used labels
```sql
-- Most used labels
SELECT 
    unnest AS label,
    count(*) AS count
FROM products,
    unnest(labels_tags) as unnest
GROUP BY label
ORDER BY count DESC
LIMIT 10;
```
```text
┌──────────────────────────┬───────┐
│          label           │ count │
│         varchar          │ int64 │
├──────────────────────────┼───────┤
│ en:no-gluten             │  7568 │
│ en:no-gmos               │  4717 │
│ en:non-gmo-project       │  4366 │
│ en:organic               │  4246 │
│ en:vegetarian            │  3846 │
│ en:vegan                 │  3646 │
│ en:kosher                │  3605 │
│ en:no-colorings          │  3176 │
│ en:canada-organic        │  2653 │
│ en:no-artificial-flavors │  2152 │
├──────────────────────────┴───────┤
│ 10 rows                2 columns │
└──────────────────────────────────┘
```
### Organic products
```sql
-- Organic products
SELECT code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
FROM products
WHERE list_contains(labels_tags, 'en:organic')
LIMIT 10;
```
```text
┌───────────────┬─────────────────────────────────────────────────────────────┐
│     code      │                            name                             │
│    varchar    │                           varchar                           │
├───────────────┼─────────────────────────────────────────────────────────────┤
│ 0008577002786 │ Organic Vermont Maple Syrup Grade A Dark Color Robust Taste │
│ 0012511472313 │ Organic Blue Agave                                          │
│ 0018627597513 │ Whole Wheat Cinnamon Harvest                                │
│ 0025293600713 │ Soy Original Organic Fortified Beverage                     │
│ 0025293600737 │ Soy Vanilla Organic Beverage                                │
│ 0030963304013 │ Mlo sport nutrition                                         │
│ 0033776011840 │ Earth Balance Organic Whipped                               │
│ 0036192127157 │ Organic Pure Lemon Juice                                    │
│ 0041143029336 │ Raisins secs biologiques                                    │
│ 0049568289465 │ Organic Vegenaise                                           │
├───────────────┴─────────────────────────────────────────────────────────────┤
│ 10 rows                                                           2 columns │
└─────────────────────────────────────────────────────────────────────────────┘
```
### Products by store
```sql
-- Products by store
SELECT 
    unnest as store_name,
    count(*) as count
FROM products,
    unnest(stores_tags) as unnest
GROUP BY store_name
ORDER BY count DESC
LIMIT 5;
```
```text
┌──────────────────────────┬───────┐
│        store_name        │ count │
│         varchar          │ int64 │
├──────────────────────────┼───────┤
│ walmart                  │  1646 │
│ safeway                  │   946 │
│ costco                   │   798 │
│ real-canadian-superstore │   685 │
│ dollarama                │   404 │
└──────────────────────────┴───────┘
```
### Complete vs incomplete products
```sql
-- Complete vs incomplete products
SELECT 
    complete,
    count(*) as count,
    avg(completeness) as avg_completeness
FROM products
GROUP BY complete;
```
```text
┌──────────┬───────┬────────────────────┐
│ complete │ count │  avg_completeness  │
│  int32   │ int64 │       double       │
├──────────┼───────┼────────────────────┤
│        0 │ 94634 │ 0.3689723067026311 │
│        1 │   168 │ 0.9315476027272996 │
└──────────┴───────┴────────────────────┘
```
### Products by food group
```sql
-- Products by food group
SELECT 
    unnest AS food_group,
    count(*) AS count
FROM products,
    unnest(food_groups_tags) AS unnest
GROUP BY food_group
ORDER BY count DESC;
```
```text
┌───────────────────────────────┬───────┐
│          food_group           │ count │
│            varchar            │ int64 │
├───────────────────────────────┼───────┤
│ en:sugary-snacks              │  3834 │
│ en:cereals-and-potatoes       │  2968 │
│ en:fats-and-sauces            │  2118 │
│ en:beverages                  │  1958 │
│ en:milk-and-dairy-products    │  1699 │
│ en:sweets                     │  1695 │
│ en:dressings-and-sauces       │  1550 │
│ en:biscuits-and-cakes         │  1422 │
│ en:fruits-and-vegetables      │  1314 │
│ en:cereals                    │  1263 │
│     ·                         │    ·  │
│     ·                         │    ·  │
│     ·                         │    ·  │
│ en:pastries                   │   152 │
│ en:dried-fruits               │   149 │
│ en:eggs                       │    79 │
│ en:fruit-juices               │    78 │
│ en:potatoes                   │    75 │
│ en:waters-and-flavored-waters │    66 │
│ en:dairy-desserts             │    48 │
│ en:soups                      │    46 │
│ en:lean-fish                  │    10 │
│ en:fruit-nectars              │     6 │
├───────────────────────────────┴───────┤
│ 51 rows (20 shown)          2 columns │
└───────────────────────────────────────┘
```
### Recently added products
```sql
-- Recently added products
SELECT code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    to_timestamp(created_t) AS added_date
FROM products
WHERE created_t IS NOT NULL
ORDER BY created_t DESC
LIMIT 10;
```
```text
┌───────────────┬─────────────────────────────────────────┬──────────────────────────┐
│     code      │                  name                   │        added_date        │
│    varchar    │                 varchar                 │ timestamp with time zone │
├───────────────┼─────────────────────────────────────────┼──────────────────────────┤
│ 0665553228235 │ Carbion blue bomb pop with electrolytes │ 2025-01-22 03:37:31-05   │
│ 0067400826159 │ Camembert Cheese                        │ 2025-01-22 02:16:16-05   │
│ 8852023668895 │ Peanuts BBQ Flavour                     │ 2025-01-22 00:05:14-05   │
│ 0060410079256 │ Lays Cheesy Garlic Bread                │ 2025-01-21 23:21:08-05   │
│ 0316114104504 │ Thin Tortilla                           │ 2025-01-21 22:37:47-05   │
│ 0850006067527 │ Cauliflower Rice                        │ 2025-01-21 22:12:06-05   │
│ 0062273552358 │ Frozen Green Peas                       │ 2025-01-21 21:14:49-05   │
│ 0627987436075 │ Margherita pizza                        │ 2025-01-21 21:13:05-05   │
│ 0057316192936 │ Pitted Green Olives                     │ 2025-01-21 19:50:48-05   │
│ 0217208605498 │ Chicken Salad Sandwich - White          │ 2025-01-21 18:59:12-05   │
├───────────────┴─────────────────────────────────────────┴──────────────────────────┤
│ 10 rows                                                                  3 columns │
└────────────────────────────────────────────────────────────────────────────────────┘
```
### Top 10 best contributors in Open Food Facts
```sql
-- Top 10 best contributors in Open Food Facts
SELECT creator, count(*) AS count
FROM products
GROUP BY creator
ORDER BY count DESC
LIMIT 10;
```
```text
┌────────────────────────────┬───────┐
│          creator           │ count │
│          varchar           │ int64 │
├────────────────────────────┼───────┤
│ kiliweb                    │ 69800 │
│ macrofactor                │  8312 │
│ openfoodfacts-contributors │  6015 │
│ inf                        │  2135 │
│ anonymous-s7co2zv64u       │   998 │
│ smoothie-app               │   925 │
│ waistline-app              │   809 │
│ foodless                   │   691 │
│ date-limite-app            │   422 │
│ halal-app-chakib           │   417 │
├────────────────────────────┴───────┤
│ 10 rows                  2 columns │
└────────────────────────────────────┘
```
### Number of added products per year
```sql
-- Number of added products per year
SELECT
    entry_dates_tags[3] AS year, count(*) AS count
FROM products
GROUP BY year
ORDER BY year DESC;
```
```text
┌─────────┬───────┐
│  year   │ count │
│ varchar │ int64 │
├─────────┼───────┤
│ 2025    │  1312 │
│ 2024    │  9429 │
│ 2023    │  9955 │
│ 2022    │ 31527 │
│ 2021    │ 19724 │
│ 2020    │ 15269 │
│ 2019    │  2716 │
│ 2018    │  3294 │
│ 2017    │   561 │
│ 2016    │   467 │
│ 2015    │   335 │
│ 2014    │    84 │
│ 2013    │    94 │
│ 2012    │    35 │
├─────────┴───────┤
│     14 rows     │
└─────────────────┘
```
### Products containing 'café', 'cafe', or 'coffee' in their generic name
```sql
-- Products containing 'café', 'cafe', or 'coffee' in their generic name
SELECT product_name, generic_name
FROM products
WHERE lower(generic_name::VARCHAR) LIKE '%café%'
   OR lower(generic_name::VARCHAR) LIKE '%cafe%'
   OR lower(generic_name::VARCHAR) LIKE '%coffee%';
```
```text
┌──────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     product_name     │                                                                                generic_name                                                                                │
│ struct(lang varcha…  │                                                                   struct(lang varchar, "text" varchar)[]                                                                   │
├──────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Coffee beverage - McCafé Frappé Caramel}, {'lang': fr, 'text': Coffee beverage - McCafé Frappé Caramel}]                                           │
│ [{'lang': main, 't…  │ [{'lang': en, 'text': Nescafe Taster's Choice Classic Instant Coffee}]                                                                                                     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Vanilla Fortified Coffee Drink}, {'lang': en, 'text': Vanilla Fortified Coffee Drink}]                                                             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Folgers Classic Roast Coffee}, {'lang': en, 'text': Folgers Classic Roast Coffee}]                                                                 │
│ [{'lang': main, 't…  │ [{'lang': fr, 'text': Boissons énergétiques au café}]                                                                                                                      │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': mezcla para preparar café capiccino moca}, {'lang': es, 'text': mezcla para preparar café capiccino moca}]                                         │
│ [{'lang': main, 't…  │ [{'lang': en, 'text': LAYERED DESSERT WITH SPONGE CAKE SOAKED IN COFFEE, MASCARPONE CREAM AND COCOA POWDER}]                                                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Almond Beverage for Coffee}, {'lang': en, 'text': Almond Beverage for Coffee}]                                                                     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 1% M.F. Coffee Partly Skimmed Milk}, {'lang': en, 'text': 1% M.F. Coffee Partly Skimmed Milk}]                                                     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Coffee Syrup}, {'lang': fr, 'text': Coffee Syrup}]                                                                                                 │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': lait sucré, crème à cafe}, {'lang': fr, 'text': lait sucré, crème à cafe}]                                                                         │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': French Vanilla Fortified Coffee Drink}, {'lang': en, 'text': French Vanilla Fortified Coffee Drink}]                                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Alternating layers of cheesecake and coffee ice cream with espresso sauce and crispy layers made with milk chocolate}, {'lang': en, 'text': Alte…  │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Caffé Mocha Fortified Coffee Drink}, {'lang': en, 'text': Caffé Mocha Fortified Coffee Drink}]                                                     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Pure cream blended with coffee brewed from Brazilian beans}, {'lang': en, 'text': Pure cream blended with coffee brewed from Brazilian beans}]     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Organic Fair Trade Chocolate with Cracked Coffee Beans}, {'lang': en, 'text': Organic Fair Trade Chocolate with Cracked Coffee Beans}]             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Coffee light ice cream with espresso swirls and chocolate cookies}, {'lang': en, 'text': Coffee light ice cream with espresso swirls and chocola…  │
├──────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 17 rows                                                                                                                                                                                 2 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Find products with all ingredients marked as vegan (no non-vegan or maybe-vegan ingredients)
```sql
-- Find products with all ingredients marked as vegan (no non-vegan or maybe-vegan ingredients)
-- The ingredients column contains a JSON array where each ingredient has a "vegan" property
-- that can be "yes", "no", or "maybe". We extract and clean the "text" field of each ingredient.
--
-- Example of ingredients JSON structure:
-- [{"text": "water", "vegan": "yes"}, {"text": "sugar", "vegan": "yes"}]
--
-- The query:
-- 1. Filters for products with only vegan ingredients using LIKE on the raw JSON
-- 2. Extracts the text field for each ingredient using json_extract
-- 3. Cleans up the extracted text by removing brackets and quotes
-- 4. Returns the brand and a comma-separated list of ingredients
WITH ingredient_array AS (
    SELECT 
        brands,
        TRY_CAST(ingredients AS JSON) AS ingredients_json
    FROM products
    WHERE ingredients IS NOT NULL
    AND ingredients != '[]'
    AND ingredients LIKE '%"vegan":"yes"%'    -- Has at least one vegan ingredient
    AND NOT ingredients LIKE '%"vegan":"no"%'  -- No non-vegan ingredients
    AND NOT ingredients LIKE '%"vegan":"maybe"%' -- No maybe-vegan ingredients
),
clean_ingredients AS (
    SELECT 
        brands,
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                json_extract(ingredients_json, '$[*].text')::VARCHAR,
                '[\[\]]',
                ''
            ),
            '"',
            ''
        ) as ingredients_list
    FROM ingredient_array
)
SELECT 
    brands,
    ingredients_list
FROM clean_ingredients
WHERE LENGTH(ingredients_list) > 0
LIMIT 10;
```
```text
┌────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           brands                           │                                                           ingredients_list                                                           │
│                          varchar                           │                                                               varchar                                                                │
├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ usda organic Butternut Mountain Farm,Butternut Mountain …  │ maple syrup"]                                                                                                                        │
│ Wel-Pac                                                    │ Ginger", "water", "salt", "acetic acid", "citric acid", "aspartame", "potassium sorbate", "and fd&c red no", "40"]                   │
│ Aroy d,Aroy-D                                              │ Eau", "lychee", "sucre", "régulateur d'acidité"]                                                                                     │
│ Aroy-D,aroy                                                │ COCONUT", "WATER"]                                                                                                                   │
│ Foco                                                       │ natural coconut water"]                                                                                                              │
│ Casa Fiesta                                                │ Green chili peppers", "water", "salt", "citric acid"]                                                                                │
│ Larabar                                                    │ Dates", "coconut", "Cashews", "Almonds"]                                                                                             │
│ Clément Faugier                                            │ Châtaignes", "sucre", "marrons glacés", "sirop de glucose", "eau", "extrait naturel de vanille"]                                     │
│ Clément Faugier                                            │ Châtaignes", "sucre", "marrons glacés", "sirop de glucose", "eau", "extrait de vanille Madagascar"]                                  │
│ Sriracha                                                   │ chili", "sugar", "salt", "garlic", "distilled vinegar", "potassium sorbate", "sodium bisulfite as preservatives", "and xanthan gum"] │
├────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                                                                 2 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
``````sql
SELECT last_editor, COUNT(*) as frequency
FROM products 
WHERE last_editor IS NOT NULL
GROUP BY last_editor
ORDER BY frequency DESC
LIMIT 10;
```
```text
┌───────────────────────────┬───────────┐
│        last_editor        │ frequency │
│          varchar          │   int64   │
├───────────────────────────┼───────────┤
│ kiliweb                   │     32134 │
│ roboto-app                │     13355 │
│ macrofactor               │     10482 │
│ teolemon                  │      3940 │
│ anonymous-s7co2zv64u      │      3302 │
│ org-label-non-gmo-project │      2647 │
│ naruyoko                  │      1990 │
│ navig491                  │      1780 │
│ inf                       │      1736 │
│ segundo                   │      1691 │
├───────────────────────────┴───────────┤
│ 10 rows                     2 columns │
└───────────────────────────────────────┘
``````sql
SELECT 
    COUNT(*) as total_products,
    COUNT(DISTINCT last_editor) as unique_editors,
    COUNT(CASE WHEN last_editor IS NOT NULL THEN 1 END) as products_with_editor
FROM products;
```
```text
┌────────────────┬────────────────┬──────────────────────┐
│ total_products │ unique_editors │ products_with_editor │
│     int64      │     int64      │        int64         │
├────────────────┼────────────────┼──────────────────────┤
│          94802 │           1515 │                93157 │
└────────────────┴────────────────┴──────────────────────┘
```
### Find popular products (>100 scans) with good nutrition score (A or B)
```sql
-- Find popular products (>100 scans) with good nutrition score (A or B)
SELECT 
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    scans_n,
    nutriscore_grade
FROM products
WHERE scans_n > 100 
AND nutriscore_grade IN ('a', 'b')
ORDER BY scans_n DESC
LIMIT 10;
```
```text
┌───────────────┬───────────────────────┬─────────┬──────────────────┐
│     code      │         name          │ scans_n │ nutriscore_grade │
│    varchar    │        varchar        │  int32  │     varchar      │
├───────────────┼───────────────────────┼─────────┼──────────────────┤
│ 80042556      │ Pulpe fine de tomates │     409 │ a                │
│ 8076800376999 │ Lasagne all'uovo      │     141 │ a                │
└───────────────┴───────────────────────┴─────────┴──────────────────┘
```
### Average number of additives by brand (for brands with >50 products)
```sql
-- Average number of additives by brand (for brands with >50 products)
SELECT 
    unnest AS brand,
    AVG(additives_n) as avg_additives,
    COUNT(*) as total_products
FROM products,
    unnest(brands_tags) AS unnest
WHERE additives_n IS NOT NULL
GROUP BY brand
HAVING COUNT(*) > 50
ORDER BY avg_additives DESC
LIMIT 10;
```
```text
┌───────────────┬────────────────────┬────────────────┐
│     brand     │   avg_additives    │ total_products │
│    varchar    │       double       │     int64      │
├───────────────┼────────────────────┼────────────────┤
│ christie      │ 3.3866666666666667 │             75 │
│ dare          │ 3.3536585365853657 │             82 │
│ nestle        │                3.3 │            190 │
│ general-mills │  3.230769230769231 │             78 │
│ kraft         │ 2.6576576576576576 │            111 │
│ lay-s         │ 2.6481481481481484 │             54 │
│ knorr         │ 2.6153846153846154 │             52 │
│ kellogg-s     │ 2.5514018691588785 │            107 │
│ quaker        │  2.539473684210526 │             76 │
│ null          │   2.49290780141844 │            282 │
├───────────────┴────────────────────┴────────────────┤
│ 10 rows                                   3 columns │
└─────────────────────────────────────────────────────┘
```
### Product creation trends by month in 2024
```sql
-- Product creation trends by month in 2024
SELECT 
    DATE_TRUNC('month', to_timestamp(created_t)) AS month,
    COUNT(*) as new_products
FROM products
WHERE created_t >= 1704067200  -- Jan 1, 2024
GROUP BY month
ORDER BY month;
```
```text
┌──────────────────────────┬──────────────┐
│          month           │ new_products │
│ timestamp with time zone │    int64     │
├──────────────────────────┼──────────────┤
│ 2023-12-01 00:00:00-05   │            1 │
│ 2024-01-01 00:00:00-05   │          116 │
│ 2024-02-01 00:00:00-05   │          169 │
│ 2024-03-01 00:00:00-05   │          218 │
│ 2024-04-01 00:00:00-04   │          678 │
│ 2024-05-01 00:00:00-04   │          830 │
│ 2024-06-01 00:00:00-04   │         1165 │
│ 2024-07-01 00:00:00-04   │          951 │
│ 2024-08-01 00:00:00-04   │          773 │
│ 2024-09-01 00:00:00-04   │         1046 │
│ 2024-10-01 00:00:00-04   │         1138 │
│ 2024-11-01 00:00:00-04   │         1245 │
│ 2024-12-01 00:00:00-05   │         1105 │
│ 2025-01-01 00:00:00-05   │         1306 │
├──────────────────────────┴──────────────┤
│ 14 rows                       2 columns │
└─────────────────────────────────────────┘
```
### Products with complete information and images
```sql
-- Products with complete information and images
SELECT 
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    completeness
FROM products
WHERE complete = 1 
AND images IS NOT NULL
AND completeness > 0.9
ORDER BY completeness DESC
LIMIT 10;
```
```text
┌───────────────┬───────────────────────────────────────────────────────────┬──────────────┐
│     code      │                           name                            │ completeness │
│    varchar    │                          varchar                          │    float     │
├───────────────┼───────────────────────────────────────────────────────────┼──────────────┤
│ 0025293001503 │ Almond, Unsweetened Beverage,                             │          1.1 │
│ 26043579      │ Maïs                                                      │          1.1 │
│ 3245390084422 │ Palets bretons                                            │          1.1 │
│ 3560070475711 │ Lait frais demi-écrémé                                    │          1.1 │
│ 5400101173224 │ Petits pois                                               │          1.1 │
│ 7802215505140 │ Costa Choco Chips                                         │          1.1 │
│ 8711327385603 │ CARTE D'OR Glace Crème Glacée Vanille de Madagascar 900ml │          1.1 │
│ 7802215515019 │ Gretel Chocolate                                          │          1.1 │
│ 0022314015174 │ Crème de Marrons de L'Ardèche                             │          1.0 │
│ 0041508963985 │ Carbonated natural mineral water                          │          1.0 │
├───────────────┴───────────────────────────────────────────────────────────┴──────────────┤
│ 10 rows                                                                        3 columns │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```
### Correlation between Nutri-Score and Eco-Score
```sql
-- Correlation between Nutri-Score and Eco-Score
SELECT 
    nutriscore_grade,
    ecoscore_grade,
    COUNT(*) as count
FROM products
WHERE nutriscore_grade IS NOT NULL 
AND ecoscore_grade IS NOT NULL
GROUP BY nutriscore_grade, ecoscore_grade
ORDER BY nutriscore_grade, ecoscore_grade;
```
```text
┌──────────────────┬────────────────┬───────┐
│ nutriscore_grade │ ecoscore_grade │ count │
│     varchar      │    varchar     │ int64 │
├──────────────────┼────────────────┼───────┤
│ a                │ a              │   341 │
│ a                │ a-plus         │    38 │
│ a                │ b              │   252 │
│ a                │ c              │    77 │
│ a                │ d              │   139 │
│ a                │ e              │   188 │
│ a                │ f              │    47 │
│ a                │ not-applicable │   104 │
│ a                │ unknown        │   898 │
│ b                │ a              │   191 │
│ ·                │ ·              │    ·  │
│ ·                │ ·              │    ·  │
│ ·                │ ·              │    ·  │
│ not-applicable   │ unknown        │   343 │
│ unknown          │ a              │   408 │
│ unknown          │ a-plus         │    34 │
│ unknown          │ b              │   660 │
│ unknown          │ c              │   280 │
│ unknown          │ d              │   403 │
│ unknown          │ e              │   278 │
│ unknown          │ f              │   179 │
│ unknown          │ not-applicable │   176 │
│ unknown          │ unknown        │ 72748 │
├──────────────────┴────────────────┴───────┤
│ 63 rows (20 shown)              3 columns │
└───────────────────────────────────────────┘
```
### Average number of ingredients by food group
```sql
-- Average number of ingredients by food group
SELECT 
    unnest AS food_group,
    AVG(ingredients_n) as avg_ingredients,
    MIN(ingredients_n) as min_ingredients,
    MAX(ingredients_n) as max_ingredients
FROM products,
    unnest(food_groups_tags) AS unnest
WHERE ingredients_n IS NOT NULL
GROUP BY food_group
ORDER BY avg_ingredients DESC
LIMIT 10;
```
```text
┌───────────────────────────┬────────────────────┬─────────────────┬─────────────────┐
│        food_group         │  avg_ingredients   │ min_ingredients │ max_ingredients │
│          varchar          │       double       │      int32      │      int32      │
├───────────────────────────┼────────────────────┼─────────────────┼─────────────────┤
│ en:pizza-pies-and-quiches │  43.93478260869565 │               6 │             163 │
│ en:composite-foods        │ 30.296903460837886 │               1 │             163 │
│ en:one-dish-meals         │               30.0 │               1 │             129 │
│ en:biscuits-and-cakes     │ 25.455216016859854 │               1 │             165 │
│ en:pastries               │ 24.854166666666668 │               9 │              58 │
│ en:poultry                │ 23.939393939393938 │               1 │             108 │
│ en:ice-cream              │ 22.489878542510123 │               1 │              69 │
│ en:breakfast-cereals      │ 20.664688427299705 │               1 │              95 │
│ en:sandwiches             │  20.18421052631579 │               2 │              95 │
│ en:bread                  │  19.14782608695652 │               1 │             142 │
├───────────────────────────┴────────────────────┴─────────────────┴─────────────────┤
│ 10 rows                                                                  4 columns │
└────────────────────────────────────────────────────────────────────────────────────┘
```
### Categories with the most products without additives
```sql
-- Categories with the most products without additives
SELECT 
    unnest AS category,
    COUNT(*) as count
FROM products,
    unnest(categories_tags) AS unnest
WHERE additives_n = 0
GROUP BY category
ORDER BY count DESC
LIMIT 10;
```
```text
┌──────────────────────────────────────┬───────┐
│               category               │ count │
│               varchar                │ int64 │
├──────────────────────────────────────┼───────┤
│ en:plant-based-foods-and-beverages   │  2186 │
│ en:plant-based-foods                 │  1987 │
│ en:cereals-and-potatoes              │   657 │
│ en:fruits-and-vegetables-based-foods │   608 │
│ en:cereals-and-their-products        │   475 │
│ en:beverages                         │   475 │
│ en:snacks                            │   473 │
│ en:dairies                           │   384 │
│ en:condiments                        │   340 │
│ en:fruits-based-foods                │   314 │
├──────────────────────────────────────┴───────┤
│ 10 rows                            2 columns │
└──────────────────────────────────────────────┘
```
### Most common conservation conditions
```sql
-- Most common conservation conditions
SELECT 
    unnest AS condition,
    COUNT(*) as count
FROM products,
    unnest(conservation_conditions_tags) AS unnest
GROUP BY condition
ORDER BY count DESC
LIMIT 10;
```

### Products with multiple allergens
```sql
-- Products with multiple allergens
SELECT 
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    ARRAY_LENGTH(allergens_tags) as allergen_count,
    allergens_tags
FROM products
WHERE allergens_tags IS NOT NULL
AND ARRAY_LENGTH(allergens_tags) > 3
ORDER BY ARRAY_LENGTH(allergens_tags) DESC
LIMIT 10;
```
```text
┌───────────────┬──────────────────────┬────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     code      │         name         │ allergen_count │                                                              allergens_tags                                                               │
│    varchar    │       varchar        │     int64      │                                                                 varchar[]                                                                 │
├───────────────┼──────────────────────┼────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0242297115924 │ Quesadillas au pou…  │             11 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:mustard, en:nuts, en:peanuts, en:sesame-seeds, en:soybeans, en:sulphur-dioxid…  │
│ 0883259010194 │ General Tao chicke…  │             11 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:sesame-seeds, en:soybeans, en:sulphur-dioxi…  │
│ 8801073142961 │ Kimchi Budak         │             11 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:peanuts, en:sesame-seeds, en:soybeans]        │
│ 0031146023103 │ Soupe aux nouilles…  │             11 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:peanuts, en:sesame-seeds, en:soybeans]        │
│ 0059491000358 │ Beef flavour insta…  │             10 │ [en:eggs, en:fish, en:gluten, en:milk, en:nuts, en:peanuts, en:sesame-seeds, en:soybeans, en:sulphur-dioxide-and-sulphites, en:shellfish] │
│ 0098308002963 │ Better Than Bouill…  │             10 │ [en:crustaceans, en:soybeans, en:lagosta, en:alho, en:cebola, en:milho, en:paprica, pt:alho, pt:cebola, pt:milho]                         │
│ 0628456830530 │ Tempura chicken br…  │             10 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:mustard, en:nuts, en:sesame-seeds, en:soybeans, en:sulphur-dioxide-and-sulphi…  │
│ 8801073114814 │ Buldak Cream Carbo…  │             10 │ [en:crustaceans, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:peanuts, en:sesame-seeds, en:soybeans]                 │
│ 8801073115088 │ quattro cheese hot…  │             10 │ [en:celery, en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:mustard, en:nuts, en:peanuts, en:soybeans]                           │
│ 0880107310415 │ Sutah Ramen Hot & …  │             10 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:peanuts, en:sesame-seeds]                     │
├───────────────┴──────────────────────┴────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                                                                 4 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Brands distribution by country
```sql
-- Brands distribution by country
SELECT 
    unnest as country,
    COUNT(DISTINCT b.brand) as unique_brands,
    COUNT(*) as total_products
FROM products,
    unnest(countries_tags) as unnest,
    unnest(brands_tags) as b(brand)
GROUP BY country
HAVING COUNT(*) > 100
ORDER BY unique_brands DESC
LIMIT 10;
```
```text
┌──────────────────┬───────────────┬────────────────┐
│     country      │ unique_brands │ total_products │
│     varchar      │     int64     │     int64      │
├──────────────────┼───────────────┼────────────────┤
│ en:canada        │          8995 │          43146 │
│ en:world         │           815 │           3957 │
│ en:france        │           700 │           1363 │
│ en:united-states │           448 │            619 │
│ en:germany       │           167 │            220 │
└──────────────────┴───────────────┴────────────────┘
```
### Products by NOVA group
```sql
-- Products by NOVA group
SELECT nova_group, count(*) AS count
FROM products
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;
```
```text
┌────────────┬───────┐
│ nova_group │ count │
│   int32    │ int64 │
├────────────┼───────┤
│          1 │  1278 │
│          2 │  1349 │
│          3 │  1783 │
│          4 │ 10317 │
└────────────┴───────┘
```
### Products with good Nutri-Score and no palm oil
```sql
-- Products with good Nutri-Score and no palm oil
SELECT code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    nutriscore_grade
FROM products 
WHERE ingredients_from_palm_oil_n = 0
AND nutriscore_grade IN ('a','b')
LIMIT 10;
```
```text
┌───────────────┬────────────────────────────────────┬──────────────────┐
│     code      │                name                │ nutriscore_grade │
│    varchar    │              varchar               │     varchar      │
├───────────────┼────────────────────────────────────┼──────────────────┤
│ 0030000012000 │ Quick 1-minute Oats imp            │ a                │
│ 0033383653259 │ Celery                             │ a                │
│ 0040822027045 │ Classic Hummus                     │ a                │
│ 0041390050039 │ Panko                              │ a                │
│ 0041508963985 │ Carbonated natural mineral water   │ a                │
│ 0051651092869 │ Beurre d'amandes                   │ a                │
│ 0052603054379 │ Low Sodium Organic Vegetable Broth │ a                │
│ 0055577101018 │ Large Flake Oats (Canada)          │ a                │
│ 0055577102053 │ 1-Minute Oats (Canada)             │ a                │
│ 0055577102459 │ Oat Bran                           │ a                │
├───────────────┴────────────────────────────────────┴──────────────────┤
│ 10 rows                                                     3 columns │
└───────────────────────────────────────────────────────────────────────┘
```
### Most common vitamins
```sql
-- Most common vitamins
SELECT 
    unnest AS vitamin,
    count(*) AS count
FROM products,
    unnest(vitamins_tags) AS unnest
GROUP BY vitamin
ORDER BY count DESC;
```
```text
┌─────────────────────────────┬───────┐
│           vitamin           │ count │
│           varchar           │ int64 │
├─────────────────────────────┼───────┤
│ en:l-ascorbic-acid          │   852 │
│ en:riboflavin               │   486 │
│ en:niacin                   │   460 │
│ en:pyridoxine-hydrochloride │   449 │
│ en:folic-acid               │   445 │
│ en:vitamin-c                │   370 │
│ en:retinyl-palmitate        │   360 │
│ en:cholecalciferol          │   338 │
│ en:vitamin-b6               │   309 │
│ en:vitamin-b12              │   307 │
│       ·                     │     · │
│       ·                     │     · │
│       ·                     │     · │
│ en:phylloquinone            │    10 │
│ en:nicotinamide             │    10 │
│ en:d-biotin                 │     7 │
│ en:vitamin-k                │     6 │
│ en:calcium-l-ascorbate      │     5 │
│ en:d-alpha-tocopherol       │     4 │
│ en:folacin                  │     2 │
│ en:nicotinic-acid           │     1 │
│ en:vitamin-b8               │     1 │
│ en:pyridoxine-dipalmitate   │     1 │
├─────────────────────────────┴───────┤
│ 37 rows (20 shown)        2 columns │
└─────────────────────────────────────┘
```
### Product completeness
```sql
-- Product completeness
SELECT 
    complete,
    count(*) as count,
    avg(completeness) as avg_completeness
FROM products
GROUP BY complete;
```
```text
┌──────────┬───────┬────────────────────┐
│ complete │ count │  avg_completeness  │
│  int32   │ int64 │       double       │
├──────────┼───────┼────────────────────┤
│        0 │ 94634 │ 0.3689723067026311 │
│        1 │   168 │ 0.9315476027272996 │
└──────────┴───────┴────────────────────┘
```
### Product creation trends by month
```sql
-- Product creation trends by month
SELECT 
    DATE_TRUNC('month', to_timestamp(created_t)) AS month,
    COUNT(*) as new_products
FROM products
WHERE created_t >= 1704067200  -- Jan 1, 2024
GROUP BY month
ORDER BY month;
```
```text
┌──────────────────────────┬──────────────┐
│          month           │ new_products │
│ timestamp with time zone │    int64     │
├──────────────────────────┼──────────────┤
│ 2023-12-01 00:00:00-05   │            1 │
│ 2024-01-01 00:00:00-05   │          116 │
│ 2024-02-01 00:00:00-05   │          169 │
│ 2024-03-01 00:00:00-05   │          218 │
│ 2024-04-01 00:00:00-04   │          678 │
│ 2024-05-01 00:00:00-04   │          830 │
│ 2024-06-01 00:00:00-04   │         1165 │
│ 2024-07-01 00:00:00-04   │          951 │
│ 2024-08-01 00:00:00-04   │          773 │
│ 2024-09-01 00:00:00-04   │         1046 │
│ 2024-10-01 00:00:00-04   │         1138 │
│ 2024-11-01 00:00:00-04   │         1245 │
│ 2024-12-01 00:00:00-05   │         1105 │
│ 2025-01-01 00:00:00-05   │         1306 │
├──────────────────────────┴──────────────┤
│ 14 rows                       2 columns │
└─────────────────────────────────────────┘
```