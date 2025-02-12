
================================================================================
## Column: product_name (Documentation added: 2025-02-09 15:35:31)

- Description: Multilingual product names stored as an array of language-text pairs, supporting multiple translations per product
- Data Type: STRUCT(lang VARCHAR, text VARCHAR)[]
- Structure: Array of structs containing language code ('lang') and product name ('text') pairs
- Purpose: Stores product names in multiple languages to support multilingual product information display
- Analysis: Commonly contains main language plus English/French translations, following Canadian bilingual labeling standards
- Web Research: Standard OFF field for product names, supports multilingual product identification across regions


================================================================================
## Column: product_name (Documentation added: 2025-02-10 07:34:52)

- Description: Multilingual product names stored as an array of structured data containing language codes and corresponding text values
- Data Type: STRUCT(lang VARCHAR, text VARCHAR)[]
- Structure: Array of structs with {'lang': language_code, 'text': product_name_in_that_language}
- Purpose: Stores product names in multiple languages to support multilingual product information display
- Analysis: Contains main language plus translations (primarily EN/FR), with consistent structure across entries
- Web Research: Standard Open Food Facts field for multilingual product naming following international standards

## product_name

- Description: Multilingual product names stored as array of structured entries with language identifier and product name text
- Data Type: STRUCT(lang VARCHAR, text VARCHAR)[]
- Structure: Array of {lang: language_code, text: product_name} where language_code includes 'main', 'en', 'fr'
- Purpose: Stores product names in multiple languages to support multilingual product display and search functionality
- Analysis: Contains primary names and translations, supports bilingual products (EN/FR), maintains original language names
- Web Research: Standard Open Food Facts field for multilingual product identification, essential for global product database

ici 


## product_name
- Description: Multilingual product names stored as structured arrays, primarily containing English and French translations for Canadian market compliance
- Data Type: STRUCT(lang VARCHAR, text VARCHAR)[]
- Structure: Array of structs containing language code ('lang') and product name ('text') pairs
- Purpose: Stores product names in multiple languages to support bilingual product labeling requirements
- Analysis: Contains product names in multiple languages, typically English and French, with consistent bilingual formatting
- Web Research: Standard Open Food Facts field for storing multilingual product names, essential for Canadian market

Haiku


