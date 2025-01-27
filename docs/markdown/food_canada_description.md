# Description de ../data/food_canada.duckdb

- Nombre de lignes: 94,802
- Nombre de colonnes: 109

## additives_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 24
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `0`
  - `1`
  - `0`
  - `4`
  - `12`
  - `0`
  - `8`
  - `3`
  - `4`
  - `4`

## additives_tags
- **Type**: `list`
- **Valeurs uniques**: 4,580
- **Valeurs nulles**: 74,211 (78.28%)
- **Exemples de valeurs**:
  - `[]`
  - `['en:e150c']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:e202', 'en:e260', 'en:e330', 'en:e951']`
  - `['en:e1104', 'en:e200', 'en:e211', 'en:e260', 'en:e282', 'en:e322', 'en:e322i', 'en:e330', 'en:e331', 'en:e341', 'en:e341i', 'en:e466', 'en:e472d', 'en:e510']`
  - `[]`
  - `[]`

## allergens_tags
- **Type**: `list`
- **Valeurs uniques**: 721
- **Valeurs nulles**: 252 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `['en:milk']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:eggs', 'en:gluten', 'en:milk', 'en:soybeans']`
  - `[]`
  - `[]`

## brands_tags
- **Type**: `list`
- **Valeurs uniques**: 9,262
- **Valeurs nulles**: 52,329 (55.20%)
- **Exemples de valeurs**:
  - `['usda-organic-butternut-mountain-farm', 'butternut-mountain-farm']`
  - `['kroger']`
  - `['kroger']`
  - `['ajishima']`
  - `['ajishima']`
  - `['wel-pac']`
  - `['a-w']`
  - `['wholesome']`
  - `['oakrun-farm']`
  - `['annie-s-homegrown', 'annie-s']`

## brands
- **Type**: `STRING`
- **Valeurs uniques**: 10,824
- **Valeurs nulles**: 52,331 (55.20%)
- **Exemples de valeurs**:
  - `usda organic Butternut Mountain Farm,Butternut Mountain Farm`
  - `Kroger`
  - `Kroger`
  - `ajishima`
  - `Ajishima`
  - `Wel-Pac`
  - `A&W`
  - `Wholesome`
  - `Oakrun Farm`
  - `Annie's Homegrown,Annie's`

## categories
- **Type**: `STRING`
- **Valeurs uniques**: 8,184
- **Valeurs nulles**: 72,133 (76.09%)
- **Exemples de valeurs**:
  - `Sweeteners,Syrups,Simple syrups,Maple syrups`
  - `Aliments et boissons à base de végétaux, Aliments d'origine végétale, Céréales et pommes de terre, Produits à tartiner, Pâtes à tartiner végétales, Produits à tartiner salés, Produits d'élevages, Pains, Œufs, Pains spéciaux, Pains Muffins, Pâtés végétaux, Fromage cheddar fondu`
  - `Sweeteners, Syrups, Simple syrups, Agave syrups`
  - `Snacks, Snacks sucrés, Biscuits et gâteaux, Gâteaux, Gâteaux au chocolat`
  - `Plant-based foods and beverages, Plant-based foods, Cereals and potatoes, Cereals and their products, Pastas`
  - `Snacks, Salty snacks`
  - `Snacks, Salty snacks, Appetizers, Crackers, Small Crackers`
  - `Snacks, Snacks salés, Amuse-gueules, Biscuits apéritifs`
  - `Plant-based foods and beverages, Plant-based foods, Breakfasts, Cereals and potatoes, Cereals and their products, Breakfast cereals, Extruded cereals`
  - `Snacks,Sweet snacks,Bars,Cereal bars`

## categories_tags
- **Type**: `list`
- **Valeurs uniques**: 5,829
- **Valeurs nulles**: 71,913 (75.86%)
- **Exemples de valeurs**:
  - `['en:sweeteners', 'en:syrups', 'en:simple-syrups', 'en:maple-syrups']`
  - `[]`
  - `['en:plant-based-foods-and-beverages', 'en:plant-based-foods', 'en:cereals-and-potatoes', 'en:spreads', 'en:plant-based-spreads', 'en:salted-spreads', 'en:farming-products', 'en:breads', 'en:eggs', 'en:special-breads', 'en:english-muffins', 'en:plant-based-pates', 'fr:fromage-cheddar-fondu']`
  - `['en:sweeteners', 'en:syrups', 'en:simple-syrups', 'en:agave-syrups']`
  - `['en:snacks', 'en:sweet-snacks', 'en:biscuits-and-cakes', 'en:cakes', 'en:chocolate-cakes']`
  - `['en:plant-based-foods-and-beverages', 'en:plant-based-foods', 'en:cereals-and-potatoes', 'en:cereals-and-their-products', 'en:pastas']`
  - `['en:snacks', 'en:salty-snacks']`
  - `['en:snacks', 'en:salty-snacks', 'en:appetizers', 'en:crackers', 'en:small-crackers']`
  - `['en:snacks', 'en:salty-snacks', 'en:appetizers', 'en:crackers']`
  - `['en:plant-based-foods-and-beverages', 'en:plant-based-foods', 'en:breakfasts', 'en:cereals-and-potatoes', 'en:cereals-and-their-products', 'en:breakfast-cereals', 'en:extruded-cereals']`

## checkers_tags
- **Type**: `list`
- **Valeurs uniques**: 10
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## ciqual_food_name_tags
- **Type**: `list`
- **Valeurs uniques**: 275
- **Valeurs nulles**: 80,059 (84.45%)
- **Exemples de valeurs**:
  - `['syrup-maple']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`

