# RECOMB Proceedings. 

- Web page design forked from [Just the Docs](https://github.com/just-the-docs/just-the-docs) and edited by: [Arda İçöz](https://github.com/ardaicoz)
- Data collection: [Ali Balapour](https://github.com/alibalapour), [Emir Tomrukçu](https://github.com/emirtom), [Arda İçöz](https://github.com/ardaicoz), [Can Alkan](https://github.com/calkan), and [Gemini Deep Research](https://gemini.google/overview/deep-research/).

## Generating Markdown files

The tsv/ directory contains tab-separated values files for each year's proceedings. There is also a python script under tools ([converter.py](tools/[converter.py)) that can be used to convert the TSV into Markdown, JSON, and BiBTeX to be used in the proceedings/ directory. Each file has a header section about the information for that specific year that are used by the converter script.

**Note that a GitHub Actions automatically runs the converter script to generate all necessary files and then build the web page. There is no need to modify any file other than the TSV files.**

For the script to work properly, the TSV file should contain the following columns (inspect the existing ones):

| Column # | Column Content            | Notes                                                                                                                                                                                                                                                                 |
|----------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1        | Authors (RECOMB version)  |                                                                                                                                                                                                                                                                       |
| 2        | Title (RECOMB version)    |                                                                                                                                                                                                                                                                       |
| 3        | LNCS Page numbers         | If left empty, or written as NONE, scripts will skip printing the LCNS citation.                                                                                                                                                                                      |
| 4        | LNCS DOI                  | The header MUST be in the following format: "LNCS volume_number DOI".  For example: LNCS 13976 DOI. The script will parse this to get the volume number. **DO NOT** add https://doi.org/ in the entries, just give the DOI.                                           |
| 5        | Preprint                  | bioRxiv or arXiv.  bioRxiv preprints should be given as "bioRxiv 2022.10.26.513897" arXiv preprints should be given as "arXiv:2303.02162". The scripts will insert the full DOI. If left empty, or written as NONE, scripts will skip printing the preprint citation. |
| 6        | Preprint DOI Prefix       | Prefix for the DOI of the preprints. This was necessary since some 2026 bioRxiv DOIs are different than earlier ones. If left empty, or written as NONE, scripts will skip printing the preprint citation. |
| 7        | Journal Name              | If left empty,  or written as NONE, scripts will skip printing the journal version citation;  and will not process the remaining columns.                                                                                                                             |
| 8        | Title (Journal Version)   |                                                                                                                                                                                                                                                                       |
| 9        | Authors (Journal version) | If left empty, scripts will copy from the first column.                                                                                                                                                                                                               |
| 10        | Issue and pages           | Journal volume/issue/page info. Example:  30(11): 1198–1225                                                                                                                                                                                                           |
| 11       | Year                      | Journal version publication year                                                                                                                                                                                                                                      |
| 12       | Journal Version DOI       | **DO NOT** add https://doi.org/ in the entries, just give the DOI.                                                                                                                                                                                                    |




## Using Gemini Deep Research or Google Antigravity to populate the tables as much as possible.

Here is the prompt we used: [prompt](tools/gemini-prompt.txt). As the prompt says, you need to upload a TSV file that contains the author names and paper titles (and the LNCS pages and DOI if possible). Gemini and Antigravity are about 70% helpful, the missing entries should be manually filled in. There could also be misidentified papers or hallucinations.



