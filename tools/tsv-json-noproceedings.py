import csv
import json
import re
import argparse

def tsv_to_json(tsv_filepath, output_filepath=None):
    # Hardcoded metadata from the AWK script [cite: 6]
    data = {
        "title": "24th Annual International Conference on Research in Computational Molecular Biology",
        "location": "xx, yy",
        "dates": "June 22-25, 2020",
        "editor": "pc chair",
        "website": "https://recomb.org/recomb2022/",
        "proceedings": "https://recomb.org/proceedings/2020-2016/2020/",
        "papers": []
    }

    recomb_year = ""

    with open(tsv_filepath, 'r', encoding='utf-8') as f:
        # Read the TSV file [cite: 6]
        reader = csv.reader(f, delimiter='\t')
        
        for row in reader:
            # Pad the row with empty strings to ensure we have exactly 10 columns [cite: 6]
            row = row + [""] * (10 - len(row))
            
            # Map columns according to the original script 
            col_authors = row[0].strip()
            col_title = row[1].strip()
            col_doi_head = row[2].strip()
            col_preprint = row[3].strip()
            col_journal = row[4].strip()
            col_journal_title = row[5].strip()
            col_journal_authors = row[6].strip()
            col_journal_issue = row[7].strip()
            col_journal_year = row[8].strip()
            col_journal_doi = row[9].strip()

            # Ignore entirely empty rows
            if not col_authors and not col_title:
                continue

            # Header row logic (equivalent to: if ($1 ~ /Authors/)) [cite: 6]
            if "Authors" in col_authors:
                year_match = re.search(r'\d+', col_title)
                if year_match:
                    recomb_year = year_match.group(0)
                continue  # Skip to the next row (data rows)
            
            # Initialize the paper dictionary [cite: 7]
            paper = {
                "author": col_authors,
                "title": col_title
            }

            # Preprint Logic [cite: 7]
            if col_preprint and col_preprint not in ("NONE", "N/A"):
                paper["preprint_id"] = col_preprint
                
                if "bioRxiv" in col_preprint:
                    temp = re.sub(r'^bioRxiv ', '', col_preprint)
                    paper["preprint_doi"] = f"{col_doi_head}/{temp}"
                elif "arXiv" in col_preprint:
                    temp = re.sub(r'^arXiv:', 'arXiv.', col_preprint)
                    paper["preprint_doi"] = f"{col_doi_head}/{temp}"
                elif "medRxiv" in col_preprint:
                    temp = re.sub(r'^medRxiv ', '', col_preprint)
                    paper["preprint_doi"] = f"{col_doi_head}/{temp}"
                elif "hal" in col_preprint:
                    paper["preprint_doi"] = f"hal.science/{col_preprint}" # Not a real DOI, matching original script

            # Journal Logic [cite: 7, 8]
            if col_journal and col_journal not in ("NONE", "N/A"):
                paper["journal"] = col_journal
                paper["journal_title"] = col_journal_title # Strip handled earlier
                paper["journal_authors"] = col_journal_authors if col_journal_authors else col_authors
                paper["journal_issue_pages"] = col_journal_issue
                paper["journal_year"] = col_journal_year
                
                # Remove carriage returns from DOI [cite: 8]
                paper["journal_doi"] = col_journal_doi.replace("\r", "")

            # Append the structured paper object to our data array
            data["papers"].append(paper)

    # Convert the Python dictionary into a formatted JSON string
    json_string = json.dumps(data, indent=4, ensure_ascii=False)

    if output_filepath:
        with open(output_filepath, 'w', encoding='utf-8') as out_f:
            out_f.write(json_string)
        print(f"Success! Valid JSON saved to {output_filepath}")
    else:
        print(json_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert Recomb TSV to valid JSON (No Proceedings variant)")
    parser.add_argument("input_tsv", help="Path to the input TSV file")
    parser.add_argument("-o", "--output", help="Path to save the output JSON file", default=None)
    
    args = parser.parse_args()
    tsv_to_json(args.input_tsv, args.output)