## cities_tags
- **Type**: `list`
- **Valeurs uniques**: 54
- **Valeurs nulles**: 84,655 (89.30%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## code
- **Type**: `STRING`
- **Valeurs uniques**: 94,802
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `0008577002786`
  - `0011110020758`
  - `0011110416469`
  - `0011152156842`
  - `0011152223131`
  - `0011152223162`
  - `0011152254999`
  - `0012009012168`
  - `0012354087774`
  - `0012502638919`

## compared_to_category
- **Type**: `STRING`
- **Valeurs uniques**: 2,446
- **Valeurs nulles**: 73,777 (77.82%)
- **Exemples de valeurs**:
  - `en:maple-syrups`
  - `en:plant-based-pates`
  - `en:agave-syrups`
  - `en:chocolate-cakes`
  - `en:pastas`
  - `en:salty-snacks`
  - `en:small-crackers`
  - `en:crackers`
  - `en:extruded-cereals`
  - `en:cereal-bars`

## complete
- **Type**: `NUMBER`
- **Valeurs uniques**: 2
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`

## completeness
- **Type**: `NUMBER`
- **Valeurs uniques**: 56
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `0.6625000238418579`
  - `0.574999988079071`
  - `0.4625000059604645`
  - `0.375`
  - `0.4749999940395355`
  - `0.574999988079071`
  - `0.4749999940395355`
  - `0.7875000238418579`
  - `0.0625`
  - `0.05000000074505806`

## correctors_tags
- **Type**: `list`
- **Valeurs uniques**: 15,720
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['usda-ndb-import', 'teolemon', 'fix-missing-lang-bot', 'org-database-usda', 'foodvisor', 'org-label-non-gmo-project', 'fighter-food-facts']`
  - `['openfoodfacts-contributors']`
  - `['trevorpetersen', 'openfoodfacts-contributors']`
  - `['tacite-mass-editor', 'kiliweb', 'yuka.sY2b0xO6T85zoF3NwEKvlm5VCsbjqDTFLjzfqHelxdefBYCzRNFb4rPGPKg']`
  - `['qingcanli', 'yuka.sY2b0xO6T85zoF3NwEKvlmBfQoH3vyrcGi7jvUmVn_GgBJztQNBvxNLYHqs', 'kiliweb']`
  - `['yuka.YmJ0Y0NvQVQvdndTZzg4bitTemMyZnRyd0pqNWUyYUtPckVOSWc9PQ', 'openfoodfacts-contributors']`
  - `['yuka.YUswdE40OFJuOGNNZ3MxazBoYUZvK3BwLzhDbmNtMjlJckFLSWc9PQ', 'date-limite-app']`
  - `['b7', 'gmathez', 'packbot']`
  - `['openfoodfacts-contributors']`
  - `['openfoodfacts-contributors']`

## countries_tags
- **Type**: `list`
- **Valeurs uniques**: 247
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['en:canada', 'en:united-states']`
  - `['en:canada']`
  - `['en:canada']`
  - `['en:canada']`
  - `['en:canada']`
  - `['en:canada']`
  - `['en:canada', 'en:united-states']`
  - `['en:canada']`
  - `['en:canada']`
  - `['en:canada']`

## created_t
- **Type**: `NUMBER`
- **Valeurs uniques**: 94,725
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `1460234918`
  - `1521609622`
  - `1494699730`
  - `1448509667`
  - `1521387208`
  - `1519614334`
  - `1489061632`
  - `1480703725`
  - `1490826795`
  - `1525644344`

## creator
- **Type**: `STRING`
- **Valeurs uniques**: 842
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `openfoodfacts-contributors`
  - `openfoodfacts-contributors`
  - `trevorpetersen`
  - `date-limite-app`
  - `qingcanli`
  - `openfoodfacts-contributors`
  - `usda-ndb-import`
  - `b7`
  - `openfoodfacts-contributors`
  - `openfoodfacts-contributors`

## data_quality_errors_tags
- **Type**: `list`
- **Valeurs uniques**: 107
- **Valeurs nulles**: 252 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:nutrition-value-total-over-105']`
  - `[]`
  - `['en:energy-value-in-kcal-does-not-match-value-computed-from-other-nutrients']`
  - `[]`
  - `[]`
  - `[]`

## data_quality_info_tags
- **Type**: `list`
- **Valeurs uniques**: 255
- **Valeurs nulles**: 252 (0.27%)
- **Exemples de valeurs**:
  - `['en:no-packaging-data', 'en:ingredients-percent-analysis-ok', 'en:all-but-one-ingredient-with-specified-percent', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ingredients-percent-analysis-ok', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ingredients-percent-analysis-ok', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ingredients-percent-analysis-ok', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:packaging-data-incomplete', 'en:ingredients-percent-analysis-ok', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-known', 'en:food-groups-2-known', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`
  - `['en:no-packaging-data', 'en:ecoscore-extended-data-not-computed', 'en:food-groups-1-unknown', 'en:food-groups-2-unknown', 'en:food-groups-3-unknown']`

## data_quality_warnings_tags
- **Type**: `list`
- **Valeurs uniques**: 4,920
- **Valeurs nulles**: 204 (0.22%)
- **Exemples de valeurs**:
  - `['en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label']`
  - `['en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label']`
  - `['en:serving-quantity-defined-but-quantity-undefined', 'en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label']`
  - `['en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label', 'en:ecoscore-threatened-species-ingredients-missing']`
  - `['en:quantity-not-recognized', 'en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label', 'en:ecoscore-threatened-species-ingredients-missing']`
  - `['en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label', 'en:ecoscore-threatened-species-ingredients-missing']`
  - `['en:energy-value-in-kcal-may-not-match-value-computed-from-other-nutrients', 'en:serving-quantity-defined-but-quantity-undefined', 'en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label']`
  - `['en:ingredients-ingredient-tag-length-greater-than-50', 'en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-production-system-no-label']`
  - `['en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label', 'en:ecoscore-threatened-species-ingredients-missing']`
  - `['en:ecoscore-origins-of-ingredients-origins-are-100-percent-unknown', 'en:ecoscore-packaging-packaging-data-missing', 'en:ecoscore-production-system-no-label', 'en:ecoscore-threatened-species-ingredients-missing']`

## data_sources_tags
- **Type**: `list`
- **Valeurs uniques**: 694
- **Valeurs nulles**: 3,182 (3.36%)
- **Exemples de valeurs**:
  - `['database-usda-ndb', 'databases', 'database-usda', 'labels', 'label-non-gmo-project']`
  - `['app-infood', 'apps']`
  - `['app-yuka', 'apps']`
  - `['app-yuka', 'apps']`
  - `['app-yuka', 'apps', 'app-smoothie-openfoodfacts']`
  - `['app-yuka', 'apps', 'database-usda-ndb', 'databases']`
  - `['app-yuka', 'apps', 'app-smoothie-openfoodfacts', 'labels', 'label-non-gmo-project']`
  - `['app-yuka', 'apps']`
  - `['app-yuka', 'apps', 'app-macrofactor']`
  - `['app-yuka', 'apps', 'app-smoothie-openfoodfacts']`

## ecoscore_data
- **Type**: `STRING`
- **Valeurs uniques**: 91,740
- **Valeurs nulles**: 3,062 (3.23%)
- **Exemples de valeurs**:
  - `{"grade":"b","score":64,"adjustments":{"packaging":{"value":-15,"warning":"packaging_data_missing"},"production_system":{"warning":"no_label","labels":[],"value":0},"origins_of_ingredients":{"values":{"lb":-5,"ua":-5,"no":-5,"cy":-5,"hu":-5,"fo":-5,"tn":-5,"gg":-5,"gr":-5,"ps":-5,"lv":-5,"it":-5,"dk":-5,"bg":-5,"ee":-5,"hr":-5,"il":-5,"ie":-5,"mk":-5,"sk":-5,"fr":-5,"ch":-5,"im":-5,"lu":-5,"mc":-5,"dz":-5,"be":-5,"ba":-5,"eg":-5,"rs":-5,"va":-5,"ma":-5,"se":-5,"al":-5,"me":-5,"si":-5,"ro":-5,"mt":-5,"xk":-5,"de":-5,"sj":-5,"at":-5,"us":-5,"sy":-5,"fi":-5,"sm":-5,"nl":-5,"tr":-5,"world":-5,"ly":-5,"cz":-5,"uk":-5,"ax":-5,"ad":-5,"gi":-5,"li":-5,"pl":-5,"es":-5,"md":-5,"lt":-5,"je":-5,"is":-5,"pt":-5},"epi_value":-5,"aggregated_origins":[{"origin":"en:unknown","percent":100}],"transportation_scores":{"hr":0.0,"il":0.0,"ie":0.0,"sk":0.0,"mk":0.0,"ps":0.0,"it":0.0,"lv":0.0,"bg":0.0,"dk":0.0,"ee":0.0,"mc":0.0,"dz":0.0,"ch":0.0,"fr":0.0,"im":0.0,"lu":0.0,"cy":0.0,"hu":0.0,"fo":0.0,"ua":0.0,"lb":0.0,"no":0.0,"tn":0.0,"gg":0.0,"gr":0.0,"cz":0.0,"uk":0.0,"ax":0.0,"world":0.0,"ly":0.0,"lt":0.0,"je":0.0,"is":0.0,"pt":0.0,"ad":0.0,"gi":0.0,"li":0.0,"es":0.0,"pl":0.0,"md":0.0,"ro":0.0,"mt":0.0,"xk":0.0,"de":0.0,"sj":0.0,"at":0.0,"be":0.0,"ba":0.0,"eg":0.0,"va":0.0,"rs":0.0,"se":0.0,"ma":0.0,"al":0.0,"me":0.0,"si":0.0,"nl":0.0,"sm":0.0,"tr":0.0,"us":0.0,"sy":0.0,"fi":0.0},"origins_from_origins_field":["en:unknown"],"origins_from_categories":["en:unknown"],"transportation_values":{"cy":0,"fo":0,"hu":0,"lb":0,"ua":0,"no":0,"tn":0,"gg":0,"gr":0,"il":0,"hr":0,"ie":0,"sk":0,"mk":0,"ps":0,"lv":0,"it":0,"ee":0,"dk":0,"bg":0,"mc":0,"dz":0,"fr":0,"ch":0,"im":0,"lu":0,"xk":0,"ro":0,"mt":0,"sj":0,"at":0,"de":0,"eg":0,"va":0,"rs":0,"be":0,"ba":0,"se":0,"ma":0,"me":0,"al":0,"si":0,"tr":0,"sm":0,"nl":0,"us":0,"sy":0,"fi":0,"uk":0,"cz":0,"ax":0,"world":0,"ly":0,"lt":0,"je":0,"is":0,"pt":0,"gi":0,"ad":0,"es":0,"md":0,"pl":0,"li":0},"epi_score":0,"warning":"origins_are_100_percent_unknown"},"threatened_species":{}},"missing_data_warning":1,"agribalyse":{"co2_transportation":0.25227586,"ef_agriculture":0.005112031,"co2_total":2.014729565,"score":84,"ef_packaging":0.052461293,"ef_consumption":0,"agribalyse_food_code":"31034","co2_processing":1.156632,"co2_consumption":0,"name_fr":"Sirop d'érable","co2_packaging":0.49792849,"dqr":"1.340153996158337","ef_distribution":0.0035269416,"name_en":"Syrup, maple","version":"3.1.1","ef_total":0.2460164216,"ef_transportation":0.026289176,"code":"31034","is_beverage":0,"co2_distribution":0.013496414,"ef_processing":0.15862698,"co2_agriculture":0.094396801},"scores":{"sy":64,"fi":64,"us":64,"tr":64,"nl":64,"sm":64,"se":64,"al":64,"ma":64,"me":64,"si":64,"eg":64,"rs":64,"va":64,"be":64,"ba":64,"sj":64,"at":64,"de":64,"xk":64,"ro":64,"mt":64,"md":64,"pl":64,"es":64,"li":64,"gi":64,"ad":64,"is":64,"pt":64,"lt":64,"je":64,"ly":64,"world":64,"ax":64,"uk":64,"cz":64,"gg":64,"gr":64,"tn":64,"no":64,"lb":64,"ua":64,"fo":64,"hu":64,"cy":64,"lu":64,"ch":64,"fr":64,"im":64,"dz":64,"mc":64,"ee":64,"dk":64,"bg":64,"ps":64,"it":64,"lv":64,"ie":64,"sk":64,"mk":64,"il":64,"hr":64},"grades":{"tn":"b","gg":"b","gr":"b","cy":"b","fo":"b","hu":"b","lb":"b","ua":"b","no":"b","mc":"b","dz":"b","ch":"b","fr":"b","im":"b","lu":"b","il":"b","hr":"b","ie":"b","sk":"b","mk":"b","ps":"b","lv":"b","it":"b","ee":"b","dk":"b","bg":"b","tr":"b","nl":"b","sm":"b","us":"b","sy":"b","fi":"b","xk":"b","ro":"b","mt":"b","sj":"b","at":"b","de":"b","eg":"b","va":"b","rs":"b","be":"b","ba":"b","se":"b","al":"b","ma":"b","me":"b","si":"b","lt":"b","je":"b","is":"b","pt":"b","gi":"b","ad":"b","es":"b","md":"b","pl":"b","li":"b","uk":"b","cz":"b","ax":"b","world":"b","ly":"b"},"missing_key_data":1,"status":"known","previous_data":{"grade":null,"score":null,"agribalyse":{"warning":"missing_agribalyse_match"}},"missing":{"labels":1,"packagings":1,"origins":1}}`
  - `{"missing":{"labels":1,"categories":1,"origins":1,"packagings":1},"adjustments":{"packaging":{"value":-15,"warning":"packaging_data_missing","non_recyclable_and_non_biodegradable_materials":1},"production_system":{"value":0,"labels":[],"warning":"no_label"},"threatened_species":{},"origins_of_ingredients":{"transportation_values":{"dz":0,"ps":0,"lu":0,"eg":0,"ax":0,"at":0,"ee":0,"se":0,"ua":0,"ma":0,"dk":0,"es":0,"it":0,"ch":0,"si":0,"hr":0,"je":0,"al":0,"me":0,"li":0,"va":0,"us":0,"tn":0,"lv":0,"mc":0,"fr":0,"fo":0,"im":0,"gr":0,"md":0,"il":0,"ro":0,"ba":0,"sk":0,"is":0,"sj":0,"fi":0,"ly":0,"ie":0,"de":0,"sy":0,"lt":0,"no":0,"ad":0,"cz":0,"gi":0,"pt":0,"tr":0,"cy":0,"world":0,"sm":0,"gg":0,"bg":0,"uk":0,"nl":0,"lb":0,"be":0,"mt":0,"pl":0,"xk":0,"rs":0,"mk":0,"hu":0},"aggregated_origins":[{"origin":"en:unknown","percent":100}],"origins_from_origins_field":["en:unknown"],"origins_from_categories":["en:unknown"],"values":{"md":-5,"il":-5,"ro":-5,"gr":-5,"im":-5,"fo":-5,"fr":-5,"mc":-5,"lv":-5,"tn":-5,"us":-5,"va":-5,"me":-5,"li":-5,"al":-5,"je":-5,"hr":-5,"si":-5,"ch":-5,"es":-5,"it":-5,"dk":-5,"ma":-5,"ua":-5,"se":-5,"ee":-5,"at":-5,"ax":-5,"eg":-5,"ps":-5,"lu":-5,"dz":-5,"hu":-5,"rs":-5,"mk":-5,"pl":-5,"mt":-5,"xk":-5,"be":-5,"lb":-5,"nl":-5,"uk":-5,"bg":-5,"gg":-5,"sm":-5,"world":-5,"cy":-5,"tr":-5,"pt":-5,"gi":-5,"ad":-5,"no":-5,"cz":-5,"sy":-5,"de":-5,"lt":-5,"ie":-5,"ly":-5,"is":-5,"fi":-5,"sj":-5,"ba":-5,"sk":-5},"epi_value":-5,"epi_score":0,"warning":"origins_are_100_percent_unknown","transportation_scores":{"hr":0,"si":0,"je":0,"al":0,"va":0,"us":0,"li":0,"me":0,"lv":0,"tn":0,"fr":0,"mc":0,"im":0,"fo":0,"ro":0,"il":0,"md":0,"gr":0,"lu":0,"ps":0,"dz":0,"at":0,"ax":0,"eg":0,"se":0,"ee":0,"ua":0,"dk":0,"ma":0,"ch":0,"it":0,"es":0,"sm":0,"world":0,"gg":0,"bg":0,"uk":0,"be":0,"lb":0,"nl":0,"xk":0,"pl":0,"mt":0,"hu":0,"mk":0,"rs":0,"sk":0,"ba":0,"ly":0,"fi":0,"sj":0,"is":0,"lt":0,"sy":0,"de":0,"ie":0,"gi":0,"cz":0,"ad":0,"no":0,"pt":0,"cy":0,"tr":0}}},"missing_agribalyse_match_warning":1,"status":"unknown","agribalyse":{"warning":"missing_agribalyse_match"},"missing_key_data":1}`
  - `{"missing_agribalyse_match_warning":1,"status":"unknown","missing":{"packagings":1,"categories":1,"origins":1,"labels":1},"missing_key_data":1,"adjustments":{"threatened_species":{},"packaging":{"value":-15,"warning":"packaging_data_missing"},"origins_of_ingredients":{"warning":"origins_are_100_percent_unknown","values":{"nl":-5,"sj":-5,"lu":-5,"ua":-5,"mt":-5,"je":-5,"il":-5,"fo":-5,"ch":-5,"is":-5,"ax":-5,"us":-5,"mc":-5,"dz":-5,"hu":-5,"mk":-5,"me":-5,"cy":-5,"ee":-5,"be":-5,"fr":-5,"ps":-5,"world":-5,"ro":-5,"lv":-5,"at":-5,"bg":-5,"eg":-5,"pl":-5,"fi":-5,"xk":-5,"rs":-5,"lb":-5,"it":-5,"ad":-5,"li":-5,"gg":-5,"ma":-5,"lt":-5,"si":-5,"im":-5,"dk":-5,"ba":-5,"es":-5,"de":-5,"ly":-5,"sy":-5,"sm":-5,"tr":-5,"pt":-5,"al":-5,"md":-5,"gi":-5,"va":-5,"ie":-5,"cz":-5,"sk":-5,"gr":-5,"tn":-5,"uk":-5,"hr":-5,"no":-5,"se":-5},"transportation_scores":{"ba":0.0,"dk":0.0,"im":0.0,"sm":0.0,"sy":0.0,"de":0.0,"ly":0.0,"es":0.0,"ad":0.0,"lb":0.0,"it":0.0,"rs":0.0,"xk":0.0,"si":0.0,"ma":0.0,"lt":0.0,"li":0.0,"gg":0.0,"gr":0.0,"sk":0.0,"cz":0.0,"va":0.0,"gi":0.0,"ie":0.0,"se":0.0,"uk":0.0,"no":0.0,"tn":0.0,"hr":0.0,"al":0.0,"md":0.0,"tr":0.0,"pt":0.0,"ua":0.0,"lu":0.0,"us":0.0,"ch":0.0,"is":0.0,"ax":0.0,"il":0.0,"fo":0.0,"mt":0.0,"je":0.0,"nl":0.0,"sj":0.0,"ee":0.0,"be":0.0,"pl":0.0,"fi":0.0,"eg":0.0,"bg":0.0,"lv":0.0,"ro":0.0,"at":0.0,"ps":0.0,"fr":0.0,"world":0.0,"mk":0.0,"dz":0.0,"mc":0.0,"hu":0.0,"cy":0.0,"me":0.0},"epi_score":0,"epi_value":-5,"origins_from_categories":["en:unknown"],"transportation_values":{"ee":0,"be":0,"fi":0,"pl":0,"bg":0,"eg":0,"ro":0,"at":0,"lv":0,"world":0,"fr":0,"ps":0,"mk":0,"hu":0,"mc":0,"dz":0,"cy":0,"me":0,"ua":0,"lu":0,"us":0,"ax":0,"is":0,"ch":0,"fo":0,"il":0,"je":0,"mt":0,"nl":0,"sj":0,"gr":0,"sk":0,"cz":0,"ie":0,"va":0,"gi":0,"se":0,"uk":0,"tn":0,"no":0,"hr":0,"md":0,"al":0,"pt":0,"tr":0,"ba":0,"dk":0,"im":0,"sm":0,"sy":0,"ly":0,"de":0,"es":0,"ad":0,"it":0,"lb":0,"rs":0,"xk":0,"si":0,"lt":0,"ma":0,"gg":0,"li":0},"aggregated_origins":[{"percent":100.0,"origin":"en:unknown"}],"origins_from_origins_field":["en:unknown"]},"production_system":{"warning":"no_label","labels":[],"value":0}},"agribalyse":{"warning":"missing_agribalyse_match"}}`
  - `{"missing_agribalyse_match_warning":1,"status":"unknown","adjustments":{"packaging":{"value":-15,"non_recyclable_and_non_biodegradable_materials":1,"warning":"packaging_data_missing"},"production_system":{"value":0,"labels":[],"warning":"no_label"},"origins_of_ingredients":{"transportation_scores":{"ua":0,"se":0,"ee":0,"ch":0,"it":0,"es":0,"dk":0,"ma":0,"lu":0,"ps":0,"dz":0,"at":0,"ax":0,"eg":0,"fr":0,"mc":0,"lv":0,"tn":0,"ro":0,"il":0,"md":0,"gr":0,"im":0,"fo":0,"je":0,"hr":0,"si":0,"us":0,"va":0,"li":0,"me":0,"al":0,"cy":0,"tr":0,"pt":0,"ly":0,"sj":0,"fi":0,"is":0,"sk":0,"ba":0,"gi":0,"no":0,"cz":0,"ad":0,"lt":0,"de":0,"sy":0,"ie":0,"lb":0,"be":0,"nl":0,"uk":0,"hu":0,"rs":0,"mk":0,"xk":0,"pl":0,"mt":0,"gg":0,"world":0,"sm":0,"bg":0},"epi_score":0,"warning":"origins_are_100_percent_unknown","epi_value":-5,"origins_from_categories":["en:unknown"],"values":{"dz":-5,"ps":-5,"lu":-5,"eg":-5,"at":-5,"ax":-5,"ee":-5,"se":-5,"ua":-5,"ma":-5,"dk":-5,"es":-5,"it":-5,"ch":-5,"si":-5,"hr":-5,"je":-5,"al":-5,"me":-5,"li":-5,"va":-5,"us":-5,"tn":-5,"lv":-5,"mc":-5,"fr":-5,"fo":-5,"im":-5,"gr":-5,"md":-5,"il":-5,"ro":-5,"ba":-5,"sk":-5,"is":-5,"sj":-5,"fi":-5,"ly":-5,"ie":-5,"de":-5,"sy":-5,"lt":-5,"ad":-5,"cz":-5,"no":-5,"gi":-5,"pt":-5,"tr":-5,"cy":-5,"world":-5,"sm":-5,"gg":-5,"bg":-5,"uk":-5,"nl":-5,"lb":-5,"be":-5,"pl":-5,"mt":-5,"xk":-5,"mk":-5,"rs":-5,"hu":-5},"aggregated_origins":[{"origin":"en:unknown","percent":100}],"origins_from_origins_field":["en:unknown"],"transportation_values":{"gg":0,"world":0,"sm":0,"bg":0,"lb":0,"be":0,"nl":0,"uk":0,"hu":0,"rs":0,"mk":0,"xk":0,"pl":0,"mt":0,"ly":0,"fi":0,"sj":0,"is":0,"sk":0,"ba":0,"gi":0,"cz":0,"no":0,"ad":0,"lt":0,"de":0,"sy":0,"ie":0,"cy":0,"tr":0,"pt":0,"je":0,"hr":0,"si":0,"va":0,"us":0,"li":0,"me":0,"al":0,"fr":0,"mc":0,"lv":0,"tn":0,"ro":0,"md":0,"il":0,"gr":0,"im":0,"fo":0,"lu":0,"ps":0,"dz":0,"at":0,"ax":0,"eg":0,"ua":0,"se":0,"ee":0,"ch":0,"it":0,"es":0,"dk":0,"ma":0}},"threatened_species":{"warning":"ingredients_missing"}},"missing":{"ingredients":1,"labels":1,"packagings":1,"origins":1,"categories":1},"missing_key_data":1,"agribalyse":{"warning":"missing_agribalyse_match"}}`
  - `{"missing_key_data":1,"agribalyse":{"warning":"missing_agribalyse_match"},"missing_agribalyse_match_warning":1,"status":"unknown","adjustments":{"packaging":{"value":-15,"warning":"packaging_data_missing","non_recyclable_and_non_biodegradable_materials":1},"origins_of_ingredients":{"epi_value":-5,"warning":"origins_are_100_percent_unknown","epi_score":0,"transportation_scores":{"gi":0,"cz":0,"no":0,"ad":0,"lt":0,"sy":0,"de":0,"ie":0,"ly":0,"fi":0,"sj":0,"is":0,"ba":0,"sk":0,"cy":0,"tr":0,"pt":0,"bg":0,"gg":0,"world":0,"sm":0,"hu":0,"rs":0,"mk":0,"xk":0,"mt":0,"pl":0,"lb":0,"be":0,"nl":0,"uk":0,"at":0,"ax":0,"eg":0,"lu":0,"ps":0,"dz":0,"ch":0,"it":0,"es":0,"dk":0,"ma":0,"ua":0,"se":0,"ee":0,"va":0,"us":0,"li":0,"me":0,"al":0,"je":0,"hr":0,"si":0,"ro":0,"il":0,"md":0,"gr":0,"im":0,"fo":0,"fr":0,"mc":0,"lv":0,"tn":0},"transportation_values":{"tr":0,"cy":0,"pt":0,"ad":0,"cz":0,"no":0,"gi":0,"ie":0,"lt":0,"de":0,"sy":0,"fi":0,"sj":0,"is":0,"ly":0,"ba":0,"sk":0,"mk":0,"rs":0,"hu":0,"xk":0,"mt":0,"pl":0,"nl":0,"lb":0,"be":0,"uk":0,"bg":0,"gg":0,"world":0,"sm":0,"it":0,"es":0,"ch":0,"ma":0,"dk":0,"ua":0,"ee":0,"se":0,"eg":0,"ax":0,"at":0,"dz":0,"lu":0,"ps":0,"gr":0,"ro":0,"il":0,"md":0,"fo":0,"im":0,"mc":0,"fr":0,"tn":0,"lv":0,"li":0,"me":0,"us":0,"va":0,"al":0,"je":0,"si":0,"hr":0},"origins_from_origins_field":["en:unknown"],"aggregated_origins":[{"origin":"en:unknown","percent":100}],"origins_from_categories":["en:unknown"],"values":{"sk":-5,"ba":-5,"is":-5,"sj":-5,"fi":-5,"ly":-5,"ie":-5,"sy":-5,"de":-5,"lt":-5,"no":-5,"cz":-5,"ad":-5,"gi":-5,"pt":-5,"tr":-5,"cy":-5,"world":-5,"sm":-5,"gg":-5,"bg":-5,"uk":-5,"nl":-5,"lb":-5,"be":-5,"mt":-5,"pl":-5,"xk":-5,"rs":-5,"mk":-5,"hu":-5,"dz":-5,"ps":-5,"lu":-5,"eg":-5,"ax":-5,"at":-5,"ee":-5,"se":-5,"ua":-5,"ma":-5,"dk":-5,"es":-5,"it":-5,"ch":-5,"si":-5,"hr":-5,"je":-5,"al":-5,"me":-5,"li":-5,"us":-5,"va":-5,"tn":-5,"lv":-5,"mc":-5,"fr":-5,"fo":-5,"im":-5,"gr":-5,"md":-5,"il":-5,"ro":-5}},"threatened_species":{"warning":"ingredients_missing"},"production_system":{"value":0,"warning":"no_label","labels":[]}},"missing":{"labels":1,"categories":1,"origins":1,"packagings":1,"ingredients":1}}`
  - `{"missing_key_data":1,"agribalyse":{"warning":"missing_agribalyse_match"},"missing_agribalyse_match_warning":1,"status":"unknown","adjustments":{"packaging":{"value":-15,"non_recyclable_and_non_biodegradable_materials":1,"warning":"packaging_data_missing"},"production_system":{"value":0,"labels":[],"warning":"no_label"},"origins_of_ingredients":{"transportation_values":{"ch":0,"es":3,"it":2,"dk":0,"ma":0,"ua":4,"se":0,"ee":0,"at":0,"ax":0,"eg":4,"ps":5,"lu":0,"dz":0,"il":4,"md":2,"ro":3,"gr":5,"im":0,"fo":0,"fr":0,"mc":4,"lv":0,"tn":4,"us":0,"va":0,"me":3,"li":1,"al":4,"je":0,"hr":3,"si":3,"cy":5,"tr":0,"pt":2,"gi":3,"no":1,"cz":0,"ad":2,"de":1,"sy":3,"lt":0,"ie":2,"ly":4,"is":0,"sj":0,"fi":0,"sk":0,"ba":1,"hu":0,"rs":1,"mk":2,"pl":0,"mt":4,"xk":2,"be":1,"lb":5,"nl":1,"uk":0,"bg":1,"gg":0,"sm":1,"world":0},"origins_from_origins_field":["en:china"],"aggregated_origins":[{"percent":100,"origin":"en:china"}],"origins_from_categories":["en:unknown"],"values":{"gg":-5,"world":-5,"sm":-4,"bg":-4,"lb":0,"be":-4,"nl":-4,"uk":-5,"hu":-5,"rs":-4,"mk":-3,"xk":-3,"pl":-5,"mt":-1,"ly":-1,"sj":-5,"fi":-5,"is":-5,"ba":-4,"sk":-5,"gi":-2,"ad":-3,"cz":-5,"no":-4,"lt":-5,"sy":-2,"de":-4,"ie":-3,"cy":0,"tr":-5,"pt":-3,"je":-5,"hr":-2,"si":-2,"us":-5,"va":-5,"li":-4,"me":-2,"al":-1,"fr":-5,"mc":-1,"lv":-5,"tn":-1,"ro":-2,"md":-3,"il":-1,"gr":0,"im":-5,"fo":-5,"lu":-5,"ps":0,"dz":-5,"at":-5,"ax":-5,"eg":-1,"ua":-1,"se":-5,"ee":-5,"ch":-5,"it":-3,"es":-2,"dk":-5,"ma":-5},"epi_value":-5,"epi_score":0,"transportation_scores":{"bg":7,"gg":0,"world":0,"sm":4,"mk":14,"rs":4,"hu":0,"xk":13,"pl":0,"mt":28,"nl":6,"be":6,"lb":31,"uk":1,"ad":13,"cz":0,"no":6,"gi":21,"ie":11,"lt":0,"sy":18,"de":6,"sj":0,"fi":1,"is":0,"ly":28,"ba":5,"sk":0,"tr":0,"cy":31,"pt":11,"li":5,"me":23,"us":0,"va":0,"al":27,"je":0,"si":21,"hr":18,"gr":31,"ro":17,"md":16,"il":27,"fo":0,"im":0,"mc":25,"fr":0,"tn":27,"lv":2,"eg":27,"ax":0,"at":2,"dz":3,"lu":0,"ps":35,"it":10,"es":19,"ch":3,"ma":0,"dk":0,"ua":27,"ee":2,"se":0}},"threatened_species":{"warning":"ingredients_missing"}},"missing":{"packagings":1,"categories":1,"labels":1,"ingredients":1}}`
  - `{"missing_key_data":1,"agribalyse":{"warning":"missing_agribalyse_match"},"status":"unknown","missing_agribalyse_match_warning":1,"adjustments":{"packaging":{"warning":"packaging_data_missing","non_recyclable_and_non_biodegradable_materials":1,"value":-15},"production_system":{"value":0,"labels":[],"warning":"no_label"},"threatened_species":{},"origins_of_ingredients":{"origins_from_categories":["en:unknown"],"values":{"uk":-5,"nl":-5,"lb":-5,"be":-5,"xk":-5,"pl":-5,"mt":-5,"rs":-5,"mk":-5,"hu":-5,"world":-5,"sm":-5,"gg":-5,"bg":-5,"pt":-5,"tr":-5,"cy":-5,"ba":-5,"sk":-5,"fi":-5,"sj":-5,"is":-5,"ly":-5,"ie":-5,"lt":-5,"sy":-5,"de":-5,"no":-5,"ad":-5,"cz":-5,"gi":-5,"tn":-5,"lv":-5,"mc":-5,"fr":-5,"fo":-5,"im":-5,"gr":-5,"ro":-5,"il":-5,"md":-5,"si":-5,"hr":-5,"je":-5,"al":-5,"li":-5,"me":-5,"va":-5,"us":-5,"ee":-5,"se":-5,"ua":-5,"ma":-5,"dk":-5,"it":-5,"es":-5,"ch":-5,"dz":-5,"lu":-5,"ps":-5,"eg":-5,"ax":-5,"at":-5},"origins_from_origins_field":["en:unknown"],"aggregated_origins":[{"percent":100,"origin":"en:unknown"}],"transportation_values":{"ax":0,"at":0,"eg":0,"ps":0,"lu":0,"dz":0,"ch":0,"es":0,"it":0,"dk":0,"ma":0,"ua":0,"se":0,"ee":0,"us":0,"va":0,"me":0,"li":0,"al":0,"je":0,"hr":0,"si":0,"il":0,"md":0,"ro":0,"gr":0,"im":0,"fo":0,"fr":0,"mc":0,"lv":0,"tn":0,"gi":0,"no":0,"ad":0,"cz":0,"de":0,"sy":0,"lt":0,"ie":0,"ly":0,"is":0,"sj":0,"fi":0,"ba":0,"sk":0,"cy":0,"tr":0,"pt":0,"bg":0,"gg":0,"sm":0,"world":0,"hu":0,"mk":0,"rs":0,"mt":0,"pl":0,"xk":0,"lb":0,"be":0,"nl":0,"uk":0},"transportation_scores":{"ro":0,"il":0,"md":0,"gr":0,"im":0,"fo":0,"fr":0,"mc":0,"lv":0,"tn":0,"va":0,"us":0,"li":0,"me":0,"al":0,"je":0,"hr":0,"si":0,"ch":0,"it":0,"es":0,"dk":0,"ma":0,"ua":0,"se":0,"ee":0,"ax":0,"at":0,"eg":0,"lu":0,"ps":0,"dz":0,"hu":0,"mk":0,"rs":0,"xk":0,"pl":0,"mt":0,"be":0,"lb":0,"nl":0,"uk":0,"bg":0,"gg":0,"sm":0,"world":0,"cy":0,"tr":0,"pt":0,"gi":0,"ad":0,"cz":0,"no":0,"lt":0,"de":0,"sy":0,"ie":0,"ly":0,"sj":0,"fi":0,"is":0,"sk":0,"ba":0},"warning":"origins_are_100_percent_unknown","epi_score":0,"epi_value":-5}},"missing":{"labels":1,"categories":1,"origins":1,"packagings":1}}`
  - `{"missing_data_warning":1,"agribalyse":{"co2_total":1.964416728,"ef_agriculture":0.16173855,"is_beverage":0,"co2_distribution":0.004786188,"co2_packaging":0.28789852,"co2_agriculture":1.3612096,"co2_transportation":0.12631417,"ef_consumption":0,"name_fr":"Muffin anglais, petit pain spécial, préemballé","version":"3.1.1","ef_total":0.22809874327000002,"agribalyse_food_code":"7257","code":"7257","ef_transportation":0.010300797,"score":86,"ef_packaging":0.018899332,"co2_consumption":0,"ef_processing":0.036425166,"dqr":"2.52","ef_distribution":0.00073489827,"co2_processing":0.18420825,"name_en":"English muffin, prepacked"},"previous_data":{"grade":"b","score":66,"agribalyse":{"ef_agriculture":0.19268689,"is_beverage":0,"co2_total":2.4903887,"co2_transportation":0.13265497,"co2_packaging":0.30185295,"co2_agriculture":1.8509804,"co2_distribution":0.0064852108,"score":82,"co2_consumption":0,"ef_packaging":0.018699113,"code":"7257","ef_transportation":0.010539211,"agribalyse_food_code":"7257","ef_total":0.2631888,"name_fr":"Muffin anglais, petit pain spécial, préemballé","ef_consumption":0,"name_en":"English muffin, prepacked","dqr":"2.52","ef_processing":0.039823527,"ef_distribution":0.0014414118,"co2_processing":0.19842529}},"adjustments":{"origins_of_ingredients":{"origins_from_origins_field":["en:unknown"],"epi_value":-5,"warning":"origins_are_100_percent_unknown","aggregated_origins":[{"origin":"en:unknown","percent":100}],"origins_from_categories":["en:unknown"],"epi_score":0,"transportation_scores":{"rs":0.0,"hr":0.0,"ax":0.0,"li":0.0,"al":0.0,"tn":0.0,"dz":0.0,"se":0.0,"es":0.0,"fi":0.0,"lv":0.0,"pt":0.0,"mk":0.0,"im":0.0,"sj":0.0,"va":0.0,"md":0.0,"gg":0.0,"fr":0.0,"pl":0.0,"tr":0.0,"dk":0.0,"mc":0.0,"at":0.0,"is":0.0,"ch":0.0,"ua":0.0,"ly":0.0,"cy":0.0,"lb":0.0,"me":0.0,"je":0.0,"mt":0.0,"cz":0.0,"bg":0.0,"ie":0.0,"it":0.0,"eg":0.0,"lu":0.0,"ro":0.0,"gr":0.0,"sm":0.0,"ma":0.0,"lt":0.0,"si":0.0,"sk":0.0,"us":0.0,"hu":0.0,"sy":0.0,"de":0.0,"ps":0.0,"ad":0.0,"nl":0.0,"ba":0.0,"ee":0.0,"no":0.0,"il":0.0,"be":0.0,"world":0.0,"uk":0.0,"xk":0.0,"gi":0.0,"fo":0.0},"values":{"ma":-5,"lt":-5,"ro":-5,"gr":-5,"sm":-5,"si":-5,"sk":-5,"us":-5,"me":-5,"je":-5,"mt":-5,"cz":-5,"cy":-5,"lb":-5,"ie":-5,"it":-5,"eg":-5,"lu":-5,"bg":-5,"be":-5,"world":-5,"uk":-5,"xk":-5,"gi":-5,"fo":-5,"ee":-5,"no":-5,"il":-5,"de":-5,"ps":-5,"hu":-5,"sy":-5,"ba":-5,"ad":-5,"nl":-5,"im":-5,"sj":-5,"pt":-5,"mk":-5,"md":-5,"gg":-5,"va":-5,"al":-5,"tn":-5,"rs":-5,"ax":-5,"hr":-5,"li":-5,"es":-5,"fi":-5,"lv":-5,"dz":-5,"se":-5,"dk":-5,"mc":-5,"at":-5,"ly":-5,"is":-5,"ch":-5,"ua":-5,"pl":-5,"fr":-5,"tr":-5},"transportation_values":{"it":0,"ie":0,"lu":0,"eg":0,"bg":0,"je":0,"mt":0,"me":0,"cz":0,"cy":0,"lb":0,"si":0,"us":0,"sk":0,"lt":0,"ma":0,"ro":0,"sm":0,"gr":0,"ba":0,"nl":0,"ad":0,"ps":0,"de":0,"hu":0,"sy":0,"world":0,"be":0,"fo":0,"xk":0,"uk":0,"gi":0,"no":0,"ee":0,"il":0,"fi":0,"es":0,"lv":0,"se":0,"dz":0,"tn":0,"al":0,"ax":0,"rs":0,"hr":0,"li":0,"md":0,"gg":0,"va":0,"im":0,"sj":0,"mk":0,"pt":0,"tr":0,"pl":0,"fr":0,"ly":0,"is":0,"ua":0,"ch":0,"dk":0,"mc":0,"at":0}},"packaging":{"value":-1,"score":92.0,"non_recyclable_and_non_biodegradable_materials":0,"packagings":[{"ecoscore_shape_ratio":1,"ecoscore_material_score":92,"shape":"en:packaging","material":"en:paper"}]},"threatened_species":{"ingredient":"en:palm-oil","value":-10},"production_system":{"labels":[],"value":0,"warning":"no_label"}},"missing":{"labels":1,"origins":1},"scores":{"ro":70,"gr":70,"sm":70,"ma":70,"lt":70,"si":70,"sk":70,"us":70,"cy":70,"lb":70,"me":70,"mt":70,"je":70,"cz":70,"bg":70,"ie":70,"it":70,"eg":70,"lu":70,"ee":70,"no":70,"il":70,"be":70,"world":70,"xk":70,"uk":70,"gi":70,"fo":70,"hu":70,"sy":70,"de":70,"ps":70,"nl":70,"ad":70,"ba":70,"pt":70,"mk":70,"im":70,"sj":70,"va":70,"md":70,"gg":70,"rs":70,"hr":70,"ax":70,"li":70,"al":70,"tn":70,"dz":70,"se":70,"es":70,"fi":70,"lv":70,"dk":70,"at":70,"mc":70,"is":70,"ch":70,"ua":70,"ly":70,"fr":70,"pl":70,"tr":70},"grade":"b","score":70,"grades":{"pl":"b","fr":"b","tr":"b","mc":"b","at":"b","dk":"b","ly":"b","ch":"b","ua":"b","is":"b","al":"b","tn":"b","li":"b","hr":"b","rs":"b","ax":"b","lv":"b","es":"b","fi":"b","dz":"b","se":"b","sj":"b","im":"b","pt":"b","mk":"b","gg":"b","md":"b","va":"b","de":"b","ps":"b","sy":"b","hu":"b","ba":"b","nl":"b","ad":"b","xk":"b","gi":"b","uk":"b","fo":"b","be":"b","world":"b","il":"b","ee":"b","no":"b","cz":"b","me":"b","mt":"b","je":"b","lb":"b","cy":"b","lu":"b","eg":"b","ie":"b","it":"b","bg":"b","ma":"b","lt":"b","gr":"b","sm":"b","ro":"b","sk":"b","us":"b","si":"b"},"status":"known"}`
  - `{"missing":{"ingredients":1,"labels":1,"origins":1,"categories":1,"packagings":1},"status":"unknown","missing_agribalyse_match_warning":1,"adjustments":{"threatened_species":{"warning":"ingredients_missing"},"origins_of_ingredients":{"epi_value":-5,"transportation_scores":{"al":0,"us":0,"va":0,"li":0,"me":0,"hr":0,"si":0,"je":0,"im":0,"fo":0,"ro":0,"il":0,"md":0,"gr":0,"lv":0,"tn":0,"fr":0,"mc":0,"ax":0,"at":0,"eg":0,"lu":0,"ps":0,"dz":0,"dk":0,"ma":0,"ch":0,"it":0,"es":0,"se":0,"ee":0,"ua":0,"bg":0,"world":0,"sm":0,"gg":0,"xk":0,"pl":0,"mt":0,"hu":0,"mk":0,"rs":0,"uk":0,"be":0,"lb":0,"nl":0,"lt":0,"sy":0,"de":0,"ie":0,"gi":0,"no":0,"cz":0,"ad":0,"ba":0,"sk":0,"ly":0,"sj":0,"fi":0,"is":0,"pt":0,"cy":0,"tr":0},"warning":"origins_are_100_percent_unknown","epi_score":0,"transportation_values":{"us":0,"va":0,"me":0,"li":0,"al":0,"je":0,"hr":0,"si":0,"il":0,"md":0,"ro":0,"gr":0,"im":0,"fo":0,"fr":0,"mc":0,"lv":0,"tn":0,"ax":0,"at":0,"eg":0,"ps":0,"lu":0,"dz":0,"ch":0,"es":0,"it":0,"dk":0,"ma":0,"ua":0,"se":0,"ee":0,"bg":0,"gg":0,"sm":0,"world":0,"hu":0,"mk":0,"rs":0,"mt":0,"pl":0,"xk":0,"lb":0,"be":0,"nl":0,"uk":0,"gi":0,"no":0,"cz":0,"ad":0,"sy":0,"de":0,"lt":0,"ie":0,"ly":0,"is":0,"sj":0,"fi":0,"sk":0,"ba":0,"cy":0,"tr":0,"pt":0},"values":{"tr":-5,"cy":-5,"pt":-5,"is":-5,"sj":-5,"fi":-5,"ly":-5,"sk":-5,"ba":-5,"no":-5,"cz":-5,"ad":-5,"gi":-5,"ie":-5,"de":-5,"sy":-5,"lt":-5,"nl":-5,"lb":-5,"be":-5,"uk":-5,"mk":-5,"rs":-5,"hu":-5,"mt":-5,"pl":-5,"xk":-5,"gg":-5,"sm":-5,"world":-5,"bg":-5,"ua":-5,"ee":-5,"se":-5,"es":-5,"it":-5,"ch":-5,"ma":-5,"dk":-5,"dz":-5,"ps":-5,"lu":-5,"eg":-5,"ax":-5,"at":-5,"mc":-5,"fr":-5,"tn":-5,"lv":-5,"gr":-5,"md":-5,"il":-5,"ro":-5,"fo":-5,"im":-5,"je":-5,"si":-5,"hr":-5,"me":-5,"li":-5,"us":-5,"va":-5,"al":-5},"origins_from_categories":["en:unknown"],"origins_from_origins_field":["en:unknown"],"aggregated_origins":[{"percent":100,"origin":"en:unknown"}]},"production_system":{"value":0,"warning":"no_label","labels":[]},"packaging":{"non_recyclable_and_non_biodegradable_materials":1,"warning":"packaging_data_missing","value":-15}},"agribalyse":{"warning":"missing_agribalyse_match"},"missing_key_data":1}`
  - `{"missing":{"origins":1,"categories":1,"packagings":1,"labels":1,"ingredients":1},"adjustments":{"packaging":{"warning":"packaging_data_missing","non_recyclable_and_non_biodegradable_materials":1,"value":-15},"origins_of_ingredients":{"transportation_scores":{"ad":0,"cz":0,"no":0,"gi":0,"ie":0,"de":0,"sy":0,"lt":0,"is":0,"fi":0,"sj":0,"ly":0,"sk":0,"ba":0,"tr":0,"cy":0,"pt":0,"bg":0,"gg":0,"sm":0,"world":0,"mk":0,"rs":0,"hu":0,"mt":0,"pl":0,"xk":0,"nl":0,"be":0,"lb":0,"uk":0,"eg":0,"at":0,"ax":0,"dz":0,"ps":0,"lu":0,"es":0,"it":0,"ch":0,"ma":0,"dk":0,"ua":0,"ee":0,"se":0,"me":0,"li":0,"us":0,"va":0,"al":0,"je":0,"si":0,"hr":0,"gr":0,"md":0,"il":0,"ro":0,"fo":0,"im":0,"mc":0,"fr":0,"tn":0,"lv":0},"warning":"origins_are_100_percent_unknown","epi_score":0,"epi_value":-5,"origins_from_categories":["en:unknown"],"values":{"cy":-5,"tr":-5,"pt":-5,"ly":-5,"is":-5,"fi":-5,"sj":-5,"ba":-5,"sk":-5,"gi":-5,"ad":-5,"cz":-5,"no":-5,"sy":-5,"de":-5,"lt":-5,"ie":-5,"lb":-5,"be":-5,"nl":-5,"uk":-5,"hu":-5,"mk":-5,"rs":-5,"mt":-5,"pl":-5,"xk":-5,"gg":-5,"world":-5,"sm":-5,"bg":-5,"ua":-5,"se":-5,"ee":-5,"ch":-5,"es":-5,"it":-5,"dk":-5,"ma":-5,"ps":-5,"lu":-5,"dz":-5,"ax":-5,"at":-5,"eg":-5,"fr":-5,"mc":-5,"lv":-5,"tn":-5,"md":-5,"il":-5,"ro":-5,"gr":-5,"im":-5,"fo":-5,"je":-5,"hr":-5,"si":-5,"va":-5,"us":-5,"me":-5,"li":-5,"al":-5},"aggregated_origins":[{"origin":"en:unknown","percent":100}],"origins_from_origins_field":["en:unknown"],"transportation_values":{"gg":0,"world":0,"sm":0,"bg":0,"lb":0,"be":0,"nl":0,"uk":0,"hu":0,"mk":0,"rs":0,"xk":0,"mt":0,"pl":0,"ly":0,"fi":0,"sj":0,"is":0,"sk":0,"ba":0,"gi":0,"no":0,"cz":0,"ad":0,"lt":0,"sy":0,"de":0,"ie":0,"cy":0,"tr":0,"pt":0,"je":0,"hr":0,"si":0,"us":0,"va":0,"li":0,"me":0,"al":0,"fr":0,"mc":0,"lv":0,"tn":0,"ro":0,"il":0,"md":0,"gr":0,"im":0,"fo":0,"lu":0,"ps":0,"dz":0,"ax":0,"at":0,"eg":0,"ua":0,"se":0,"ee":0,"ch":0,"it":0,"es":0,"dk":0,"ma":0}},"threatened_species":{"warning":"ingredients_missing"},"production_system":{"value":0,"labels":[],"warning":"no_label"}},"status":"unknown","missing_agribalyse_match_warning":1,"agribalyse":{"warning":"missing_agribalyse_match"},"missing_key_data":1}`

## ecoscore_grade
- **Type**: `STRING`
- **Valeurs uniques**: 9
- **Valeurs nulles**: 3,062 (3.23%)
- **Exemples de valeurs**:
  - `b`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `b`
  - `unknown`
  - `unknown`

## ecoscore_score
- **Type**: `NUMBER`
- **Valeurs uniques**: 130
- **Valeurs nulles**: 83,095 (87.65%)
- **Exemples de valeurs**:
  - `64`
  - `70`
  - `29`
  - `39`
  - `78`
  - `67`
  - `29`
  - `35`
  - `25`
  - `25`

## ecoscore_tags
- **Type**: `list`
- **Valeurs uniques**: 9
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `['b']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['b']`
  - `['unknown']`
  - `['unknown']`

## editors
- **Type**: `list`
- **Valeurs uniques**: 174
- **Valeurs nulles**: 94,262 (99.43%)
- **Exemples de valeurs**:
  - `['date-limite-app']`
  - `['']`
  - `['manu1400', 'upcbot', 'minouche']`
  - `['', 'upcbot']`
  - `['']`
  - `['', 'upcbot']`
  - `['']`
  - `['raphael0202']`
  - `['']`
  - `['', 'upcbot']`

## emb_codes_tags
- **Type**: `list`
- **Valeurs uniques**: 299
- **Valeurs nulles**: 84,655 (89.30%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## emb_codes
- **Type**: `STRING`
- **Valeurs uniques**: 307
- **Valeurs nulles**: 84,655 (89.30%)
- **Exemples de valeurs**:
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``

## entry_dates_tags
- **Type**: `list`
- **Valeurs uniques**: 3,214
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['2016-04-09', '2016-04', '2016']`
  - `['2018-03-21', '2018-03', '2018']`
  - `['2017-05-13', '2017-05', '2017']`
  - `['2015-11-26', '2015-11', '2015']`
  - `['2018-03-18', '2018-03', '2018']`
  - `['2018-02-26', '2018-02', '2018']`
  - `['2017-03-09', '2017-03', '2017']`
  - `['2016-12-02', '2016-12', '2016']`
  - `['2017-03-30', '2017-03', '2017']`
  - `['2018-05-07', '2018-05', '2018']`

## food_groups_tags
- **Type**: `list`
- **Valeurs uniques**: 44
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:fish-meat-eggs', 'en:eggs']`
  - `[]`
  - `[]`

## generic_name
- **Type**: `list`
- **Valeurs uniques**: 1,199
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[{'lang': 'main', 'text': 'Sandwich déjeuner - Oeuf, saucisse, fromage'}, {'lang': 'fr', 'text': 'Sandwich déjeuner - Oeuf, saucisse, fromage'}]`
  - `[]`
  - `[]`

## images
- **Type**: `list`
- **Valeurs uniques**: 86,988
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[{'key': 'front_en', 'imgid': 1, 'sizes': {'100': {'h': 100, 'w': 83}, '200': {'h': 200, 'w': 167}, '400': {'h': 400, 'w': 333}, 'full': {'h': 600, 'w': 500}}, 'uploaded_t': None, 'uploader': None}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 83}, '200': None, '400': {'h': 400, 'w': 333}, 'full': {'h': 600, 'w': 500}}, 'uploaded_t': 1660213050, 'uploader': 'foodvisor'}]`
  - `[{'key': 'ingredients_en', 'imgid': 3, 'sizes': {'100': {'h': 100, 'w': 73}, '200': {'h': 200, 'w': 146}, '400': {'h': 400, 'w': 292}, 'full': {'h': 1868, 'w': 1364}}, 'uploaded_t': None, 'uploader': None}, {'key': '3', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 73}, '200': None, '400': {'h': 400, 'w': 292}, 'full': {'h': 1868, 'w': 1364}}, 'uploaded_t': 1593726979, 'uploader': 'openfoodfacts-contributors'}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 3264, 'w': 2448}}, 'uploaded_t': 1521609622, 'uploader': 'openfoodfacts-contributors'}, {'key': 'front_en', 'imgid': 1, 'sizes': {'100': {'h': 100, 'w': 75}, '200': {'h': 200, 'w': 150}, '400': {'h': 400, 'w': 300}, 'full': {'h': 3264, 'w': 2448}}, 'uploaded_t': None, 'uploader': None}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 3264, 'w': 2448}}, 'uploaded_t': 1521609740, 'uploader': 'openfoodfacts-contributors'}]`
  - `[{'key': 'front_en', 'imgid': 1, 'sizes': {'100': {'h': 100, 'w': 56}, '200': {'h': 200, 'w': 113}, '400': {'h': 400, 'w': 225}, 'full': {'h': 2000, 'w': 1125}}, 'uploaded_t': None, 'uploader': None}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 56}, '200': None, '400': {'h': 400, 'w': 225}, 'full': {'h': 2000, 'w': 1125}}, 'uploaded_t': 1494699730, 'uploader': 'trevorpetersen'}]`
  - `[{'key': '3', 'imgid': None, 'sizes': {'100': {'h': 47, 'w': 100}, '200': None, '400': {'h': 188, 'w': 400}, 'full': {'h': 965, 'w': 2050}}, 'uploaded_t': 1610433267, 'uploader': 'kiliweb'}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 1333, 'w': 1000}}, 'uploaded_t': 1448509671, 'uploader': 'date-limite-app'}, {'key': 'front_fr', 'imgid': 2, 'sizes': {'100': {'h': 100, 'w': 100}, '200': {'h': 200, 'w': 200}, '400': {'h': 400, 'w': 400}, 'full': {'h': 1176, 'w': 1176}}, 'uploaded_t': None, 'uploader': None}, {'key': 'front', 'imgid': 1, 'sizes': {'100': {'h': 100, 'w': 75}, '200': {'h': 200, 'w': 150}, '400': {'h': 400, 'w': 300}, 'full': {'h': 1333, 'w': 1000}}, 'uploaded_t': None, 'uploader': None}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 100}, '200': None, '400': {'h': 400, 'w': 400}, 'full': {'h': 1176, 'w': 1176}}, 'uploaded_t': 1610433243, 'uploader': 'kiliweb'}, {'key': 'nutrition_fr', 'imgid': 3, 'sizes': {'100': {'h': 47, 'w': 100}, '200': {'h': 94, 'w': 200}, '400': {'h': 188, 'w': 400}, 'full': {'h': 965, 'w': 2050}}, 'uploaded_t': None, 'uploader': None}]`
  - `[{'key': 'front_en', 'imgid': 2, 'sizes': {'100': {'h': 100, 'w': 80}, '200': {'h': 200, 'w': 160}, '400': {'h': 400, 'w': 319}, 'full': {'h': 1200, 'w': 957}}, 'uploaded_t': None, 'uploader': None}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 80}, '200': None, '400': {'h': 400, 'w': 319}, 'full': {'h': 1200, 'w': 957}}, 'uploaded_t': 1631796149, 'uploader': 'kiliweb'}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 4032, 'w': 3024}}, 'uploaded_t': 1521387208, 'uploader': 'qingcanli'}, {'key': 'nutrition_en', 'imgid': 3, 'sizes': {'100': {'h': 100, 'w': 68}, '200': {'h': 200, 'w': 136}, '400': {'h': 400, 'w': 272}, 'full': {'h': 1200, 'w': 815}}, 'uploaded_t': None, 'uploader': None}, {'key': '3', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 68}, '200': None, '400': {'h': 400, 'w': 272}, 'full': {'h': 1200, 'w': 815}}, 'uploaded_t': 1631796150, 'uploader': 'kiliweb'}]`
  - `[{'key': 'front_fr', 'imgid': 5, 'sizes': {'100': {'h': 100, 'w': 59}, '200': {'h': 200, 'w': 118}, '400': {'h': 400, 'w': 235}, 'full': {'h': 1200, 'w': 705}}, 'uploaded_t': None, 'uploader': None}, {'key': '4', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 2666, 'w': 2000}}, 'uploaded_t': 1519614442, 'uploader': 'openfoodfacts-contributors'}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 2666, 'w': 2000}}, 'uploaded_t': 1519614418, 'uploader': 'openfoodfacts-contributors'}, {'key': '6', 'imgid': None, 'sizes': {'100': {'h': 58, 'w': 100}, '200': None, '400': {'h': 233, 'w': 400}, 'full': {'h': 1200, 'w': 2061}}, 'uploaded_t': 1519615071, 'uploader': 'kiliweb'}, {'key': 'ingredients_fr', 'imgid': 6, 'sizes': {'100': {'h': 58, 'w': 100}, '200': {'h': 116, 'w': 200}, '400': {'h': 233, 'w': 400}, 'full': {'h': 1200, 'w': 2061}}, 'uploaded_t': None, 'uploader': None}, {'key': '5', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 59}, '200': None, '400': {'h': 400, 'w': 235}, 'full': {'h': 1200, 'w': 705}}, 'uploaded_t': 1519615069, 'uploader': 'kiliweb'}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 2666, 'w': 2000}}, 'uploaded_t': 1519614334, 'uploader': 'openfoodfacts-contributors'}, {'key': '3', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 75}, '200': None, '400': {'h': 400, 'w': 300}, 'full': {'h': 2666, 'w': 2000}}, 'uploaded_t': 1519614430, 'uploader': 'openfoodfacts-contributors'}]`
  - `[{'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 62}, '200': None, '400': {'h': 400, 'w': 247}, 'full': {'h': 1200, 'w': 740}}, 'uploaded_t': 1574639168, 'uploader': 'kiliweb'}, {'key': 'nutrition_en', 'imgid': 2, 'sizes': {'100': {'h': 69, 'w': 100}, '200': {'h': 139, 'w': 200}, '400': {'h': 277, 'w': 400}, 'full': {'h': 660, 'w': 953}}, 'uploaded_t': None, 'uploader': None}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 69, 'w': 100}, '200': None, '400': {'h': 277, 'w': 400}, 'full': {'h': 660, 'w': 953}}, 'uploaded_t': 1574639169, 'uploader': 'kiliweb'}, {'key': 'front_en', 'imgid': 1, 'sizes': {'100': {'h': 100, 'w': 62}, '200': {'h': 200, 'w': 123}, '400': {'h': 400, 'w': 247}, 'full': {'h': 1200, 'w': 740}}, 'uploaded_t': None, 'uploader': None}]`
  - `[{'key': '3', 'imgid': None, 'sizes': {'100': {'h': 75, 'w': 100}, '200': None, '400': {'h': 300, 'w': 400}, 'full': {'h': 2048, 'w': 2732}}, 'uploaded_t': 1480706178, 'uploader': 'b7'}, {'key': 'front_fr', 'imgid': 2, 'sizes': {'100': {'h': 68, 'w': 100}, '200': {'h': 135, 'w': 200}, '400': {'h': 270, 'w': 400}, 'full': {'h': 734, 'w': 1086}}, 'uploaded_t': None, 'uploader': None}, {'key': 'ingredients_fr', 'imgid': 3, 'sizes': {'100': {'h': 70, 'w': 100}, '200': {'h': 140, 'w': 200}, '400': {'h': 280, 'w': 400}, 'full': {'h': 1079, 'w': 1544}}, 'uploaded_t': None, 'uploader': None}, {'key': '2', 'imgid': None, 'sizes': {'100': {'h': 75, 'w': 100}, '200': None, '400': {'h': 300, 'w': 400}, 'full': {'h': 2448, 'w': 3264}}, 'uploaded_t': 1480705644, 'uploader': 'b7'}, {'key': '1', 'imgid': None, 'sizes': {'100': {'h': 100, 'w': 95}, '200': None, '400': {'h': 400, 'w': 382}, 'full': {'h': 1598, 'w': 1526}}, 'uploaded_t': 1480704340, 'uploader': 'b7'}, {'key': 'nutrition_fr', 'imgid': 3, 'sizes': {'100': {'h': 41, 'w': 100}, '200': {'h': 83, 'w': 200}, '400': {'h': 165, 'w': 400}, 'full': {'h': 671, 'w': 1625}}, 'uploaded_t': None, 'uploader': None}]`
  - `[{'key': '1', 'imgid': None, 'sizes': {'100': {'h': 56, 'w': 100}, '200': None, '400': {'h': 225, 'w': 400}, 'full': {'h': 1125, 'w': 2000}}, 'uploaded_t': 1490826795, 'uploader': 'openfoodfacts-contributors'}, {'key': 'front_en', 'imgid': 1, 'sizes': {'100': {'h': 56, 'w': 100}, '200': {'h': 113, 'w': 200}, '400': {'h': 225, 'w': 400}, 'full': {'h': 1125, 'w': 2000}}, 'uploaded_t': None, 'uploader': None}]`
  - `[{'key': '1', 'imgid': None, 'sizes': {'100': {'h': 75, 'w': 100}, '200': None, '400': {'h': 299, 'w': 400}, 'full': {'h': 1493, 'w': 2000}}, 'uploaded_t': 1525644345, 'uploader': 'openfoodfacts-contributors'}]`

## informers_tags
- **Type**: `list`
- **Valeurs uniques**: 66,977
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['openfoodfacts-contributors', 'usda-ndb-import', 'teolemon', 'clockwerx', 'fix-missing-lang-bot', 'org-database-usda', 'foodvisor']`
  - `['openfoodfacts-contributors', 'inf']`
  - `['trevorpetersen', 'teolemon', 'openfoodfacts-contributors']`
  - `['date-limite-app', 'tacite-mass-editor', 'roboto-app', 'fix-missing-lang-bot', 'kiliweb', 'yuka.sY2b0xO6T85zoF3NwEKvlm5VCsbjqDTFLjzfqHelxdefBYCzRNFb4rPGPKg']`
  - `['qingcanli', 'yuka.sY2b0xO6T85zoF3NwEKvlmBfQoH3vyrcGi7jvUmVn_GgBJztQNBvxNLYHqs', 'kiliweb']`
  - `['openfoodfacts-contributors', 'yuka.YmJ0Y0NvQVQvdndTZzg4bitTemMyZnRyd0pqNWUyYUtPckVOSWc9PQ', 'kiliweb', 'jeanko']`
  - `['usda-ndb-import', 'yuka.YUswdE40OFJuOGNNZ3MxazBoYUZvK3BwLzhDbmNtMjlJckFLSWc9PQ', 'kiliweb']`
  - `['b7', 'gmathez']`
  - `['openfoodfacts-contributors']`
  - `['openfoodfacts-contributors', 'naruyoko']`

## ingredients_analysis_tags
- **Type**: `list`
- **Valeurs uniques**: 35
- **Valeurs nulles**: 76,003 (80.17%)
- **Exemples de valeurs**:
  - `['en:palm-oil-free', 'en:vegan', 'en:vegetarian']`
  - `['en:palm-oil-content-unknown', 'en:vegan-status-unknown', 'en:vegetarian-status-unknown']`
  - `['en:palm-oil-free', 'en:non-vegan', 'en:maybe-vegetarian']`
  - `['en:palm-oil-free', 'en:vegan-status-unknown', 'en:vegetarian-status-unknown']`
  - `['en:palm-oil', 'en:non-vegan', 'en:non-vegetarian']`
  - `['en:palm-oil-content-unknown', 'en:vegan', 'en:vegetarian']`
  - `['en:palm-oil-free', 'en:non-vegan', 'en:vegetarian-status-unknown']`
  - `['en:palm-oil-free', 'en:non-vegan', 'en:vegetarian-status-unknown']`
  - `['en:palm-oil-free', 'en:non-vegan', 'en:vegetarian-status-unknown']`
  - `['en:palm-oil-free', 'en:non-vegan', 'en:vegetarian-status-unknown']`

## ingredients_from_palm_oil_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 3
- **Valeurs nulles**: 80,953 (85.39%)
- **Exemples de valeurs**:
  - `0`
  - `0`
  - `0`
  - `1`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`

## ingredients_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 139
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `1`
  - `5`
  - `3`
  - `10`
  - `71`
  - `1`
  - `47`
  - `24`
  - `27`
  - `23`

## ingredients_original_tags
- **Type**: `list`
- **Valeurs uniques**: 14,669
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `['en:maple-syrup']`
  - `['en:water', 'en:sugar', 'en:propylene-glycol-caramel-color', 'en:ethyl-vanillin', 'en:artificial-flavouring']`
  - `['en:skimmed-milk', 'en:retinyl-palmitate', 'en:cholecalciferol']`
  - `['en:ginger', 'en:water', 'en:salt', 'en:e260', 'en:e330', 'en:e951', 'en:e202', 'en:and-fd-c-red-no', 'en:40', 'en:preservative']`
  - `['en:egg', 'fr:categorie-canada-a', 'en:cheddar', 'fr:ingredients-de-lait-modifie', 'en:microbial-culture', 'en:salt', 'en:rennet', 'en:microbial-coagulating-enzyme', 'en:e509', 'en:colour', 'en:e1104', 'en:e200', 'fr:ingredients-de-lait-modifie', 'en:water', 'en:sodium-citrate', 'en:e339', 'en:glucose', 'en:e260', 'en:salt', 'en:e200', 'en:soya-lecithin', 'en:e466', 'en:colour', 'fr:galette-de-saucisse', 'en:water', 'fr:substances-laitieres-modifies', 'en:salt', 'fr:extrait-sec-de-sirop-demais', 'en:dextrose', 'en:spice', 'fr:muffin-anglais', 'en:water', 'en:yeast', 'en:cornmeal', 'en:salt', 'en:vegetable-oil', 'en:glucose-fructose', 'en:sugar', 'en:e341', 'en:e282', 'en:e516', 'en:e510', 'en:wheat-gluten', 'fr:esters-tartriques-des-mono-et-diglycerides-acetyles', 'en:margarine', 'en:water', 'en:oil', 'fr:modifiees', 'en:salt', 'fr:monoglycerides-vegetales', 'en:soya-lecithin', 'en:e211', 'en:e330', 'en:natural-flavouring', 'en:colour', 'fr:palmitate-de-vitamine-a', 'en:cholecalciferol', 'fr:huile-pour-le-gril', 'en:soya-lecithin', 'en:natural-flavouring', 'fr:moyen-frais', 'en:cheese', 'en:milk', 'en:pork', 'en:fortified-wheat-flour', 'en:canola', 'en:soya', 'en:canola-oil', 'en:palm-oil', 'en:palm-kernel-oil', 'en:canola-oil']`
  - `['en:blue-agave-syrup']`
  - `['en:sugar', 'en:fortified-wheat-flour', 'en:water', 'en:liquid-whole-egg', 'en:soya-oil', 'fr:ou-de-canola', 'en:chocolate', 'en:sour-cream', 'en:cocoa-powder', 'en:modified-corn-starch', 'fr:shortening-d-huile-de-canola-et-de-palme-modifie-et-de-palmiste-modifie', 'en:chocolate-chunk', 'en:e500ii', 'en:e339', 'fr:phosphate-d-aluminium', 'fr:esters-monoacides-gras-de-propyleneglycol', 'en:skimmed-milk-powder', 'en:salt', 'fr:mono-et-diglycerides', 'en:e415', 'fr:gomme-de-crllulose', 'en:soya-lecithin', 'en:e202', 'en:e282', 'fr:acide-sobriquet', 'en:natural-flavouring', 'en:sugar', 'en:chocolate', 'en:cocoa-butter', 'en:dextrose', 'en:soya-lecithin', 'en:vanilla-extract', 'en:cream', 'en:milk', 'en:modified-milk-ingredients', 'en:modified-corn-starch', 'en:e412', 'en:e407', 'en:e410', 'en:sodium-citrate', 'en:e339', 'en:microbial-culture', 'en:sugar', 'en:chocolate', 'en:cocoa-butter', 'en:soya-lecithin', 'en:artificial-flavouring']`
  - `['en:pasta', 'en:whey', 'en:sour-cream', 'en:skimmed-milk', 'en:salt', 'en:butter', 'en:cheddar', 'en:corn-starch', 'en:e330', 'en:e160b', 'en:e270', 'en:sunflower-lecithin', 'en:e339', 'en:e551', 'en:ingredients', 'en:wheat-flour', 'en:cream', 'en:bacterial-cultures', 'en:pasteurised-milk', 'en:bacterial-cultures', 'en:salt', 'en:microbial-coagulating-enzyme', 'en:colour', 'en:for-anticaking']`
  - `['en:fortified-wheat-flour', 'en:cheddar', 'en:vegetable-oil', 'en:salt', 'en:sugar', 'en:yeast', 'en:coating', 'en:autolyzed-yeast-extract', 'en:e341i', 'en:e503ii', 'en:e500ii', 'en:e375', 'en:iron', 'en:thiamin-mononitrate', 'en:e101', 'en:folic-acid', 'en:milk', 'en:bacterial-culture', 'en:salt', 'en:enzyme', 'en:e160b', 'en:soya-bean', 'en:canola', 'en:sunflower', 'en:paprika', 'en:celery', 'en:onion']`
  - `['en:fortified-wheat-flour', 'en:sunflower-oil', 'en:cheddar', 'en:parmigiano-reggiano', 'en:salt', 'en:yeast', 'en:sugar', 'fr:levure-autolysee', 'en:onion', 'en:condiment', 'en:butter', 'en:e160b', 'en:e341', 'en:e500ii', 'en:e503ii', 'fr:lait-culture-bacterienne', 'en:salt', 'en:enzyme', 'en:e160b', 'fr:lait-bacterienne', 'en:salt', 'en:enzyme', 'en:barley']`

## ingredients_percent_analysis
- **Type**: `NUMBER`
- **Valeurs uniques**: 2
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`

## ingredients_tags
- **Type**: `list`
- **Valeurs uniques**: 14,645
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `['en:maple-syrup', 'en:added-sugar', 'en:disaccharide']`
  - `['en:water', 'en:sugar', 'en:added-sugar', 'en:disaccharide', 'en:propylene-glycol-caramel-color', 'en:ethyl-vanillin', 'en:artificial-flavouring', 'en:flavouring']`
  - `['en:skimmed-milk', 'en:dairy', 'en:milk', 'en:retinyl-palmitate', 'en:vitamins', 'en:vitamin-a', 'en:cholecalciferol', 'en:vitamin-d']`
  - `['en:ginger', 'en:condiment', 'en:spice', 'en:water', 'en:salt', 'en:e260', 'en:e330', 'en:e951', 'en:e202', 'en:and-fd-c-red-no', 'en:40', 'en:preservative']`
  - `['en:egg', 'fr:categorie-canada-a', 'en:cheddar', 'en:dairy', 'en:cheese', 'fr:ingredients-de-lait-modifie', 'en:microbial-culture', 'en:ferment', 'en:salt', 'en:rennet', 'en:enzyme', 'en:coagulating-enzyme', 'en:microbial-coagulating-enzyme', 'en:e509', 'en:colour', 'en:e1104', 'en:e200', 'en:water', 'en:sodium-citrate', 'en:minerals', 'en:sodium', 'en:e339', 'en:glucose', 'en:added-sugar', 'en:monosaccharide', 'en:e260', 'en:soya-lecithin', 'en:e322', 'en:e322i', 'en:e466', 'fr:galette-de-saucisse', 'fr:substances-laitieres-modifies', 'fr:extrait-sec-de-sirop-demais', 'en:dextrose', 'en:spice', 'en:condiment', 'fr:muffin-anglais', 'en:yeast', 'en:cornmeal', 'en:cereal', 'en:corn', 'en:vegetable-oil', 'en:oil-and-fat', 'en:vegetable-oil-and-fat', 'en:glucose-fructose', 'en:fructose', 'en:sugar', 'en:disaccharide', 'en:e341', 'en:e282', 'en:e516', 'en:e510', 'en:wheat-gluten', 'en:gluten', 'fr:esters-tartriques-des-mono-et-diglycerides-acetyles', 'en:margarine', 'en:oil', 'fr:modifiees', 'fr:monoglycerides-vegetales', 'en:e211', 'en:e330', 'en:natural-flavouring', 'en:flavouring', 'fr:palmitate-de-vitamine-a', 'en:cholecalciferol', 'en:vitamin-d', 'fr:huile-pour-le-gril', 'fr:moyen-frais', 'en:milk', 'en:pork', 'en:animal', 'en:fortified-wheat-flour', 'en:flour', 'en:wheat', 'en:cereal-flour', 'en:wheat-flour', 'en:canola', 'en:vegetable', 'en:root-vegetable', 'en:rapeseed', 'en:soya', 'en:canola-oil', 'en:rapeseed-oil', 'en:palm-oil', 'en:palm-oil-and-fat', 'en:palm-kernel-oil', 'en:palm-kernel-oil-and-fat']`
  - `['en:blue-agave-syrup']`
  - `['en:sugar', 'en:added-sugar', 'en:disaccharide', 'en:fortified-wheat-flour', 'en:cereal', 'en:flour', 'en:wheat', 'en:cereal-flour', 'en:wheat-flour', 'en:water', 'en:liquid-whole-egg', 'en:egg', 'en:whole-egg', 'en:soya-oil', 'en:oil-and-fat', 'en:vegetable-oil-and-fat', 'en:vegetable-oil', 'fr:ou-de-canola', 'en:chocolate', 'en:sour-cream', 'en:dairy', 'en:cream', 'en:cocoa-powder', 'en:plant', 'en:cocoa', 'en:modified-corn-starch', 'en:starch', 'en:corn-starch', 'en:modified-starch', 'fr:shortening-d-huile-de-canola-et-de-palme-modifie-et-de-palmiste-modifie', 'en:chocolate-chunk', 'en:e500ii', 'en:e500', 'en:e339', 'fr:phosphate-d-aluminium', 'fr:esters-monoacides-gras-de-propyleneglycol', 'en:skimmed-milk-powder', 'en:milk-powder', 'en:salt', 'fr:mono-et-diglycerides', 'en:e415', 'fr:gomme-de-crllulose', 'en:soya-lecithin', 'en:e322', 'en:e322i', 'en:e202', 'en:e282', 'fr:acide-sobriquet', 'en:natural-flavouring', 'en:flavouring', 'en:cocoa-butter', 'en:dextrose', 'en:monosaccharide', 'en:glucose', 'en:vanilla-extract', 'en:extract', 'en:vanilla', 'en:vegetable-extract', 'en:milk', 'en:modified-milk-ingredients', 'en:e412', 'en:e407', 'en:e410', 'en:sodium-citrate', 'en:minerals', 'en:sodium', 'en:microbial-culture', 'en:ferment', 'en:artificial-flavouring']`
  - `['en:pasta', 'en:dough', 'en:whey', 'en:dairy', 'en:sour-cream', 'en:cream', 'en:skimmed-milk', 'en:milk', 'en:salt', 'en:butter', 'en:cheddar', 'en:cheese', 'en:corn-starch', 'en:starch', 'en:e330', 'en:e160b', 'en:e270', 'en:sunflower-lecithin', 'en:e322', 'en:e322i', 'en:e339', 'en:e551', 'en:ingredients', 'en:wheat-flour', 'en:cereal', 'en:flour', 'en:wheat', 'en:cereal-flour', 'en:bacterial-cultures', 'en:pasteurised-milk', 'en:microbial-coagulating-enzyme', 'en:enzyme', 'en:coagulating-enzyme', 'en:colour', 'en:for-anticaking']`
  - `['en:fortified-wheat-flour', 'en:cereal', 'en:flour', 'en:wheat', 'en:cereal-flour', 'en:wheat-flour', 'en:cheddar', 'en:dairy', 'en:cheese', 'en:vegetable-oil', 'en:oil-and-fat', 'en:vegetable-oil-and-fat', 'en:salt', 'en:sugar', 'en:added-sugar', 'en:disaccharide', 'en:yeast', 'en:coating', 'en:autolyzed-yeast-extract', 'en:yeast-extract', 'en:e341i', 'en:e341', 'en:e503ii', 'en:e503', 'en:e500ii', 'en:e500', 'en:e375', 'en:iron', 'en:minerals', 'en:thiamin-mononitrate', 'en:thiamin', 'en:e101', 'en:folic-acid', 'en:folate', 'en:milk', 'en:bacterial-culture', 'en:enzyme', 'en:e160b', 'en:soya-bean', 'en:vegetable', 'en:legume', 'en:pulse', 'en:soya', 'en:canola', 'en:root-vegetable', 'en:rapeseed', 'en:sunflower', 'en:plant', 'en:paprika', 'en:condiment', 'en:spice', 'en:celery', 'en:stalk-vegetable', 'en:onion', 'en:onion-family-vegetable']`
  - `['en:fortified-wheat-flour', 'en:cereal', 'en:flour', 'en:wheat', 'en:cereal-flour', 'en:wheat-flour', 'en:sunflower-oil', 'en:oil-and-fat', 'en:vegetable-oil-and-fat', 'en:vegetable-oil', 'en:cheddar', 'en:dairy', 'en:cheese', 'en:parmigiano-reggiano', 'en:salt', 'en:yeast', 'en:sugar', 'en:added-sugar', 'en:disaccharide', 'fr:levure-autolysee', 'en:onion', 'en:vegetable', 'en:root-vegetable', 'en:onion-family-vegetable', 'en:condiment', 'en:butter', 'en:e160b', 'en:e341', 'en:e500ii', 'en:e500', 'en:e503ii', 'en:e503', 'fr:lait-culture-bacterienne', 'en:enzyme', 'fr:lait-bacterienne', 'en:barley']`

## ingredients_text
- **Type**: `list`
- **Valeurs uniques**: 15,781
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[{'lang': 'main', 'text': 'Pure organic maple syrup'}, {'lang': 'en', 'text': 'Pure organic maple syrup'}, {'lang': 'en', 'text': 'Pure organic maple syrup'}]`
  - `[{'lang': 'main', 'text': 'water, sugar, propylene glycol caramel color, ethyl vanillin, artificial flavor'}, {'lang': 'en', 'text': 'water, sugar, propylene glycol caramel color, ethyl vanillin, artificial flavor'}, {'lang': 'en', 'text': 'water, sugar, propylene glycol caramel color, ethyl vanillin, artificial flavor'}]`
  - `[{'lang': 'main', 'text': 'lowfat milk, vitamin A palmitate, vitamin D3'}, {'lang': 'en', 'text': 'lowfat milk, vitamin A palmitate, vitamin D3'}, {'lang': 'en', 'text': 'lowfat milk, vitamin A palmitate, vitamin D3'}]`
  - `[]`
  - `[]`
  - `[]`
  - `[{'lang': 'main', 'text': 'Ginger, water, salt, acetic acid, citric acid, aspartame, potassium sorbate (preservative), and fd&c red no. 40.'}, {'lang': 'en', 'text': 'Ginger, water, salt, acetic acid, citric acid, aspartame, potassium sorbate (preservative), and fd&c red no. 40.'}, {'lang': 'en', 'text': 'Ginger, water, salt, acetic acid, citric acid, aspartame, potassium sorbate (preservative), and fd&c red no. 40.'}]`
  - `[{'lang': 'main', 'text': "Œuf : moyen frais, catégorie Canada A. / Fromage cheddar fondu : fromage (lait, ingrédients de lait modifié, culture bactérienne, sel, présure ou enzyme microbienne, chlorure de calcium, colorant, lipase, acide sorbique), ingrédients de lait modifié, eau, citrate de sodium ou phosphate de sodium, glucose, acide acétique, sel, acide sorbique, lécithine de soya, carboxyméthylcellulose, colorant. / Galette de saucisse : Porc, eau, substances laitières modifies, sel, extrait sec de sirop demaïs, dextrose, épice. Contient: lait. /Muffin anglais: farine de blé enrichie, eau, levure, semoule de maïs, sel, huile végétale (canola ou soya), glucose-fructose/sucre, phosphate monocalcique, propionate de calcium, sulfate de calcium, chlorure d'ammonium, gluten de blé, esters tartriques des mono-et diglycérides acétylés. / Margarine : huile de canola, eau, huiles de palme et de palmiste modifiées, sel,monoglycérides végétales, lécithine de soja, benzoate de sodium, acide citrique, arôme naturel, colorant, palmitate de vitamine A, vitamine D3. / Huile pour le gril : huile de canola, lécithine de soya, arôme naturel."}, {'lang': 'fr', 'text': 'Œuf : moyen frais, catégorie Canada A. / Fromage cheddar fondu : fromage (<span class="allergen">lait</span>, ingrédients de lait modifié, culture bactérienne, sel, présure ou enzyme microbienne, chlorure de calcium, colorant, lipase, acide sorbique), ingrédients de lait modifié, eau, citrate de sodium ou phosphate de sodium, glucose, acide acétique, sel, acide sorbique, lécithine de soya, carboxyméthylcellulose, colorant. / Galette de saucisse : Porc, eau, substances laitières modifies, sel, extrait sec de sirop demaïs, dextrose, épice. Contient<span class="allergen">: lait</span>. /Muffin anglais: farine de blé enrichie, eau, levure, semoule de maïs, sel, huile végétale (canola ou soya), glucose-fructose/sucre, phosphate monocalcique, propionate de calcium, sulfate de calcium, chlorure d\'ammonium, <span class="allergen">gluten de blé</span>, esters tartriques des mono-et diglycérides acétylés. / Margarine : huile de canola, eau, huiles de palme et de palmiste modifiées, sel,monoglycérides végétales, <span class="allergen">lécithine de soja</span>, benzoate de sodium, acide citrique, arôme naturel, colorant, palmitate de vitamine A, vitamine D3. / Huile pour le gril : huile de canola, lécithine de soya, arôme naturel.'}, {'lang': 'fr', 'text': "Œuf : moyen frais, catégorie Canada A. / Fromage cheddar fondu : fromage (lait, ingrédients de lait modifié, culture bactérienne, sel, présure ou enzyme microbienne, chlorure de calcium, colorant, lipase, acide sorbique), ingrédients de lait modifié, eau, citrate de sodium ou phosphate de sodium, glucose, acide acétique, sel, acide sorbique, lécithine de soya, carboxyméthylcellulose, colorant. / Galette de saucisse : Porc, eau, substances laitières modifies, sel, extrait sec de sirop demaïs, dextrose, épice. Contient: lait. /Muffin anglais: farine de blé enrichie, eau, levure, semoule de maïs, sel, huile végétale (canola ou soya), glucose-fructose/sucre, phosphate monocalcique, propionate de calcium, sulfate de calcium, chlorure d'ammonium, gluten de blé, esters tartriques des mono-et diglycérides acétylés. / Margarine : huile de canola, eau, huiles de palme et de palmiste modifiées, sel,monoglycérides végétales, lécithine de soja, benzoate de sodium, acide citrique, arôme naturel, colorant, palmitate de vitamine A, vitamine D3. / Huile pour le gril : huile de canola, lécithine de soya, arôme naturel."}]`
  - `[]`
  - `[]`

## ingredients_with_specified_percent_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 15
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`
  - `0`

## ingredients_with_unspecified_percent_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 122
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `1`
  - `5`
  - `3`
  - `9`
  - `63`
  - `1`
  - `44`
  - `19`
  - `23`
  - `20`

## ingredients_without_ciqual_codes_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 97
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `1`
  - `3`
  - `2`
  - `7`
  - `40`
  - `1`
  - `20`
  - `12`
  - `15`
  - `10`

## ingredients_without_ciqual_codes
- **Type**: `list`
- **Valeurs uniques**: 13,082
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `['en:maple-syrup']`
  - `['en:artificial-flavouring', 'en:ethyl-vanillin', 'en:propylene-glycol-caramel-color']`
  - `['en:cholecalciferol', 'en:retinyl-palmitate']`
  - `['en:40', 'en:and-fd-c-red-no', 'en:e202', 'en:e260', 'en:e330', 'en:e951', 'en:preservative']`
  - `['en:canola', 'en:cholecalciferol', 'en:colour', 'en:e1104', 'en:e200', 'en:e211', 'en:e260', 'en:e282', 'en:e330', 'en:e339', 'en:e341', 'en:e466', 'en:e509', 'en:e510', 'en:e516', 'en:margarine', 'en:microbial-coagulating-enzyme', 'en:microbial-culture', 'en:natural-flavouring', 'en:oil', 'en:palm-kernel-oil', 'en:pork', 'en:rennet', 'en:sodium-citrate', 'en:soya', 'en:spice', 'en:vegetable-oil', 'en:wheat-gluten', 'fr:categorie-canada-a', 'fr:esters-tartriques-des-mono-et-diglycerides-acetyles', 'fr:extrait-sec-de-sirop-demais', 'fr:galette-de-saucisse', 'fr:huile-pour-le-gril', 'fr:ingredients-de-lait-modifie', 'fr:modifiees', 'fr:monoglycerides-vegetales', 'fr:moyen-frais', 'fr:muffin-anglais', 'fr:palmitate-de-vitamine-a', 'fr:substances-laitieres-modifies']`
  - `['en:blue-agave-syrup']`
  - `['en:artificial-flavouring', 'en:chocolate', 'en:e202', 'en:e282', 'en:e339', 'en:e407', 'en:e410', 'en:e412', 'en:e415', 'en:e500ii', 'en:microbial-culture', 'en:natural-flavouring', 'en:sodium-citrate', 'fr:acide-sobriquet', 'fr:esters-monoacides-gras-de-propyleneglycol', 'fr:gomme-de-crllulose', 'fr:mono-et-diglycerides', 'fr:ou-de-canola', 'fr:phosphate-d-aluminium', 'fr:shortening-d-huile-de-canola-et-de-palme-modifie-et-de-palmiste-modifie']`
  - `['en:bacterial-cultures', 'en:colour', 'en:e160b', 'en:e270', 'en:e330', 'en:e339', 'en:e551', 'en:for-anticaking', 'en:ingredients', 'en:microbial-coagulating-enzyme', 'en:sunflower-lecithin', 'en:whey']`
  - `['en:bacterial-culture', 'en:canola', 'en:coating', 'en:e101', 'en:e160b', 'en:e341i', 'en:e375', 'en:e500ii', 'en:e503ii', 'en:enzyme', 'en:folic-acid', 'en:iron', 'en:sunflower', 'en:thiamin-mononitrate', 'en:vegetable-oil']`
  - `['en:barley', 'en:condiment', 'en:e160b', 'en:e341', 'en:e500ii', 'en:e503ii', 'en:enzyme', 'fr:lait-bacterienne', 'fr:lait-culture-bacterienne', 'fr:levure-autolysee']`

## ingredients
- **Type**: `STRING`
- **Valeurs uniques**: 15,576
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `[{"percent_max":100.0,"percent_min":100.0,"is_in_taxonomy":1,"percent_estimate":100.0,"vegan":"yes","id":"en:maple-syrup","text":"maple syrup","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":"en:organic","origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":20.0,"is_in_taxonomy":null,"percent_estimate":60.0,"vegan":"yes","id":"en:water","text":"water","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":20.0,"vegan":"yes","id":"en:sugar","text":"sugar","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":10.0,"vegan":null,"id":"en:propylene-glycol-caramel-color","text":"propylene glycol caramel color","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":5.0,"vegan":null,"id":"en:ethyl-vanillin","text":"ethyl vanillin","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":5.0,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":5.0,"vegan":"maybe","id":"en:artificial-flavouring","text":"artificial flavor","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":33.333333333333336,"is_in_taxonomy":1,"percent_estimate":66.66666666666667,"vegan":"no","id":"en:skimmed-milk","text":"lowfat milk","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":16.666666666666664,"vegan":"yes","id":"en:retinyl-palmitate","text":"vitamin A palmitate","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":16.666666666666657,"vegan":"maybe","id":"en:cholecalciferol","text":"vitamin D3","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":42.3,"is_in_taxonomy":null,"percent_estimate":71.15,"vegan":"yes","id":"en:ginger","text":"Ginger","vegetarian":"yes","ciqual_food_code":"11074","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":14.424999999999997,"vegan":"yes","id":"en:water","text":"water","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":"yes","id":"en:salt","text":"salt","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":"yes","id":"en:e260","text":"acetic acid","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":"yes","id":"en:e330","text":"citric acid","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":"yes","id":"en:e951","text":"aspartame","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":"yes","id":"en:e202","text":"potassium sorbate","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":null,"id":"en:preservative","text":"preservative","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":0.55,"vegan":null,"id":"en:and-fd-c-red-no","text":"and fd&c red no","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.1,"percent_min":0.0,"is_in_taxonomy":null,"percent_estimate":11.125000000000014,"vegan":null,"id":"en:40","text":"40","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":1.6666666666666667,"is_in_taxonomy":1,"percent_estimate":50.833333333333336,"vegan":"no","id":"en:egg","text":"Œuf","vegetarian":"yes","ciqual_food_code":"22000","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":100.0,"percent_min":1.6666666666666667,"is_in_taxonomy":0,"percent_estimate":50.833333333333336,"vegan":null,"id":"fr:moyen-frais","text":"moyen frais","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":"egg-indoor-code3","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":24.583333333333332,"vegan":null,"id":"fr:categorie-canada-a","text":"catégorie Canada A","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":12.291666666666664,"vegan":"no","id":"en:cheddar","text":"Fromage cheddar","vegetarian":"maybe","ciqual_food_code":"12726","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.145833333333332,"vegan":"no","id":"en:cheese","text":"fromage","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"12999"},{"percent_max":16.666666666666668,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.145833333333332,"vegan":"no","id":"en:milk","text":"lait","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"}],"ecobalyse_code":null,"processing":"en:melted","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":6.145833333333329,"vegan":null,"id":"fr:ingredients-de-lait-modifie","text":"ingrédients de lait modifié","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":20.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.0729166666666643,"vegan":"maybe","id":"en:microbial-culture","text":"culture bactérienne","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.59,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.59,"vegan":"maybe","id":"en:rennet","text":"présure","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.59,"vegan":"yes","id":"en:microbial-coagulating-enzyme","text":"enzyme microbienne","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.59,"vegan":"yes","id":"en:e509","text":"chlorure de calcium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.3564583333333218,"vegan":null,"id":"en:colour","text":"colorant","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.1782291666666609,"vegan":"maybe","id":"en:e1104","text":"lipase","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.08911458333332689,"vegan":"yes","id":"en:e200","text":"acide sorbique","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.044557291666663446,"vegan":null,"id":"fr:ingredients-de-lait-modifie","text":"ingrédients de lait modifié","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.022278645833331723,"vegan":"yes","id":"en:water","text":"eau","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"tap-water","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.011139322916662309,"vegan":null,"id":"en:sodium-citrate","text":"citrate de sodium","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.005569661458331154,"vegan":"yes","id":"en:e339","text":"phosphate de sodium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.00278483072916913,"vegan":"yes","id":"en:glucose","text":"glucose","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.001392415364584565,"vegan":"yes","id":"en:e260","text":"acide acétique","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0006962076822958352,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0003481038411479176,"vegan":"yes","id":"en:e200","text":"acide sorbique","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0001740519205739588,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soya","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.00008702596028342668,"vegan":"yes","id":"en:e466","text":"carboxyméthylcellulose","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.00004351298014171334,"vegan":null,"id":"en:colour","text":"colorant","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.00002175649007085667,"vegan":null,"id":"fr:galette-de-saucisse","text":"Galette de saucisse","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.00002175649007085667,"vegan":"no","id":"en:pork","text":"Porc","vegetarian":"no","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.000010878245035428336,"vegan":"yes","id":"en:water","text":"eau","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"tap-water","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":5.439122517714168e-6,"vegan":null,"id":"fr:substances-laitieres-modifies","text":"substances laitières modifies","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.719561258857084e-6,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":1.3597806258758283e-6,"vegan":null,"id":"fr:extrait-sec-de-sirop-demais","text":"extrait sec de sirop demaïs","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.798903129379141e-7,"vegan":"yes","id":"en:dextrose","text":"dextrose","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.3994516002167074e-7,"vegan":"yes","id":"en:spice","text":"épice","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":1.6997258001083537e-7,"vegan":null,"id":"fr:muffin-anglais","text":"Muffin anglais","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.6997258001083537e-7,"vegan":"yes","id":"en:fortified-wheat-flour","text":"farine de blé enrichie","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"flour","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9410"}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":8.498629000541769e-8,"vegan":"yes","id":"en:water","text":"eau","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"tap-water","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":4.2493141449995164e-8,"vegan":"yes","id":"en:yeast","text":"levure","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"11009"},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.1246570724997582e-8,"vegan":"yes","id":"en:cornmeal","text":"semoule de maïs","vegetarian":"yes","ciqual_food_code":"9615","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0623281809785112e-8,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.311640904892556e-9,"vegan":"yes","id":"en:vegetable-oil","text":"huile végétale","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":"maybe","ingredients":[{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.655820452446278e-9,"vegan":"yes","id":"en:canola","text":"canola","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"rapeseed-non-eu","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.59,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.655820452446278e-9,"vegan":"yes","id":"en:soya","text":"soya","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.18,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.655824005159957e-9,"vegan":"yes","id":"en:glucose-fructose","text":"glucose-fructose","vegetarian":"yes","ciqual_food_code":"31077","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.3279120025799784e-9,"vegan":"yes","id":"en:sugar","text":"sucre","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.63959554003668e-10,"vegan":"yes","id":"en:e341","text":"phosphate monocalcique","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.31979777001834e-10,"vegan":"yes","id":"en:e282","text":"propionate de calcium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.65989888500917e-10,"vegan":"yes","id":"en:e516","text":"sulfate de calcium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":8.29913915367797e-11,"vegan":"yes","id":"en:e510","text":"chlorure d'ammonium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":4.149569576838985e-11,"vegan":"yes","id":"en:wheat-gluten","text":"gluten de blé","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":2.0747847884194925e-11,"vegan":null,"id":"fr:esters-tartriques-des-mono-et-diglycerides-acetyles","text":"esters tartriques des mono- et diglycérides acétylés","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0373923942097463e-11,"vegan":null,"id":"en:margarine","text":"Margarine","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0373923942097463e-11,"vegan":"yes","id":"en:canola-oil","text":"huile de canola","vegetarian":"yes","ciqual_food_code":"17130","percent":null,"from_palm_oil":"no","ingredients":null,"ecobalyse_code":"rapeseed-oil","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.186961971048731e-12,"vegan":"yes","id":"en:water","text":"eau","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"tap-water","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.5934809855243657e-12,"vegan":"maybe","id":"en:oil","text":"huiles","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":"maybe","ingredients":[{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.2967404927621828e-12,"vegan":"yes","id":"en:palm-oil","text":"huile de palme","vegetarian":"yes","ciqual_food_code":"16129","percent":null,"from_palm_oil":"yes","ingredients":null,"ecobalyse_code":"refined-palm-oil","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.52,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.2967404927621828e-12,"vegan":"yes","id":"en:palm-kernel-oil","text":"huile de palmiste","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":"yes","ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":1.2931877790833823e-12,"vegan":null,"id":"fr:modifiees","text":"modifiées","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.465938895416912e-13,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":3.268496584496461e-13,"vegan":null,"id":"fr:monoglycerides-vegetales","text":"monoglycérides végétales","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.6342482922482304e-13,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soja","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":8.526512829121202e-14,"vegan":"yes","id":"en:e211","text":"benzoate de sodium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":4.263256414560601e-14,"vegan":"yes","id":"en:e330","text":"acide citrique","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.1316282072803006e-14,"vegan":"maybe","id":"en:natural-flavouring","text":"arôme naturel","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.4210854715202004e-14,"vegan":null,"id":"en:colour","text":"colorant","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":7.105427357601002e-15,"vegan":null,"id":"fr:palmitate-de-vitamine-a","text":"palmitate de vitamine A","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"maybe","id":"en:cholecalciferol","text":"vitamine D3","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0,"vegan":null,"id":"fr:huile-pour-le-gril","text":"Huile pour le gril","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:canola-oil","text":"huile de canola","vegetarian":"yes","ciqual_food_code":"17130","percent":null,"from_palm_oil":"no","ingredients":null,"ecobalyse_code":"rapeseed-oil","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soya","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.04,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"maybe","id":"en:natural-flavouring","text":"arôme naturel","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":100.0,"is_in_taxonomy":0,"percent_estimate":100.0,"vegan":null,"id":"en:blue-agave-syrup","text":"blue agave syrup","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":"en:organic","origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":3.8461538461538463,"is_in_taxonomy":1,"percent_estimate":51.92307692307692,"vegan":"yes","id":"en:sugar","text":"Sucré","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":24.03846153846154,"vegan":"yes","id":"en:fortified-wheat-flour","text":"farine de blé enrichie","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"flour","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9410"},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":12.019230769230774,"vegan":"yes","id":"en:water","text":"eau","vegetarian":"yes","ciqual_food_code":"18066","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"tap-water","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.009615384615387,"vegan":"no","id":"en:liquid-whole-egg","text":"œufs entiers liquides","vegetarian":"yes","ciqual_food_code":"22000","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"egg-indoor-code3","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":20.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.0048076923076934,"vegan":"yes","id":"en:soya-oil","text":"huile de soya","vegetarian":"yes","ciqual_food_code":"17420","percent":null,"from_palm_oil":"no","ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":16.666666666666668,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":1.5024038461538467,"vegan":null,"id":"fr:ou-de-canola","text":"ou de canola","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":14.285714285714286,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.7512019230769198,"vegan":"maybe","id":"en:chocolate","text":"de chocolat","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":14.285714285714286,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.3756009615384599,"vegan":"yes","id":"en:sugar","text":"sucré","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":7.142857142857143,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.18780048076922995,"vegan":"maybe","id":"en:chocolate","text":"chocolat","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":"en:unsweetened","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":4.761904761904762,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.09390024038461497,"vegan":"yes","id":"en:cocoa-butter","text":"beurre de cacao","vegetarian":"yes","ciqual_food_code":"16030","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":3.5714285714285716,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.04695012019230749,"vegan":"yes","id":"en:dextrose","text":"dextrose","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":2.857142857142857,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.023475060096153744,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soya","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.380952380952381,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.023475060096153744,"vegan":"yes","id":"en:vanilla-extract","text":"extrait de vanille","vegetarian":"yes","ciqual_food_code":"11065","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":"en:peeling","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":12.5,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.3756009615384599,"vegan":"no","id":"en:sour-cream","text":"crème sûre","vegetarian":"yes","ciqual_food_code":"19402","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":12.5,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.18780048076922995,"vegan":"no","id":"en:cream","text":"crème","vegetarian":"yes","ciqual_food_code":"19402","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":6.25,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.09390024038461497,"vegan":"no","id":"en:milk","text":"lait","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":4.166666666666667,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.04695012019230749,"vegan":"no","id":"en:modified-milk-ingredients","text":"substances laitières modifiées","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":3.125,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.023475060096153744,"vegan":"yes","id":"en:modified-corn-starch","text":"amidon de maïs modifié","vegetarian":"yes","ciqual_food_code":"9510","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.5,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.011737530048076872,"vegan":"yes","id":"en:e412","text":"gomme de guar","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0833333333333335,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.005868765024038436,"vegan":"yes","id":"en:e407","text":"carraghénine","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.7857142857142858,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.002934382512019218,"vegan":"yes","id":"en:e410","text":"gomme de caroube","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.5625,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.001467191256009609,"vegan":null,"id":"en:sodium-citrate","text":"citrate de sodium","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.3888888888888888,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0007335956280047906,"vegan":"yes","id":"en:e339","text":"phosphate de sodium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.25,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0007335956280047906,"vegan":"maybe","id":"en:microbial-culture","text":"culture bactérienne","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":11.11111111111111,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.1878004807692264,"vegan":"yes","id":"en:cocoa-powder","text":"poudre de cacao","vegetarian":"yes","ciqual_food_code":"18100","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":10.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0939002403846132,"vegan":"yes","id":"en:modified-corn-starch","text":"amidon de maïs modifié","vegetarian":"yes","ciqual_food_code":"9510","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":9.090909090909092,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0469501201923066,"vegan":null,"id":"fr:shortening-d-huile-de-canola-et-de-palme-modifie-et-de-palmiste-modifie","text":"shortening d'huile de canola et de palme modifié et de palmiste modifié","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":8.333333333333334,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0234750600961533,"vegan":"maybe","id":"en:chocolate-chunk","text":"morceaux de chocolat","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":8.333333333333334,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.01173753004807665,"vegan":"yes","id":"en:sugar","text":"sucré","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":4.166666666666667,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.005868765024038325,"vegan":"maybe","id":"en:chocolate","text":"chocolat","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":"en:unsweetened","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.777777777777778,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0029343825120191624,"vegan":"yes","id":"en:cocoa-butter","text":"beurre de cacao","vegetarian":"yes","ciqual_food_code":"16030","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0833333333333335,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0014671912560095812,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soya","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.6666666666666667,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0014671912560095812,"vegan":"maybe","id":"en:artificial-flavouring","text":"arôme artificiel","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31005"},{"percent_max":7.6923076923076925,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.011737530048080203,"vegan":"yes","id":"en:e500ii","text":"bicarbonate de sodium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":7.142857142857143,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.005868765024040101,"vegan":"yes","id":"en:e339","text":"phosphate de sodium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":6.666666666666667,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0029343825120236033,"vegan":null,"id":"fr:phosphate-d-aluminium","text":"phosphate d'aluminium","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":6.25,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0014671912560118017,"vegan":null,"id":"fr:esters-monoacides-gras-de-propyleneglycol","text":"esters monoacides gras de propylénéglycol","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":5.882352941176471,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0007335956280059008,"vegan":"no","id":"en:skimmed-milk-powder","text":"poudre de lait écrémé","vegetarian":"yes","ciqual_food_code":"19054","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk-powder","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0003667978140029504,"vegan":"yes","id":"en:salt","text":"sel","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0001833989069979225,"vegan":null,"id":"fr:mono-et-diglycerides","text":"mono- et diglycérides","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.00009169945349896125,"vegan":"yes","id":"en:e415","text":"gomme de xanthane","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.00004584972674592791,"vegan":null,"id":"fr:gomme-de-crllulose","text":"gomme de crllulose","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.000022924863372963955,"vegan":"yes","id":"en:soya-lecithin","text":"lécithine de soya","vegetarian":"yes","ciqual_food_code":"42200","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.000011462431686481978,"vegan":"yes","id":"en:e202","text":"SORBATE de potassium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.731215843240989e-6,"vegan":"yes","id":"en:e282","text":"propionate de calcium","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":2.865607925173208e-6,"vegan":null,"id":"fr:acide-sobriquet","text":"acide sobriquet","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.889,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.865607925173208e-6,"vegan":"maybe","id":"en:natural-flavouring","text":"arôme naturel","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":6.666666666666667,"is_in_taxonomy":1,"percent_estimate":53.333333333333336,"vegan":"maybe","id":"en:pasta","text":"PASTA","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":100.0,"percent_min":6.666666666666667,"is_in_taxonomy":1,"percent_estimate":53.333333333333336,"vegan":"yes","id":"en:wheat-flour","text":"WHEAT FLOUR","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"flour-organic","processing":null,"labels":"en:organic","origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9410"}],"ecobalyse_code":null,"processing":null,"labels":"en:organic","origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9810"},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":23.333333333333332,"vegan":"no","id":"en:whey","text":"WHEY","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":11.666666666666664,"vegan":"no","id":"en:sour-cream","text":"CULTURED CREAM","vegetarian":"yes","ciqual_food_code":"19402","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.833333333333332,"vegan":"no","id":"en:cream","text":"CREAM","vegetarian":"yes","ciqual_food_code":"19402","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":16.666666666666668,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":5.833333333333332,"vegan":null,"id":"en:bacterial-cultures","text":"BACTERIAL CULTURES","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.833333333333329,"vegan":"no","id":"en:skimmed-milk","text":"SKIM MILK","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.9649122807017501,"vegan":"yes","id":"en:salt","text":"SALT","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.9649122807017501,"vegan":"no","id":"en:butter","text":"BUTTER","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"butter","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"16400"},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.9649122807017501,"vegan":"no","id":"en:cheddar","text":"CHEDDAR CHEESE","vegetarian":"maybe","ciqual_food_code":"12726","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.48245614035087503,"vegan":"no","id":"en:pasteurised-milk","text":"PASTEURIZED MILK","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":0.9649122807017501,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.24122807017543751,"vegan":null,"id":"en:bacterial-cultures","text":"BACTERIAL CULTURES","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.6432748538011667,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.12061403508771873,"vegan":"yes","id":"en:salt","text":"SALT","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.48245614035087503,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.12061403508771873,"vegan":"en:yes","id":"en:microbial-coagulating-enzyme","text":"MICROBIAL ENZYME","vegetarian":"en:yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":"en:vegan","origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":"en:dried","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.9649122807017501,"vegan":"yes","id":"en:corn-starch","text":"CORN STARCH","vegetarian":"yes","ciqual_food_code":"9510","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.9649122807017501,"vegan":"yes","id":"en:e330","text":"CITRIC ACID","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.5043859649122808,"vegan":"yes","id":"en:e160b","text":"ANNATTO","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.5043859649122808,"vegan":null,"id":"en:colour","text":"FOR COLOUR","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":"en:extract","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.25219298245613686,"vegan":"yes","id":"en:e270","text":"LACTIC ACID","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.12609649122806843,"vegan":"yes","id":"en:sunflower-lecithin","text":"SUNFLOWER LECITHIN","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.06304824561403422,"vegan":"yes","id":"en:e339","text":"SODIUM PHOSPHATE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.031524122807013555,"vegan":"yes","id":"en:e551","text":"SILICON DIOXIDE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.031524122807013555,"vegan":null,"id":"en:for-anticaking","text":"FOR ANTICAKING","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":1.9298245614035001,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.031524122807013555,"vegan":null,"id":"en:ingredients","text":"INGREDIENTS","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":9.090909090909092,"is_in_taxonomy":1,"percent_estimate":54.54545454545455,"vegan":"yes","id":"en:fortified-wheat-flour","text":"Enriched wheat flour","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":100.0,"percent_min":1.8181818181818183,"is_in_taxonomy":1,"percent_estimate":28.181818181818183,"vegan":"maybe","id":"en:e375","text":"niacin","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":13.181818181818182,"vegan":null,"id":"en:iron","text":"iron","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.59090909090909,"vegan":"maybe","id":"en:thiamin-mononitrate","text":"thiamine mononitrate","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.2954545454545467,"vegan":"maybe","id":"en:e101","text":"riboflavin","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":20.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.2954545454545467,"vegan":"yes","id":"en:folic-acid","text":"folic acid","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":"flour","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9410"},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":22.727272727272727,"vegan":"no","id":"en:cheddar","text":"Cheddar cheese","vegetarian":"maybe","ciqual_food_code":"12726","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":11.363636363636363,"vegan":"no","id":"en:milk","text":"milk","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"milk","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"19051"},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":5.681818181818182,"vegan":null,"id":"en:bacterial-culture","text":"bacterial culture","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":10.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.84090909090909,"vegan":"yes","id":"en:salt","text":"salt","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":10.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.420454545454545,"vegan":"maybe","id":"en:enzyme","text":"enzymes","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":10.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.4204545454545467,"vegan":"yes","id":"en:e160b","text":"annatto","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":11.36363636363636,"vegan":"yes","id":"en:vegetable-oil","text":"Vegetable oil","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":"maybe","ingredients":[{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.68181818181818,"vegan":"yes","id":"en:soya-bean","text":"soybean","vegetarian":"yes","ciqual_food_code":"20901","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":16.666666666666668,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.84090909090909,"vegan":"yes","id":"en:canola","text":"canola","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"rapeseed-non-eu","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":11.111111111111112,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":2.84090909090909,"vegan":"yes","id":"en:sunflower","text":"sunflower","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sunflower-non-eu","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":10.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.0,"vegan":"yes","id":"en:salt","text":"Salt","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:sugar","text":"Sugar","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:yeast","text":"Yeast","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"11009"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"maybe","id":"en:coating","text":"Seasoning","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:paprika","text":"contains paprika","vegetarian":"yes","ciqual_food_code":"11049","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:celery","text":"celery","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"celery-eu","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"20055"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:onion","text":"onion","vegetarian":"yes","ciqual_food_code":"20034","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"onion-non-eu","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:autolyzed-yeast-extract","text":"Autolyzed yeast extract","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"11009"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:e341i","text":"Monocalcium phosphate","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:e503ii","text":"Ammonium bicarbonate","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":6.36363636363636,"vegan":"yes","id":"en:e500ii","text":"Baking soda","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`
  - `[{"percent_max":100.0,"percent_min":6.666666666666667,"is_in_taxonomy":1,"percent_estimate":53.333333333333336,"vegan":"yes","id":"en:fortified-wheat-flour","text":"FARINE DE BLÉ ENRICHIE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"flour","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"9410"},{"percent_max":50.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":23.333333333333332,"vegan":"yes","id":"en:sunflower-oil","text":"HUILE VÉGÉTALE et TOURNESOL","vegetarian":"yes","ciqual_food_code":"17440","percent":null,"from_palm_oil":"no","ingredients":null,"ecobalyse_code":"sunflower-oil","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":11.666666666666664,"vegan":"no","id":"en:cheddar","text":"CHEDDAR","vegetarian":"maybe","ciqual_food_code":"12726","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":33.333333333333336,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":5.833333333333332,"vegan":null,"id":"fr:lait-culture-bacterienne","text":"LAIT CULTURE BACTÉRIENNE","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0,"vegan":"yes","id":"en:salt","text":"SEL","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0,"vegan":"maybe","id":"en:enzyme","text":"ENZYMES","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.833333333333332,"vegan":"yes","id":"en:e160b","text":"ROCOU","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":5.833333333333329,"vegan":"no","id":"en:parmigiano-reggiano","text":"PARMESAN","vegetarian":"maybe","ciqual_food_code":"12120","percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":25.0,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":2.9166666666666643,"vegan":null,"id":"fr:lait-bacterienne","text":"LAIT BACTÉRIENNE","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0,"vegan":"yes","id":"en:salt","text":"SEL","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.9166666666666643,"vegan":"maybe","id":"en:enzyme","text":"ENZYMES","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0,"vegan":"yes","id":"en:salt","text":"SEL","vegetarian":"yes","ciqual_food_code":"11058","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":2.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":1.0,"vegan":"yes","id":"en:yeast","text":"LEVURE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"11009"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:sugar","text":"SUCRE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"sugar","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"31016"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":0,"percent_estimate":0.0,"vegan":null,"id":"fr:levure-autolysee","text":"LEVURE AUTOLYSÉE","vegetarian":null,"ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":[{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:barley","text":"ORGE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}],"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:onion","text":"OIGNON","vegetarian":"yes","ciqual_food_code":"20034","percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"onion-non-eu","processing":"en:powder","labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"maybe","id":"en:condiment","text":"ASSAISONNEMENT","vegetarian":"maybe","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"no","id":"en:butter","text":"BEURRE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":"butter","processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":"16400"},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:e160b","text":"ROCOU","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:e341","text":"PHOSPHATE MONOCALCIQUE","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":0.0,"vegan":"yes","id":"en:e500ii","text":"BICARBONATE DE SODIUM","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null},{"percent_max":0.0,"percent_min":0.0,"is_in_taxonomy":1,"percent_estimate":3.8333333333333286,"vegan":"yes","id":"en:e503ii","text":"BICARBONATE D'AMMONIUM","vegetarian":"yes","ciqual_food_code":null,"percent":null,"from_palm_oil":null,"ingredients":null,"ecobalyse_code":null,"processing":null,"labels":null,"origins":null,"ecobalyse_proxy_code":null,"quantity":null,"quantity_g":null,"ciqual_proxy_food_code":null}]`

## known_ingredients_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 107
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `3`
  - `6`
  - `8`
  - `10`
  - `75`
  - `0`
  - `62`
  - `32`
  - `54`
  - `33`

## labels_tags
- **Type**: `list`
- **Valeurs uniques**: 4,099
- **Valeurs nulles**: 64,291 (67.82%)
- **Exemples de valeurs**:
  - `['en:organic', 'en:no-gmos', 'en:non-gmo-project']`
  - `['en:real-california-milk']`
  - `[]`
  - `[]`
  - `['en:green-dot']`
  - `['en:fair-trade', 'en:no-gluten', 'en:organic', 'en:vegetarian', 'en:kosher', 'en:no-gmos', 'en:vegan', 'en:canada-organic', 'en:fairtrade-usa', 'en:non-gmo-project', 'en:orthodox-union-kosher', 'en:certified-by-quality-assurance-international']`
  - `[]`
  - `['en:no-artificial-flavors', 'en:no-colorings']`
  - `[]`
  - `[]`

## labels
- **Type**: `STRING`
- **Valeurs uniques**: 5,221
- **Valeurs nulles**: 64,529 (68.07%)
- **Exemples de valeurs**:
  - `Organic,No GMOs,Non GMO project`
  - `Real California Milk`
  - ``
  - `Green Dot`
  - `Fair trade, No gluten, Organic, Vegetarian, Kosher, No GMOs, Vegan, Canada Organic, Fairtrade USA, Non GMO project, Orthodox Union Kosher, Certified by Quality Assurance International`
  - ``
  - `No artificial flavors, No colorings`
  - ``
  - ``
  - ``

## lang
- **Type**: `STRING`
- **Valeurs uniques**: 60
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `en`
  - `en`
  - `en`
  - `fr`
  - `en`
  - `fr`
  - `en`
  - `fr`
  - `en`
  - `en`

## languages_tags
- **Type**: `list`
- **Valeurs uniques**: 235
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['en:english', 'en:french', 'en:2', 'en:multilingual']`
  - `['en:english', 'en:1']`
  - `['en:english', 'en:1']`
  - `['en:french', 'en:1']`
  - `['en:english', 'en:1']`
  - `['en:french', 'en:1']`
  - `['en:english', 'en:1']`
  - `['en:french', 'en:1']`
  - `['en:english', 'en:1']`
  - `['en:0']`

## last_edit_dates_tags
- **Type**: `list`
- **Valeurs uniques**: 2,276
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['2024-10-17', '2024-10', '2024']`
  - `['2020-07-02', '2020-07', '2020']`
  - `['2024-11-13', '2024-11', '2024']`
  - `['2022-08-10', '2022-08', '2022']`
  - `['2021-09-16', '2021-09', '2021']`
  - `['2023-09-02', '2023-09', '2023']`
  - `['2020-03-01', '2020-03', '2020']`
  - `['2022-02-10', '2022-02', '2022']`
  - `['2017-03-30', '2017-03', '2017']`
  - `['2023-06-30', '2023-06', '2023']`

## last_editor
- **Type**: `STRING`
- **Valeurs uniques**: 1,515
- **Valeurs nulles**: 1,645 (1.74%)
- **Exemples de valeurs**:
  - `fighter-food-facts`
  - `inf`
  - `kiliweb`
  - `kiliweb`
  - `jeanko`
  - `date-limite-app`
  - `packbot`
  - `naruyoko`
  - `org-label-non-gmo-project`
  - `packbot`

## last_image_t
- **Type**: `NUMBER`
- **Valeurs uniques**: 86,983
- **Valeurs nulles**: 7,809 (8.24%)
- **Exemples de valeurs**:
  - `1660213050`
  - `1593726979`
  - `1494699730`
  - `1610433267`
  - `1631796150`
  - `1519615071`
  - `1574639169`
  - `1480706178`
  - `1490826795`
  - `1525644346`

## last_modified_by
- **Type**: `STRING`
- **Valeurs uniques**: 1,514
- **Valeurs nulles**: 1,785 (1.88%)
- **Exemples de valeurs**:
  - `fighter-food-facts`
  - `inf`
  - `kiliweb`
  - `kiliweb`
  - `jeanko`
  - `date-limite-app`
  - `packbot`
  - `naruyoko`
  - `org-label-non-gmo-project`
  - `packbot`

## last_modified_t
- **Type**: `NUMBER`
- **Valeurs uniques**: 89,170
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `1729151192`
  - `1593726999`
  - `1731471549`
  - `1660153152`
  - `1631796150`
  - `1693658788`
  - `1583090351`
  - `1644532900`
  - `1490826795`
  - `1688095557`

## last_updated_t
- **Type**: `NUMBER`
- **Valeurs uniques**: 61,694
- **Valeurs nulles**: 1 (0.00%)
- **Exemples de valeurs**:
  - `1734386632`
  - `1707490480`
  - `1731471549`
  - `1707492215`
  - `1707492218`
  - `1707492218`
  - `1707492220`
  - `1734752918`
  - `1707492796`
  - `1707492798`

## link
- **Type**: `STRING`
- **Valeurs uniques**: 2,399
- **Valeurs nulles**: 84,833 (89.48%)
- **Exemples de valeurs**:
  - ``
  - ``
  - ``
  - `www.oakrun.com`
  - ``
  - ``
  - ``
  - ``
  - ``
  - ``

## main_countries_tags
- **Type**: `list`
- **Valeurs uniques**: 1
- **Valeurs nulles**: 1 (0.00%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## manufacturing_places_tags
- **Type**: `list`
- **Valeurs uniques**: 602
- **Valeurs nulles**: 84,584 (89.22%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `['ancaster', 'ontario']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['thailand']`

## manufacturing_places
- **Type**: `STRING`
- **Valeurs uniques**: 677
- **Valeurs nulles**: 84,584 (89.22%)
- **Exemples de valeurs**:
  - ``
  - ``
  - ``
  - `Ancaster,Ontario`
  - ``
  - ``
  - ``
  - ``
  - ``
  - `Thailand`

## max_imgid
- **Type**: `NUMBER`
- **Valeurs uniques**: 50
- **Valeurs nulles**: 7,810 (8.24%)
- **Exemples de valeurs**:
  - `1`
  - `3`
  - `1`
  - `3`
  - `3`
  - `6`
  - `2`
  - `3`
  - `1`
  - `1`

## minerals_tags
- **Type**: `list`
- **Valeurs uniques**: 550
- **Valeurs nulles**: 71,384 (75.30%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:calcium-chloride', 'en:sodium-phosphate', 'en:calcium-sulfate']`
  - `[]`
  - `[]`

## misc_tags
- **Type**: `list`
- **Valeurs uniques**: 6,624
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['en:ecoscore-changed', 'en:ecoscore-computed', 'en:ecoscore-extended-data-not-computed', 'en:ecoscore-grade-changed', 'en:ecoscore-missing-data-labels', 'en:ecoscore-missing-data-no-packagings', 'en:ecoscore-missing-data-origins', 'en:ecoscore-missing-data-packagings', 'en:ecoscore-missing-data-warning', 'en:nutriscore-2021-better-than-2023', 'en:nutriscore-2021-d-2023-e', 'en:nutriscore-2021-different-from-2023', 'en:nutriscore-computed', 'en:nutrition-fruits-vegetables-legumes-estimate-from-ingredients', 'en:nutrition-fruits-vegetables-nuts-estimate-from-ingredients', 'en:nutrition-no-fiber', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-empty', 'en:packagings-not-complete', 'en:packagings-number-of-components-0']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutrition-not-enough-data-to-compute-nutrition-score', 'en:nutriscore-missing-nutrition-data', 'en:nutriscore-missing-nutrition-data-energy', 'en:nutriscore-missing-nutrition-data-fat', 'en:nutriscore-missing-nutrition-data-saturated-fat', 'en:nutriscore-missing-nutrition-data-sugars', 'en:nutriscore-missing-nutrition-data-sodium', 'en:nutriscore-missing-nutrition-data-proteins', 'en:nutrition-no-fiber', 'en:nutriscore-not-computed', 'en:nutrition-fruits-vegetables-nuts-estimate-from-ingredients', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:nutrition-fruits-vegetables-legumes-estimate-from-ingredients', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:ecoscore-extended-data-not-computed', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutriscore-not-computed', 'en:nutrition-all-nutriscore-values-known', 'en:nutrition-fruits-vegetables-legumes-estimate-from-ingredients', 'en:nutrition-fruits-vegetables-nuts-estimate-from-ingredients', 'en:packagings-empty', 'en:packagings-not-complete', 'en:packagings-number-of-components-0', 'en:main-countries-no-scans']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutriscore-not-computed', 'en:nutrition-no-fruits-vegetables-nuts', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutrition-no-fiber', 'en:nutriscore-not-computed', 'en:nutrition-no-fruits-vegetables-nuts', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutrition-no-fiber', 'en:nutriscore-not-computed', 'en:nutrition-no-fruits-vegetables-nuts', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutriscore-not-computed', 'en:nutrition-fruits-vegetables-nuts-estimate-from-ingredients', 'en:nutrition-all-nutriscore-values-known', 'en:nutrition-fruits-vegetables-legumes-estimate-from-ingredients', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:ecoscore-changed', 'en:ecoscore-computed', 'en:ecoscore-extended-data-not-computed', 'en:ecoscore-missing-data-labels', 'en:ecoscore-missing-data-origins', 'en:ecoscore-missing-data-warning', 'en:forest-footprint-a', 'en:forest-footprint-computed', 'en:nutriscore-2021-d-2023-d', 'en:nutriscore-2021-same-as-2023', 'en:nutriscore-computed', 'en:nutrition-all-nutriscore-values-known', 'en:nutrition-fruits-vegetables-legumes-estimate-from-ingredients', 'en:nutrition-fruits-vegetables-nuts-estimate-from-ingredients', 'en:packagings-not-complete', 'en:packagings-not-empty', 'en:packagings-not-empty-but-not-complete', 'en:packagings-number-of-components-1']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutrition-not-enough-data-to-compute-nutrition-score', 'en:nutriscore-missing-nutrition-data', 'en:nutriscore-missing-nutrition-data-energy', 'en:nutriscore-missing-nutrition-data-fat', 'en:nutriscore-missing-nutrition-data-saturated-fat', 'en:nutriscore-missing-nutrition-data-sugars', 'en:nutriscore-missing-nutrition-data-sodium', 'en:nutriscore-missing-nutrition-data-proteins', 'en:nutrition-no-fiber', 'en:nutriscore-not-computed', 'en:nutrition-no-fruits-vegetables-nuts', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`
  - `['en:packagings-number-of-components-0', 'en:ecoscore-not-computed', 'en:nutriscore-missing-category', 'en:nutrition-not-enough-data-to-compute-nutrition-score', 'en:nutriscore-missing-nutrition-data', 'en:nutriscore-missing-nutrition-data-energy', 'en:nutriscore-missing-nutrition-data-fat', 'en:nutriscore-missing-nutrition-data-saturated-fat', 'en:nutriscore-missing-nutrition-data-sugars', 'en:nutriscore-missing-nutrition-data-sodium', 'en:nutriscore-missing-nutrition-data-proteins', 'en:nutrition-no-fiber', 'en:nutriscore-not-computed', 'en:nutrition-no-fruits-vegetables-nuts', 'en:nutrition-no-fiber-or-fruits-vegetables-nuts', 'en:packagings-not-complete', 'en:packagings-empty', 'en:ecoscore-extended-data-not-computed']`

## new_additives_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 3
- **Valeurs nulles**: 94,798 (100.00%)
- **Exemples de valeurs**:
  - `1`
  - `0`
  - `6`
  - `0`

## no_nutrition_data
- **Type**: `bool`
- **Valeurs uniques**: 2
- **Valeurs nulles**: 68,477 (72.23%)
- **Exemples de valeurs**:
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`

## nova_group
- **Type**: `NUMBER`
- **Valeurs uniques**: 4
- **Valeurs nulles**: 80,075 (84.47%)
- **Exemples de valeurs**:
  - `2`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`

## nova_groups_tags
- **Type**: `list`
- **Valeurs uniques**: 6
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `['en:2-processed-culinary-ingredients']`
  - `['en:4-ultra-processed-food-and-drink-products']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['unknown']`
  - `['en:4-ultra-processed-food-and-drink-products']`
  - `['en:4-ultra-processed-food-and-drink-products']`
  - `['unknown']`
  - `['unknown']`

## nova_groups
- **Type**: `STRING`
- **Valeurs uniques**: 4
- **Valeurs nulles**: 80,075 (84.47%)
- **Exemples de valeurs**:
  - `2`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`
  - `4`

## nucleotides_tags
- **Type**: `list`
- **Valeurs uniques**: 9
- **Valeurs nulles**: 71,384 (75.30%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## nutrient_levels_tags
- **Type**: `list`
- **Valeurs uniques**: 187
- **Valeurs nulles**: 252 (0.27%)
- **Exemples de valeurs**:
  - `['en:fat-in-low-quantity', 'en:sugars-in-high-quantity', 'en:salt-in-low-quantity']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:fat-in-moderate-quantity', 'en:saturated-fat-in-high-quantity', 'en:sugars-in-low-quantity', 'en:salt-in-moderate-quantity']`
  - `[]`
  - `[]`

## nutriments
- **Type**: `list`
- **Valeurs uniques**: 80,827
- **Valeurs nulles**: 10,091 (10.64%)
- **Exemples de valeurs**:
  - `[{'name': 'proteins', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 88.33000183105469, '100g': 88.33000183105469, 'serving': 53.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 333.0, '100g': 333.0, 'serving': 200.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 20.0, '100g': 0.019999999552965164, 'serving': 0.012000000104308128, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 88.33000183105469, '100g': 88.33000183105469, 'serving': 53.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nova-group', 'value': None, '100g': 2.0, 'serving': 2.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 333.0, '100g': 1393.0, 'serving': 836.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 8.0, '100g': 0.00800000037997961, 'serving': 0.004800000227987766, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nutrition-score-fr', 'value': None, '100g': 19.0, 'serving': None, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'nova-group', 'value': None, '100g': 4.0, 'serving': 4.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'fat', 'value': 2.5, '100g': 1.0399999618530273, 'serving': 2.5, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 15.0, '100g': 6.25, 'serving': 15.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 10.0, '100g': 4.170000076293945, 'serving': 10.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'trans-fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 325.0, '100g': 0.13500000536441803, 'serving': 0.32499998807907104, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 1.5, '100g': 0.625, 'serving': 1.5, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 130.0, '100g': 227.0, 'serving': 544.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 130.0, '100g': 0.05420000106096268, 'serving': 0.12999999523162842, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 16.0, '100g': 6.670000076293945, 'serving': 16.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 130.0, '100g': 54.20000076293945, 'serving': 130.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'sugars', 'value': 7.0, '100g': 7.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 6.0, '100g': 6.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 7.0, '100g': 7.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 380.0, '100g': 380.0, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 77.0, '100g': 77.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 1.2999999523162842, '100g': 1.2999999523162842, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 8.0, '100g': 8.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 1.0, '100g': 1.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 0.5199999809265137, '100g': 0.5199999809265137, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 380.0, '100g': 1590.0, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'carbohydrates', 'value': 50.0, '100g': 50.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 416.6666564941406, '100g': 1743.0, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 33.33333206176758, '100g': 33.33333206176758, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 2.6666667461395264, '100g': 2.6666667461395264, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 16.66666603088379, '100g': 16.66666603088379, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 416.6666564941406, '100g': 416.6666564941406, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 0.0, '100g': 0.0, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 33.33333206176758, '100g': 33.33333206176758, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 6.666666507720947, '100g': 6.666666507720947, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'carbohydrates', 'value': 2.0, '100g': 2.0, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 1.5, '100g': 1.5, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 30.0, '100g': 30.0, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 1.0, '100g': 1.0, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 1.7999999523162842, '100g': 1.7999999523162842, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 1.0, '100g': 1.0, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 0.0, '100g': 0.0, 'serving': None, 'unit': '', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 30.0, '100g': 126.0, 'serving': None, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 0.7200000286102295, '100g': 0.7200000286102295, 'serving': None, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'iron', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 3.569999933242798, '100g': 3.569999933242798, 'serving': 1.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-a', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'IU', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 3.200000047683716, '100g': 3.200000047683716, 'serving': 0.8960000276565552, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-c', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'cholesterol', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 1.100000023841858, '100g': 1.100000023841858, 'serving': 0.30799999833106995, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'calcium', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'trans-fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 0.4399999976158142, '100g': 0.4399999976158142, 'serving': 0.12300000339746475, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nova-group', 'value': None, '100g': 4.0, 'serving': 4.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'sodium', 'value': 904.239990234375, '100g': 0.47099998593330383, 'serving': 0.9042400121688843, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'calcium', 'value': 15.0, '100g': 0.07810000330209732, 'serving': 0.15000000596046448, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 2.0, '100g': 1.0399999618530273, 'serving': 2.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'trans-fat', 'value': 0.20000000298023224, '100g': 0.10400000214576721, 'serving': 0.20000000298023224, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 16.0, '100g': 8.329999923706055, 'serving': 16.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'cholesterol', 'value': 241.0, '100g': 0.12600000202655792, 'serving': 0.2409999966621399, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 11.0, '100g': 5.730000019073486, 'serving': 11.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 1.0, '100g': 0.5210000276565552, 'serving': 1.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 510.0, '100g': 1110.0, 'serving': 2134.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'iron', 'value': 30.0, '100g': 0.0028099999763071537, 'serving': 0.005400000140070915, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 32.0, '100g': 16.700000762939453, 'serving': 32.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 32.0, '100g': 16.700000762939453, 'serving': 32.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 510.0, '100g': 266.0, 'serving': 510.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nova-group', 'value': None, '100g': 4.0, 'serving': 4.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 2260.60009765625, '100g': 1.1799999475479126, 'serving': 2.2606000900268555, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nutrition-score-fr', 'value': None, '100g': 13.0, 'serving': None, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 2.6661943763883755e-09, 'serving': 2.6661943763883755e-09, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-a', 'value': 20.0, '100g': 0.000155999994603917, 'serving': 0.0003000000142492354, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-c', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'sodium', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 120.0, '100g': 120.0, 'serving': 36.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 32.0, '100g': 32.0, 'serving': 9.600000381469727, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 120.0, '100g': 502.0, 'serving': 151.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 32.0, '100g': 32.0, 'serving': 9.600000381469727, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'saturated-fat', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nutrition-score-fr', 'value': None, '100g': 10.0, 'serving': None, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`
  - `[{'name': 'saturated-fat', 'value': 4.5, '100g': 4.5, 'serving': 4.5, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fiber', 'value': 2.0, '100g': 2.0, 'serving': 2.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy', 'value': 360.0, '100g': 1510.0, 'serving': 1506.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'cholesterol', 'value': 50.0, '100g': 0.05000000074505806, 'serving': 0.05000000074505806, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sodium', 'value': 355.6000061035156, '100g': 0.35600000619888306, 'serving': 0.3555999994277954, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'calcium', 'value': 6.0, '100g': 0.05999999865889549, 'serving': 0.05999999865889549, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'sugars', 'value': 27.0, '100g': 27.0, 'serving': 27.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'trans-fat', 'value': 0.20000000298023224, '100g': 0.20000000298023224, 'serving': 0.20000000298023224, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'proteins', 'value': 5.0, '100g': 5.0, 'serving': 5.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'energy-kcal', 'value': 360.0, '100g': 360.0, 'serving': 360.0, 'unit': 'kcal', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nova-group', 'value': None, '100g': 4.0, 'serving': 4.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'carbohydrates', 'value': 45.0, '100g': 45.0, 'serving': 45.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'iron', 'value': 30.0, '100g': 0.005400000140070915, 'serving': 0.005400000140070915, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fat', 'value': 18.0, '100g': 18.0, 'serving': 18.0, 'unit': 'g', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'salt', 'value': 889.0, '100g': 0.8889999985694885, 'serving': 0.8889999985694885, 'unit': 'mg', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-nuts-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'fruits-vegetables-legumes-estimate-from-ingredients', 'value': None, '100g': 0.0, 'serving': 0.0, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'nutrition-score-fr', 'value': None, '100g': 19.0, 'serving': None, 'unit': None, 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-a', 'value': 2.0, '100g': 2.9999999242136255e-05, 'serving': 2.9999999242136255e-05, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}, {'name': 'vitamin-c', 'value': 0.0, '100g': 0.0, 'serving': 0.0, 'unit': '% DV', 'prepared_value': None, 'prepared_100g': None, 'prepared_serving': None, 'prepared_unit': None}]`

## nutriscore_grade
- **Type**: `STRING`
- **Valeurs uniques**: 7
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `e`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `unknown`
  - `d`
  - `unknown`
  - `unknown`

## nutriscore_score
- **Type**: `NUMBER`
- **Valeurs uniques**: 61
- **Valeurs nulles**: 78,448 (82.75%)
- **Exemples de valeurs**:
  - `19`
  - `13`
  - `10`
  - `19`
  - `18`
  - `17`
  - `14`
  - `16`
  - `16`
  - `6`

## nutrition_data_per
- **Type**: `STRING`
- **Valeurs uniques**: 3
- **Valeurs nulles**: 579 (0.61%)
- **Exemples de valeurs**:
  - `100g`
  - `100g`
  - `serving`
  - `100g`
  - `100g`
  - `100g`
  - `100g`
  - `serving`
  - `100g`
  - `100g`

## obsolete
- **Type**: `bool`
- **Valeurs uniques**: 1
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`
  - `False`

## origins_tags
- **Type**: `list`
- **Valeurs uniques**: 574
- **Valeurs nulles**: 83,594 (88.18%)
- **Exemples de valeurs**:
  - `[]`
  - `['en:china']`
  - `[]`
  - `[]`
  - `['en:canada', 'fr:ancaster', 'fr:ontario']`
  - `[]`
  - `[]`
  - `['en:united-states']`
  - `[]`
  - `[]`

## origins
- **Type**: `STRING`
- **Valeurs uniques**: 679
- **Valeurs nulles**: 83,594 (88.18%)
- **Exemples de valeurs**:
  - ``
  - `Chine`
  - ``
  - ``
  - `Ancaster,Ontario,canada`
  - ``
  - ``
  - `United States`
  - ``
  - ``

## owner_fields
- **Type**: `list`
- **Valeurs uniques**: 122
- **Valeurs nulles**: 94,680 (99.87%)
- **Exemples de valeurs**:
  - `[{'field_name': 'countries', 'timestamp': 1736827489}, {'field_name': 'sugars', 'timestamp': 1736827489}, {'field_name': 'generic_name_fr', 'timestamp': 1736827489}, {'field_name': 'no_nutrition_data', 'timestamp': 1736827489}, {'field_name': 'owner', 'timestamp': 1736827489}, {'field_name': 'product_name_fr', 'timestamp': 1736827489}, {'field_name': 'brands', 'timestamp': 1736827489}, {'field_name': 'fat', 'timestamp': 1736827489}, {'field_name': 'energy-kcal', 'timestamp': 1736827489}, {'field_name': 'customer_service_fr', 'timestamp': 1736827489}, {'field_name': 'serving_size', 'timestamp': 1736827489}, {'field_name': 'packaging', 'timestamp': 1736827489}, {'field_name': 'quantity', 'timestamp': 1736827489}, {'field_name': 'carbohydrates', 'timestamp': 1736827489}, {'field_name': 'data_sources', 'timestamp': 1736827489}, {'field_name': 'allergens', 'timestamp': 1736827489}, {'field_name': 'salt', 'timestamp': 1736827489}, {'field_name': 'energy-kj', 'timestamp': 1736827489}, {'field_name': 'sodium', 'timestamp': 1736827489}, {'field_name': 'lang', 'timestamp': 1736827489}, {'field_name': 'lc', 'timestamp': 1736827489}, {'field_name': 'energy', 'timestamp': 1611293436}, {'field_name': 'ingredients_text_fr', 'timestamp': 1736827489}, {'field_name': 'proteins', 'timestamp': 1736827489}, {'field_name': 'obsolete', 'timestamp': 1736827489}, {'field_name': 'nutrition_data_per', 'timestamp': 1736827489}, {'field_name': 'producer_version_id', 'timestamp': 1736827489}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1736827489}, {'field_name': 'saturated-fat', 'timestamp': 1736827489}]`
  - `[{'field_name': 'preparation_fr', 'timestamp': 1637904657}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1637904657}, {'field_name': 'fiber', 'timestamp': 1637904657}, {'field_name': 'origin_fr', 'timestamp': 1637904657}, {'field_name': 'obsolete', 'timestamp': 1637904657}, {'field_name': 'fat', 'timestamp': 1637904657}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1637904657}, {'field_name': 'sugars', 'timestamp': 1637904657}, {'field_name': 'abbreviated_product_name', 'timestamp': 1618461047}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1637904657}, {'field_name': 'product_name_fr', 'timestamp': 1637904657}, {'field_name': 'owner', 'timestamp': 1637904657}, {'field_name': 'brands', 'timestamp': 1637904657}, {'field_name': 'producer_version_id', 'timestamp': 1637904657}, {'field_name': 'saturated-fat', 'timestamp': 1637904657}, {'field_name': 'salt', 'timestamp': 1637904657}, {'field_name': 'proteins', 'timestamp': 1637904657}, {'field_name': 'data_sources', 'timestamp': 1637904657}, {'field_name': 'countries', 'timestamp': 1637904657}, {'field_name': 'energy', 'timestamp': 1615440646}, {'field_name': 'serving_size', 'timestamp': 1637904657}, {'field_name': 'lang', 'timestamp': 1637904657}, {'field_name': 'ingredients_text_fr', 'timestamp': 1637904657}, {'field_name': 'generic_name_fr', 'timestamp': 1637904657}, {'field_name': 'customer_service_fr', 'timestamp': 1637904657}, {'field_name': 'nutriscore_grade_producer', 'timestamp': 1622176251}, {'field_name': 'carbohydrates', 'timestamp': 1637904657}, {'field_name': 'energy-kcal', 'timestamp': 1637904657}, {'field_name': 'energy-kj', 'timestamp': 1637904657}, {'field_name': 'lc', 'timestamp': 1637904657}, {'field_name': 'packaging', 'timestamp': 1637904657}, {'field_name': 'nutrition_data_per', 'timestamp': 1637904657}, {'field_name': 'quantity', 'timestamp': 1637904657}]`
  - `[{'field_name': 'energy', 'timestamp': 1615440646}, {'field_name': 'data_sources', 'timestamp': 1637904657}, {'field_name': 'preparation_fr', 'timestamp': 1637904657}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1637904657}, {'field_name': 'fat', 'timestamp': 1637904657}, {'field_name': 'producer_version_id', 'timestamp': 1637904657}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1637904657}, {'field_name': 'packaging', 'timestamp': 1637904657}, {'field_name': 'generic_name_fr', 'timestamp': 1637904657}, {'field_name': 'product_name_fr', 'timestamp': 1637904657}, {'field_name': 'ingredients_text_fr', 'timestamp': 1637904657}, {'field_name': 'customer_service_fr', 'timestamp': 1637904657}, {'field_name': 'serving_size', 'timestamp': 1637904657}, {'field_name': 'carbohydrates', 'timestamp': 1637904657}, {'field_name': 'countries', 'timestamp': 1637904657}, {'field_name': 'abbreviated_product_name', 'timestamp': 1618461047}, {'field_name': 'sugars', 'timestamp': 1637904657}, {'field_name': 'energy-kj', 'timestamp': 1637904657}, {'field_name': 'nutrition_data_per', 'timestamp': 1637904657}, {'field_name': 'quantity', 'timestamp': 1637904657}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1637904657}, {'field_name': 'lang', 'timestamp': 1637904657}, {'field_name': 'obsolete', 'timestamp': 1637904657}, {'field_name': 'energy-kcal', 'timestamp': 1637904657}, {'field_name': 'categories', 'timestamp': 1622521851}, {'field_name': 'proteins', 'timestamp': 1637904657}, {'field_name': 'fiber', 'timestamp': 1637904657}, {'field_name': 'lc', 'timestamp': 1637904657}, {'field_name': 'nutriscore_grade_producer', 'timestamp': 1622521851}, {'field_name': 'brands', 'timestamp': 1637904657}, {'field_name': 'saturated-fat', 'timestamp': 1637904657}, {'field_name': 'salt', 'timestamp': 1637904657}, {'field_name': 'owner', 'timestamp': 1637904657}]`
  - `[{'field_name': 'fiber', 'timestamp': 1621263224}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1621263224}, {'field_name': 'sugars', 'timestamp': 1621263224}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1621263224}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1621263224}, {'field_name': 'abbreviated_product_name', 'timestamp': 1616682972}, {'field_name': 'obsolete', 'timestamp': 1621263224}, {'field_name': 'fat', 'timestamp': 1621263224}, {'field_name': 'brands', 'timestamp': 1621263224}, {'field_name': 'product_name_fr', 'timestamp': 1621263224}, {'field_name': 'salt', 'timestamp': 1621263224}, {'field_name': 'proteins', 'timestamp': 1621263224}, {'field_name': 'saturated-fat', 'timestamp': 1621263224}, {'field_name': 'energy', 'timestamp': 1616682972}, {'field_name': 'serving_size', 'timestamp': 1621263224}, {'field_name': 'allergens', 'timestamp': 1621263224}, {'field_name': 'data_sources', 'timestamp': 1621263224}, {'field_name': 'countries', 'timestamp': 1621263224}, {'field_name': 'vitamin-a', 'timestamp': 1621263224}, {'field_name': 'ingredients_text_fr', 'timestamp': 1621263224}, {'field_name': 'lang', 'timestamp': 1621263224}, {'field_name': 'generic_name_fr', 'timestamp': 1621263224}, {'field_name': 'carbohydrates', 'timestamp': 1621263224}, {'field_name': 'energy-kcal', 'timestamp': 1621263224}, {'field_name': 'customer_service_fr', 'timestamp': 1621263224}, {'field_name': 'lc', 'timestamp': 1621263224}, {'field_name': 'nutrition_data_per', 'timestamp': 1621263224}, {'field_name': 'quantity', 'timestamp': 1621263224}, {'field_name': 'traces', 'timestamp': 1621263224}, {'field_name': 'energy-kj', 'timestamp': 1621263224}]`
  - `[{'field_name': 'countries', 'timestamp': 1611293455}, {'field_name': 'data_sources', 'timestamp': 1611293455}, {'field_name': 'labels', 'timestamp': 1611293455}, {'field_name': 'energy', 'timestamp': 1611293455}, {'field_name': 'ingredients_text_fr', 'timestamp': 1611293455}, {'field_name': 'lang', 'timestamp': 1611293455}, {'field_name': 'generic_name_fr', 'timestamp': 1611293455}, {'field_name': 'customer_service_fr', 'timestamp': 1611293455}, {'field_name': 'no_nutrition_data', 'timestamp': 1611293455}, {'field_name': 'energy-kcal', 'timestamp': 1611293455}, {'field_name': 'carbohydrates', 'timestamp': 1611293455}, {'field_name': 'energy-kj', 'timestamp': 1611293455}, {'field_name': 'quantity', 'timestamp': 1611293455}, {'field_name': 'nutrition_data_per', 'timestamp': 1611293455}, {'field_name': 'packaging', 'timestamp': 1611293455}, {'field_name': 'lc', 'timestamp': 1611293455}, {'field_name': 'preparation_fr', 'timestamp': 1611293455}, {'field_name': 'fat', 'timestamp': 1611293455}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1611293455}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1611293455}, {'field_name': 'sugars', 'timestamp': 1611293455}, {'field_name': 'product_name_fr', 'timestamp': 1611293455}, {'field_name': 'producer_version_id', 'timestamp': 1611293455}, {'field_name': 'brands', 'timestamp': 1611293455}, {'field_name': 'saturated-fat', 'timestamp': 1611293455}, {'field_name': 'proteins', 'timestamp': 1611293455}, {'field_name': 'salt', 'timestamp': 1611293455}]`
  - `[{'field_name': 'countries', 'timestamp': 1611293455}, {'field_name': 'lc', 'timestamp': 1611293455}, {'field_name': 'no_nutrition_data', 'timestamp': 1611293455}, {'field_name': 'labels', 'timestamp': 1611293455}, {'field_name': 'product_name_fr', 'timestamp': 1611293455}, {'field_name': 'customer_service_fr', 'timestamp': 1611293455}, {'field_name': 'energy', 'timestamp': 1611293455}, {'field_name': 'lang', 'timestamp': 1611293455}, {'field_name': 'nutrition_data_per', 'timestamp': 1611293455}, {'field_name': 'ingredients_text_fr', 'timestamp': 1611293455}, {'field_name': 'fat', 'timestamp': 1611293455}, {'field_name': 'producer_version_id', 'timestamp': 1611293455}, {'field_name': 'sugars', 'timestamp': 1611293455}, {'field_name': 'salt', 'timestamp': 1611293455}, {'field_name': 'brands', 'timestamp': 1611293455}, {'field_name': 'generic_name_fr', 'timestamp': 1611293455}, {'field_name': 'preparation_fr', 'timestamp': 1611293455}, {'field_name': 'energy-kj', 'timestamp': 1611293455}, {'field_name': 'carbohydrates', 'timestamp': 1611293455}, {'field_name': 'quantity', 'timestamp': 1611293455}, {'field_name': 'packaging', 'timestamp': 1611293455}, {'field_name': 'energy-kcal', 'timestamp': 1611293455}, {'field_name': 'saturated-fat', 'timestamp': 1611293455}, {'field_name': 'data_sources', 'timestamp': 1611293455}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1611293455}, {'field_name': 'proteins', 'timestamp': 1611293455}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1611293455}]`
  - `[{'field_name': 'nutriscore_grade_producer', 'timestamp': 1695309270}, {'field_name': 'monounsaturated-fat', 'timestamp': 1620983150}, {'field_name': 'fiber', 'timestamp': 1695309270}, {'field_name': 'serving_size', 'timestamp': 1695309270}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1695309270}, {'field_name': 'sugars', 'timestamp': 1695309270}, {'field_name': 'energy-kj', 'timestamp': 1695309270}, {'field_name': 'ingredients_text_fr', 'timestamp': 1695309270}, {'field_name': 'nutrition_data_per', 'timestamp': 1695309270}, {'field_name': 'quantity', 'timestamp': 1695309270}, {'field_name': 'energy-kcal', 'timestamp': 1695309270}, {'field_name': 'preparation_fr', 'timestamp': 1695309270}, {'field_name': 'data_sources', 'timestamp': 1695309270}, {'field_name': 'fat', 'timestamp': 1695309270}, {'field_name': 'saturated-fat', 'timestamp': 1695309270}, {'field_name': 'generic_name_fr', 'timestamp': 1695309270}, {'field_name': 'brands', 'timestamp': 1695309270}, {'field_name': 'polyunsaturated-fat', 'timestamp': 1620983150}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1695309270}, {'field_name': 'carbohydrates', 'timestamp': 1695309270}, {'field_name': 'producer_version_id', 'timestamp': 1695309270}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1695309270}, {'field_name': 'product_name_fr', 'timestamp': 1695309270}, {'field_name': 'lang', 'timestamp': 1695309270}, {'field_name': 'proteins', 'timestamp': 1695309270}, {'field_name': 'salt', 'timestamp': 1695309270}, {'field_name': 'labels', 'timestamp': 1695309270}, {'field_name': 'lc', 'timestamp': 1695309270}, {'field_name': 'customer_service_fr', 'timestamp': 1695309270}, {'field_name': 'categories', 'timestamp': 1695309270}, {'field_name': 'obsolete', 'timestamp': 1695309270}, {'field_name': 'allergens', 'timestamp': 1695309270}, {'field_name': 'packaging', 'timestamp': 1695309270}, {'field_name': 'countries', 'timestamp': 1695309270}]`
  - `[{'field_name': 'countries', 'timestamp': 1641989215}, {'field_name': 'nutrition_data_per', 'timestamp': 1641989215}, {'field_name': 'fat', 'timestamp': 1641989215}, {'field_name': 'product_name_fr', 'timestamp': 1641989215}, {'field_name': 'proteins', 'timestamp': 1641989215}, {'field_name': 'generic_name_fr', 'timestamp': 1641989215}, {'field_name': 'labels', 'timestamp': 1641989215}, {'field_name': 'data_sources', 'timestamp': 1641989215}, {'field_name': 'saturated-fat', 'timestamp': 1641989215}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1641989215}, {'field_name': 'fiber', 'timestamp': 1641989215}, {'field_name': 'quantity', 'timestamp': 1641989215}, {'field_name': 'lang', 'timestamp': 1641989215}, {'field_name': 'lc', 'timestamp': 1641989215}, {'field_name': 'serving_size', 'timestamp': 1641989215}, {'field_name': 'preparation_fr', 'timestamp': 1641989215}, {'field_name': 'customer_service_fr', 'timestamp': 1641989215}, {'field_name': 'producer_version_id', 'timestamp': 1641989215}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1641989215}, {'field_name': 'salt', 'timestamp': 1641989215}, {'field_name': 'brands', 'timestamp': 1641989215}, {'field_name': 'ingredients_text_fr', 'timestamp': 1641989215}, {'field_name': 'sugars', 'timestamp': 1641989215}, {'field_name': 'energy-kcal', 'timestamp': 1641989215}, {'field_name': 'energy-kj', 'timestamp': 1641989215}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1641989215}, {'field_name': 'categories', 'timestamp': 1641989215}, {'field_name': 'nutriscore_grade_producer', 'timestamp': 1641989215}, {'field_name': 'packaging', 'timestamp': 1641989215}, {'field_name': 'obsolete', 'timestamp': 1641989215}, {'field_name': 'carbohydrates', 'timestamp': 1641989215}]`
  - `[{'field_name': 'sugars', 'timestamp': 1641989215}, {'field_name': 'ingredients_text_fr', 'timestamp': 1641989215}, {'field_name': 'brands', 'timestamp': 1641989215}, {'field_name': 'carbohydrates', 'timestamp': 1641989215}, {'field_name': 'obsolete', 'timestamp': 1641989215}, {'field_name': 'nutriscore_grade_producer', 'timestamp': 1641989215}, {'field_name': 'packaging', 'timestamp': 1641989215}, {'field_name': 'categories', 'timestamp': 1641989215}, {'field_name': 'abbreviated_product_name_fr', 'timestamp': 1641989215}, {'field_name': 'energy-kj', 'timestamp': 1641989215}, {'field_name': 'energy-kcal', 'timestamp': 1641989215}, {'field_name': 'preparation_fr', 'timestamp': 1641989215}, {'field_name': 'serving_size', 'timestamp': 1641989215}, {'field_name': 'quantity', 'timestamp': 1641989215}, {'field_name': 'lc', 'timestamp': 1641989215}, {'field_name': 'lang', 'timestamp': 1641989215}, {'field_name': 'salt', 'timestamp': 1641989215}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1641989215}, {'field_name': 'producer_version_id', 'timestamp': 1641989215}, {'field_name': 'customer_service_fr', 'timestamp': 1641989215}, {'field_name': 'labels', 'timestamp': 1641989215}, {'field_name': 'generic_name_fr', 'timestamp': 1641989215}, {'field_name': 'proteins', 'timestamp': 1641989215}, {'field_name': 'fiber', 'timestamp': 1641989215}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1641989215}, {'field_name': 'saturated-fat', 'timestamp': 1641989215}, {'field_name': 'data_sources', 'timestamp': 1641989215}, {'field_name': 'countries', 'timestamp': 1641989215}, {'field_name': 'fat', 'timestamp': 1641989215}, {'field_name': 'product_name_fr', 'timestamp': 1641989215}, {'field_name': 'nutrition_data_per', 'timestamp': 1641989215}]`
  - `[{'field_name': 'owner', 'timestamp': 1703079806}, {'field_name': 'lc', 'timestamp': 1703079806}, {'field_name': 'saturated-fat', 'timestamp': 1703079806}, {'field_name': 'customer_service_es', 'timestamp': 1703079806}, {'field_name': 'carbohydrates', 'timestamp': 1703079806}, {'field_name': 'product_name_es', 'timestamp': 1703079806}, {'field_name': 'proteins', 'timestamp': 1703079806}, {'field_name': 'energy-kcal', 'timestamp': 1703079806}, {'field_name': 'ingredients_text_fr', 'timestamp': 1703079806}, {'field_name': 'countries', 'timestamp': 1703079806}, {'field_name': 'generic_name_es', 'timestamp': 1703079806}, {'field_name': 'obsolete', 'timestamp': 1703079806}, {'field_name': 'producer_es', 'timestamp': 1703079806}, {'field_name': 'fiber', 'timestamp': 1703079806}, {'field_name': 'energy-kj', 'timestamp': 1703079806}, {'field_name': 'stores', 'timestamp': 1703079806}, {'field_name': 'data_sources', 'timestamp': 1703079806}, {'field_name': 'producer_product_id', 'timestamp': 1703079806}, {'field_name': 'customer_service_nl', 'timestamp': 1703079806}, {'field_name': 'conservation_conditions_nl', 'timestamp': 1703079806}, {'field_name': 'producer_it', 'timestamp': 1703079806}, {'field_name': 'allergens', 'timestamp': 1703079806}, {'field_name': 'ingredients_text_it', 'timestamp': 1703079806}, {'field_name': 'conservation_conditions_fr', 'timestamp': 1703079806}, {'field_name': 'product_name_fr', 'timestamp': 1703079806}, {'field_name': 'ingredients_text_nl', 'timestamp': 1703079806}, {'field_name': 'producer_fr', 'timestamp': 1703079806}, {'field_name': 'customer_service_it', 'timestamp': 1703079806}, {'field_name': 'nutrition_data_prepared_per', 'timestamp': 1703079806}, {'field_name': 'conservation_conditions_es', 'timestamp': 1703079806}, {'field_name': 'brands', 'timestamp': 1703079806}, {'field_name': 'generic_name_it', 'timestamp': 1703079806}, {'field_name': 'generic_name_nl', 'timestamp': 1703079806}, {'field_name': 'customer_service_fr', 'timestamp': 1703079806}, {'field_name': 'categories', 'timestamp': 1703079806}, {'field_name': 'nutrition_data_per', 'timestamp': 1703079806}, {'field_name': 'salt', 'timestamp': 1703079806}, {'field_name': 'lang', 'timestamp': 1703079806}, {'field_name': 'producer_nl', 'timestamp': 1703079806}, {'field_name': 'quantity', 'timestamp': 1703079806}, {'field_name': 'product_name_it', 'timestamp': 1703079806}, {'field_name': 'product_name_nl', 'timestamp': 1703079806}, {'field_name': 'conservation_conditions_it', 'timestamp': 1703079806}, {'field_name': 'sugars', 'timestamp': 1703079806}, {'field_name': 'generic_name_fr', 'timestamp': 1703079806}, {'field_name': 'fat', 'timestamp': 1703079806}, {'field_name': 'ingredients_text_es', 'timestamp': 1703079806}]`

## owner
- **Type**: `STRING`
- **Valeurs uniques**: 25
- **Valeurs nulles**: 94,678 (99.87%)
- **Exemples de valeurs**:
  - `org-ferrero-france-commerciale`
  - `org-panzani-sa`
  - `org-panzani-sa`
  - `org-bonduelle`
  - `org-cristalco`
  - `org-cristalco`
  - `org-pepsico-france`
  - `org-pepsico-france`
  - `org-pepsico-france`
  - `org-carrefour`

## packagings_complete
- **Type**: `bool`
- **Valeurs uniques**: 2
- **Valeurs nulles**: 88,292 (93.13%)
- **Exemples de valeurs**:
  - `False`
  - `False`
  - `True`
  - `False`
  - `False`
  - `True`
  - `False`
  - `False`
  - `False`
  - `False`

## packaging_recycling_tags
- **Type**: `list`
- **Valeurs uniques**: 464
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## packaging_shapes_tags
- **Type**: `list`
- **Valeurs uniques**: 611
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:packaging']`
  - `[]`
  - `[]`

