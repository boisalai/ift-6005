
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

