# Conversational Agent for Open Food Facts Database

> [!NOTE]
> This directory will eventually contain technical documentation for the project. For now, it only contains draft notes and work in progress.

## Overview
This project is part of the IFT-6005 Integrative Project course at [Laval University](https://www.ulaval.ca/en). 
It aims to develop a conversational agent that enables natural language querying of the 
[Open Food Facts](https://world.openfoodfacts.org/) database, making nutritional information more accessible to the general public.

## Problem Statement
Traditional access to relational databases requires knowledge of structured query languages (e.g., SQL), which creates a barrier for users without technical expertise. This limitation is particularly significant in domains requiring broad public accessibility, such as nutritional information.

For example, platforms like Open Food Facts aggregate thousands of detailed product records (including composition, nutritional content, and certifications), but their interface typically relies on manual queries or predefined filters. For a consumer wanting to ask complex questions like "Which allergen-free snacks have a Nutri-score A?", the user experience remains cumbersome.

## Solution Approach
This project explores the use of Large Language Models (LLMs) to facilitate database access. LLMs can:
- Understand questions asked in natural language
- Convert these questions into appropriate database queries
- Present results in a user-friendly format

## Project Goal
The primary objective is to develop a conversational agent capable of:
- Understanding natural language questions about food products
- Querying the Open Food Facts database effectively
- Providing accurate and relevant nutritional information
- Making food product data more accessible to the general public

## Technical Documentation

The following files contain detailed documentation of the project's components:

- [`dataset.md`](dataset.md): Explains the process of preparing and filtering the Open Food Facts dataset for use in our system.
- `dictionary.md`: Documents how we automatically generate comprehensive database column documentation using Claude 3.5.
- `qa_pairs.md`: Describes the generation of 110 bilingual question-answer pairs used for evaluating the conversational agent.