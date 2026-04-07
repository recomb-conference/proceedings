import csv
import json
import re
import sys
import argparse

def tsv_to_json(tsv_filepath, output_filepath=None):
    # Hardcoded metadata from the original awk script
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
    lncs_volume = ""
    proceedings_type = ""

    with open(tsv_filepath, 'r', encoding='utf-8') as f:
        # Read the TSV file
        reader = csv.reader(f, delimiter='\t')
        
        for row in reader:
            # Pad the row with empty strings in case some columns are missing
            row = row + [""] * (11 - len(row))
            
            # Map columns according to the original script
            col_authors = row[0].strip()
            col_title = row[1].strip()
            col_pages = row[2].strip()
            col_doi = row[3].strip()
            col_preprint = row[4].strip()
            col_journal = row[5].strip()
            col_journal_title = row[6].strip()
            col_journal_authors = row[7].strip()
            col_journal_issue = row[8].strip()
            col_journal_year = row[9].strip()
            col_journal_doi = row[10].strip()

            # Ignore entirely empty rows
            if not col_authors and not col_title:
                continue

            # Header row logic (equivalent to: if ($1 ~ /Authors/))
            if "Authors" in col_authors:
                year_match = re.search(r'\d+', col_title)
                if year_match:
                    recomb_year = year_match.group(0)
                
                if "LNCS" in col_pages:
                    vol_match = re.search(r'\d+', col_doi)
                    if vol_match:
                        lncs_volume = vol_match.group(0)
                    proceedings_type = "lncs"
                elif "ACM" in col_pages:
                    proceedings_type = "acm"
                    lncs_volume = ""
                continue  # Skip to the next row (data rows)
            
            # Initialize the paper dictionary
            paper = {
                "author": col_authors,
                "title": col_title
            }

            # Proceedings Logic
            if col_pages and col_pages not in ("NONE", "N/A"):
                if proceedings_type == "lncs":
                    paper["proceedings_name"] = f"Research in Computational Molecular Biology. RECOMB {recomb_year}. Lecture Notes in Computer Science, vol {lncs_volume}, pp {col_pages}, Springer, Cham."
                    paper["proceedings_volume"] = lncs_volume
                    paper["proceedings_pages"] = col_pages
                    paper["proceedings_doi"] = col_doi
                else:
                    paper["proceedings_name"] = f"Research in Computational Molecular Biology. RECOMB {recomb_year}, pp {col_pages}. Association for Computing Machinery, New York, NY, USA."
                    paper["proceedings_volume"] = lncs_volume
                    paper["proceedings_pages"] = col_pages
                    paper["proceedings_doi"] = col_doi

            # Preprint Logic
            if col_preprint and col_preprint not in ("NONE", "N/A"):
                paper["preprint_id"] = col_preprint
                
                if "bioRxiv" in col_preprint:
                    temp = re.sub(r'^bioRxiv ', '', col_preprint)
                    paper["preprint_doi"] = f"10.1101/{temp}"
                elif "arXiv" in col_preprint:
                    temp = re.sub(r'^arXiv:', 'arXiv.', col_preprint)
                    paper["preprint_doi"] = f"10.48550/{temp}"
                elif "hal" in col_preprint:
                    paper["preprint_doi"] = f"hal.science/{col_preprint}" # Not a real DOI, matching original script

            # Journal Logic
            if col_journal and col_journal not in ("NONE", "N/A"):
                paper["journal"] = col_journal
                paper["journal_title"] = col_journal_title
                paper["journal_authors"] = col_journal_authors if col_journal_authors else col_authors
                paper["journal_issue_pages"] = col_journal_issue
                paper["journal_year"] = col_journal_year
                # Remove carriage returns from DOI
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
    parser = argparse.ArgumentParser(description="Convert Recomb TSV to valid JSON")
    parser.add_argument("input_tsv", help="Path to the input TSV file")
    parser.add_argument("-o", "--output", help="Path to save the output JSON file", default=None)
    
    args = parser.parse_args()
    tsv_to_json(args.input_tsv, args.output)
