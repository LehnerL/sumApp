# sumApp: fast text summarization tool

name: L. Lehner |
licenses: MIT |
multilinguality: monolingual |
task_categories: summarization |
task_ids: text2text-generation

## Model

https://huggingface.co/sshleifer/distilbart-cnn-12-6
This model is based on:
BartForConditionalGeneration.from_pretrained. See the BART docs for more information.
https://huggingface.co/transformers/model_doc/bart.html?#transformers.BartForConditionalGeneration

## Dataset

`cnn_dailymail`
The CNN / DailyMail Dataset is an English-language dataset containing just over 300k unique news articles as written by journalists at CNN and the Daily Mail. The current version supports both extractive and abstractive summarization, though the original version was created for machine reading and comprehension and abstractive question answering.
https://huggingface.co/datasets/cnn_dailymail

`xsum`
Extreme Summarization (XSum) Dataset.
There are three features:
document: Input news article.
summary: One sentence summary of the article.
id: BBC ID of the article.
https://huggingface.co/datasets/xsum

## Languages

[En] - English

## Data Fields

We stored each sample in a JSON file using the MongoDB database and structured it with the following attributes: name, summary, timer, and date. The timer contains the model's summarization time in milliseconds so we can collect and evaluate this data for future statistics, such as performance.

## Social Impact

We are excited about the future of applying text-based models on task such as processing and generation new text. We hope this project will encourage more NLP researchers to improve the way we understand and enjoy articles, since achieving literary comprehension is another step that progress us to the goal of robust AI.

## Other

Known Limitations:
This program works only with relevant input: links to article-based pages (HTML, PDF, Docx) or direct text (type, paste).

## Run

> cd C:\Users\[your_user_name]\Desktop\fin_pro\sumApp\sumApp\sum_env\Scripts
> streamlit run C:\Users\[your_user_name]\Desktop\fin_pro\sumApp\sumApp\sumApp.py [ARGUMENTS]

## Licensing Information

All source of code belongs to L. Lehner.

## Contributions

Thanks to @sshleifer for adding this model.
