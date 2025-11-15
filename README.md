# RECOMB Proceedings. 

- Web page design forked from [Just the Docs](https://github.com/just-the-docs/just-the-docs) and edited by: [Arda İçöz](https://github.com/ardaicoz)
- Data collection: [Emir Tomrukçu](https://github.com/emirtom), [Arda İçöz](https://github.com/ardaicoz), [Can Alkan](https://github.com/calkan), and [Gemini Deep Research](https://gemini.google/overview/deep-research/).

## Generating Markdown files

The tsv/ directory contains tab-separated values files for each year's proceedings. There is also an AWK script under tool ([tsv-markdown.awk](tools/tsv-markdown.awk)) that can be used to convert the TSV into Markdown to be used in the proceedings/ directory. It does not generate the header section though, that should be done manually. 

For the script to work properly, the TSV file should contain the following columns (inspect the existing ones):

| Column # | Column Content            | Notes                                                                                                                                                                                                                                                                 |
|----------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1        | Authors (RECOMB version)  |                                                                                                                                                                                                                                                                       |
| 2        | Title (RECOMB version)    |                                                                                                                                                                                                                                                                       |
| 3        | LNCS Page numbers         | If left empty, or written as NONE, scripts will skip printing the LCNS citation.                                                                                                                                                                                      |
| 4        | LNCS DOI                  | The header MUST be in the following format: "LNCS volume_number DOI".  For example: LNCS 13976 DOI. The script will parse this to get the volume number. **DO NOT** add https://doi.org/ in the entries, just give the DOI.                                           |
| 5        | Preprint                  | bioRxiv or arXiv.  bioRxiv preprints should be given as "bioRxiv 2022.10.26.513897" arXiv preprints should be given as "arXiv:2303.02162". The scripts will insert the full DOI. If left empty, or written as NONE, scripts will skip printing the preprint citation. |
| 6        | Journal Name              | If left empty,  or written as NONE, scripts will skip printing the journal version citation;  and will not process the remaining columns.                                                                                                                             |
| 7        | Title (Journal Version)   |                                                                                                                                                                                                                                                                       |
| 8        | Authors (Journal version) | If left empty, scripts will copy from the first column.                                                                                                                                                                                                               |
| 9        | Issue and pages           | Journal volume/issue/page info. Example:  30(11): 1198–1225                                                                                                                                                                                                           |
| 10       | Year                      | Journal version publication year                                                                                                                                                                                                                                      |
| 11       | Journal Version DOI       | **DO NOT** add https://doi.org/ in the entries, just give the DOI.                                                                                                                                                                                                    |



Run the Markdown generation script as:

```
awk -f tsv-markdown.awk recomb2023.tsv >> ../proceedings/2025-2021/2023.md
```

## Using Gemini Deep Research to populate the tables as much as possible.

Here is the prompt we used: [prompt](tools/gemini-prompt.txt).  This is about 70% helpful, the missing entries should be manually filled in.