## packaging_tags
- **Type**: `list`
- **Valeurs uniques**: 1,097
- **Valeurs nulles**: 85,887 (90.60%)
- **Exemples de valeurs**:
  - `[]`
  - `['en:fresh', 'fr:emballage-papier']`
  - `['en:box']`
  - `[]`
  - `[]`
  - `[]`
  - `['en:plastic', 'en:box', 'en:cardboard']`
  - `[]`
  - `['fr:conserve-acier']`
  - `['en:1-aluminium-can-to-recycle']`

## packaging_text
- **Type**: `list`
- **Valeurs uniques**: 243
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## packaging
- **Type**: `STRING`
- **Valeurs uniques**: 1,370
- **Valeurs nulles**: 85,890 (90.60%)
- **Exemples de valeurs**:
  - ``
  - `Frais, Emballage papier`
  - `Boîte`
  - ``
  - ``
  - ``
  - `Plastic, Box, Cardboard`
  - ``
  - `Conserve acier`
  - `1 aluminium can to recycle`

## packagings
- **Type**: `list`
- **Valeurs uniques**: 1,450
- **Valeurs nulles**: 253 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[{'material': 'en:paper', 'number_of_units': None, 'quantity_per_unit': None, 'quantity_per_unit_unit': None, 'quantity_per_unit_value': None, 'recycling': None, 'shape': 'en:packaging', 'weight_measured': None}]`
  - `[]`
  - `[]`

## photographers
- **Type**: `list`
- **Valeurs uniques**: 11
- **Valeurs nulles**: 94,766 (99.96%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `['andre']`
  - `[]`
  - `['julia-t']`
  - `[]`
  - `['manu1400']`
  - `[]`
  - `['andre']`

## popularity_key
- **Type**: `NUMBER`
- **Valeurs uniques**: 166
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `0`
  - `1`
  - `0`
  - `1`
  - `1`
  - `1`
  - `0`
  - `1`
  - `0`
  - `0`

## popularity_tags
- **Type**: `list`
- **Valeurs uniques**: 3,307
- **Valeurs nulles**: 79,642 (84.01%)
- **Exemples de valeurs**:
  - `['bottom-25-percent-scans-2021', 'bottom-20-percent-scans-2021', 'top-85-percent-scans-2021', 'top-90-percent-scans-2021', 'top-10000-us-scans-2021', 'top-50000-us-scans-2021', 'top-100000-us-scans-2021', 'top-country-us-scans-2021']`
  - `['bottom-25-percent-scans-2019', 'bottom-20-percent-scans-2019', 'top-85-percent-scans-2019', 'top-90-percent-scans-2019', 'top-5000-mx-scans-2019', 'top-10000-mx-scans-2019', 'top-50000-mx-scans-2019', 'top-100000-mx-scans-2019', 'top-country-mx-scans-2019', 'top-75-percent-scans-2023', 'top-80-percent-scans-2023', 'top-85-percent-scans-2023', 'top-90-percent-scans-2023', 'top-country-fr-scans-2023']`
  - `['bottom-25-percent-scans-2021', 'bottom-20-percent-scans-2021', 'top-85-percent-scans-2021', 'top-90-percent-scans-2021', 'top-500-hk-scans-2021', 'top-1000-hk-scans-2021', 'top-5000-hk-scans-2021', 'top-10000-hk-scans-2021', 'top-50000-hk-scans-2021', 'top-100000-hk-scans-2021', 'top-country-hk-scans-2021']`
  - `['top-75-percent-scans-2023', 'top-80-percent-scans-2023', 'top-85-percent-scans-2023', 'top-90-percent-scans-2023', 'top-country-fr-scans-2023']`
  - `['top-country-fr-scans-2019', 'bottom-25-percent-scans-2020', 'bottom-20-percent-scans-2020', 'top-85-percent-scans-2020', 'top-90-percent-scans-2020', 'top-5000-ma-scans-2020', 'top-10000-ma-scans-2020', 'top-50000-ma-scans-2020', 'top-100000-ma-scans-2020', 'top-country-ma-scans-2020', 'bottom-25-percent-scans-2021', 'bottom-20-percent-scans-2021', 'top-85-percent-scans-2021', 'top-90-percent-scans-2021', 'top-5000-ca-scans-2021', 'top-10000-ca-scans-2021', 'top-50000-ca-scans-2021', 'top-100000-ca-scans-2021', 'top-country-ca-scans-2021']`
  - `['top-75-percent-scans-2023', 'top-80-percent-scans-2023', 'top-85-percent-scans-2023', 'top-90-percent-scans-2023', 'top-10000-ca-scans-2023', 'top-50000-ca-scans-2023', 'top-100000-ca-scans-2023', 'top-country-ca-scans-2023']`
  - `['top-75-percent-scans-2023', 'top-80-percent-scans-2023', 'top-85-percent-scans-2023', 'top-90-percent-scans-2023', 'top-5000-ca-scans-2023', 'top-10000-ca-scans-2023', 'top-50000-ca-scans-2023', 'top-100000-ca-scans-2023', 'top-country-ca-scans-2023']`
  - `['top-country-es-scans-2019']`
  - `['top-country-us-scans-2019', 'top-75-percent-scans-2020', 'top-80-percent-scans-2020', 'top-85-percent-scans-2020', 'top-90-percent-scans-2020', 'top-500-ca-scans-2020', 'top-1000-ca-scans-2020', 'top-5000-ca-scans-2020', 'top-10000-ca-scans-2020', 'top-50000-ca-scans-2020', 'top-100000-ca-scans-2020', 'top-country-ca-scans-2020', 'top-75-percent-scans-2021', 'top-80-percent-scans-2021', 'top-85-percent-scans-2021', 'top-90-percent-scans-2021', 'top-5000-ca-scans-2021', 'top-10000-ca-scans-2021', 'top-50000-ca-scans-2021', 'top-100000-ca-scans-2021', 'top-country-ca-scans-2021', 'top-75-percent-scans-2023', 'top-80-percent-scans-2023', 'top-85-percent-scans-2023', 'top-90-percent-scans-2023', 'top-1000-ca-scans-2023', 'top-5000-ca-scans-2023', 'top-10000-ca-scans-2023', 'top-50000-ca-scans-2023', 'top-100000-ca-scans-2023', 'top-country-ca-scans-2023', 'top-10000-pt-scans-2023', 'top-50000-pt-scans-2023', 'top-100000-pt-scans-2023']`
  - `['bottom-25-percent-scans-2019', 'bottom-20-percent-scans-2019', 'top-85-percent-scans-2019', 'top-90-percent-scans-2019', 'top-5000-ca-scans-2019', 'top-10000-ca-scans-2019', 'top-50000-ca-scans-2019', 'top-100000-ca-scans-2019', 'top-country-ca-scans-2019', 'bottom-25-percent-scans-2020', 'bottom-20-percent-scans-2020', 'top-85-percent-scans-2020', 'top-90-percent-scans-2020', 'top-5000-ca-scans-2020', 'top-10000-ca-scans-2020', 'top-50000-ca-scans-2020', 'top-100000-ca-scans-2020', 'top-country-ca-scans-2020']`

## product_name
- **Type**: `list`
- **Valeurs uniques**: 76,656
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `[{'lang': 'main', 'text': 'Organic Vermont Maple Syrup Grade A Dark Color Robust Taste'}, {'lang': 'en', 'text': 'Organic Vermont Maple Syrup Grade A Dark Color Robust Taste'}, {'lang': 'fr', 'text': '100 pure vermont organic maple syrup'}]`
  - `[{'lang': 'main', 'text': 'Imitation vanilla flavor'}, {'lang': 'en', 'text': 'Imitation vanilla flavor'}]`
  - `[{'lang': 'main', 'text': '1% low-fat milk'}, {'lang': 'en', 'text': '1% low-fat milk'}]`
  - `[{'lang': 'main', 'text': 'Fresh udon bowl'}, {'lang': 'fr', 'text': 'Fresh udon bowl'}]`
  - `[{'lang': 'main', 'text': 'Seto fumi furikake'}, {'lang': 'en', 'text': 'Seto fumi furikake'}]`
  - `[{'lang': 'main', 'text': 'Assaisonnement pour riz'}, {'lang': 'fr', 'text': 'Assaisonnement pour riz'}]`
  - `[{'lang': 'main', 'text': 'Sushi Ginger Gari'}, {'lang': 'en', 'text': 'Sushi Ginger Gari'}]`
  - `[{'lang': 'main', 'text': "Chef d'oeuf™avec fromage sur muffin anglais"}, {'lang': 'fr', 'text': "Chef d'oeuf™avec fromage sur muffin anglais"}]`
  - `[]`
  - `[]`

## product_quantity_unit
- **Type**: `STRING`
- **Valeurs uniques**: 2
- **Valeurs nulles**: 82,430 (86.95%)
- **Exemples de valeurs**:
  - `ml`
  - `g`
  - `ml`
  - `g`
  - `g`
  - `g`
  - `g`
  - `g`
  - `ml`
  - `ml`

## product_quantity
- **Type**: `STRING`
- **Valeurs uniques**: 1,587
- **Valeurs nulles**: 76,065 (80.24%)
- **Exemples de valeurs**:
  - `946.0`
  - `118`
  - `235`
  - `50`
  - `192.0`
  - `480.0`
  - `1000.0`
  - `3`
  - `0.0`
  - `28.0`

## purchase_places_tags
- **Type**: `list`
- **Valeurs uniques**: 338
- **Valeurs nulles**: 84,151 (88.77%)
- **Exemples de valeurs**:
  - `[]`
  - `['saint-jean-sur-richelieu']`
  - `['calgary', 'alberta', 'canada']`
  - `['candiac', 'quebec']`
  - `[]`
  - `[]`
  - `[]`
  - `['canada', 'etats-unis']`
  - `['plainville', 'connecticut', 'united-states']`
  - `['paris-xiii', 'paris', 'france', 'canberra', 'australia', 'montreal', 'canada']`

## quantity
- **Type**: `STRING`
- **Valeurs uniques**: 3,823
- **Valeurs nulles**: 73,448 (77.48%)
- **Exemples de valeurs**:
  - `946 ml`
  - `118 ml`
  - ``
  - `235 g`
  - `50`
  - `50g`
  - `192 g`
  - `480 mL`
  - `1 kg`
  - ``

## rev
- **Type**: `NUMBER`
- **Valeurs uniques**: 135
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `11`
  - `12`
  - `7`
  - `11`
  - `10`
  - `21`
  - `7`
  - `15`
  - `3`
  - `3`

## scans_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 74
- **Valeurs nulles**: 79,576 (83.94%)
- **Exemples de valeurs**:
  - `1`
  - `5`
  - `1`
  - `1`
  - `1`
  - `1`
  - `2`
  - `1`
  - `4`
  - `2`

## serving_quantity
- **Type**: `STRING`
- **Valeurs uniques**: 890
- **Valeurs nulles**: 73,622 (77.66%)
- **Exemples de valeurs**:
  - `60.0`
  - `240.0`
  - `28`
  - `192.0`
  - `30.0`
  - `100.0`
  - `30.0`
  - `28.0`
  - `28.0`
  - `42.0`

## serving_size
- **Type**: `STRING`
- **Valeurs uniques**: 6,920
- **Valeurs nulles**: 73,261 (77.28%)
- **Exemples de valeurs**:
  - `4 Tbsp (60 ml)`
  - `240ml`
  - `28 g (1 oz)`
  - `192 g / 1 sanwich`
  - `30 mL`
  - `100 g / 1/10 du gâteau`
  - `0.25 cup (30 g)`
  - `28 g`
  - `3/4 cup (28 g) (28 g)`
  - `2 bars (42 g)`

## states_tags
- **Type**: `list`
- **Valeurs uniques**: 1,195
- **Valeurs nulles**: 0 (0.00%)
- **Exemples de valeurs**:
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-to-be-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-to-be-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-to-be-completed', 'en:packaging-to-be-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-to-be-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-to-be-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-completed', 'en:categories-to-be-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-completed', 'en:packaging-to-be-completed', 'en:quantity-to-be-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-completed', 'en:ingredients-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-completed', 'en:brands-completed', 'en:packaging-completed', 'en:quantity-completed', 'en:product-name-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-selected', 'en:ingredients-photo-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-to-be-completed', 'en:ingredients-to-be-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-to-be-completed', 'en:packaging-to-be-completed', 'en:quantity-to-be-completed', 'en:product-name-to-be-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-selected', 'en:photos-uploaded']`
  - `['en:to-be-completed', 'en:nutrition-facts-to-be-completed', 'en:ingredients-to-be-completed', 'en:expiration-date-to-be-completed', 'en:packaging-code-to-be-completed', 'en:characteristics-to-be-completed', 'en:origins-to-be-completed', 'en:categories-to-be-completed', 'en:brands-to-be-completed', 'en:packaging-to-be-completed', 'en:quantity-to-be-completed', 'en:product-name-to-be-completed', 'en:photos-to-be-validated', 'en:packaging-photo-to-be-selected', 'en:nutrition-photo-to-be-selected', 'en:ingredients-photo-to-be-selected', 'en:front-photo-to-be-selected', 'en:photos-uploaded']`

## stores_tags
- **Type**: `list`
- **Valeurs uniques**: 881
- **Valeurs nulles**: 82,569 (87.10%)
- **Exemples de valeurs**:
  - `[]`
  - `['a-w']`
  - `['real-canadian-superstore']`
  - `['costco']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['big-y']`
  - `['tang-freres', 'costco', 'kim-phat']`

## stores
- **Type**: `STRING`
- **Valeurs uniques**: 978
- **Valeurs nulles**: 82,569 (87.10%)
- **Exemples de valeurs**:
  - ``
  - `A&W`
  - `Real Canadian Superstore`
  - `Costco`
  - ``
  - ``
  - ``
  - ``
  - `Big Y`
  - `Tang fréres,Costco,Kim Phat`

## traces_tags
- **Type**: `list`
- **Valeurs uniques**: 713
- **Valeurs nulles**: 252 (0.27%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['fr:contient-lait-autre-gluten-soya-oeuf', 'fr:dans-l-usine-de-fabrication', 'fr:graines-de-sesame-lait-ble-et-autre-gluten-soya-moutarde']`
  - `[]`
  - `[]`

## unique_scans_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 66
- **Valeurs nulles**: 79,576 (83.94%)
- **Exemples de valeurs**:
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `2`
  - `1`
  - `4`
  - `1`

## unknown_ingredients_n
- **Type**: `NUMBER`
- **Valeurs uniques**: 83
- **Valeurs nulles**: 78,646 (82.96%)
- **Exemples de valeurs**:
  - `0`
  - `2`
  - `0`
  - `2`
  - `12`
  - `1`
  - `7`
  - `3`
  - `1`
  - `3`

## unknown_nutrients_tags
- **Type**: `list`
- **Valeurs uniques**: 43
- **Valeurs nulles**: 842 (0.89%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `[]`

## vitamins_tags
- **Type**: `list`
- **Valeurs uniques**: 488
- **Valeurs nulles**: 71,384 (75.30%)
- **Exemples de valeurs**:
  - `[]`
  - `[]`
  - `['en:retinyl-palmitate', 'en:cholecalciferol']`
  - `[]`
  - `[]`
  - `[]`
  - `[]`
  - `['en:retinyl-palmitate', 'en:cholecalciferol']`
  - `[]`
  - `[]`

## with_non_nutritive_sweeteners
- **Type**: `NUMBER`
- **Valeurs uniques**: 1
- **Valeurs nulles**: 94,180 (99.34%)
- **Exemples de valeurs**:
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`

## with_sweeteners
- **Type**: `NUMBER`
- **Valeurs uniques**: 1
- **Valeurs nulles**: 94,572 (99.76%)
- **Exemples de valeurs**:
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`
  - `1`

