import json
import re
import argparse
import sys

def parse_journal_info(info_str):
    """
    Splits strings like '27(4): 485-499' into volume, issue, and pages.
    """
    if not info_str:
        return None, None, ""
        
    # Regex: volume(issue): pages
    pattern = r"(\d+)\((.*?)\):\s*(.*)"
    match = re.search(pattern, info_str)
    
    if match:
        volume = match.group(1)
        issue = match.group(2)
        pages = match.group(3).replace('-', '--')
        return volume, issue, pages
    return None, None, info_str.replace('-', '--')

def convert(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    bib_entries = []

    for paper in data.get('papers', []):
        # Logic: Priority to journal fields if available
        has_journal = 'journal' in paper
        
        author = paper.get('journal_authors', paper.get('author')) if has_journal else paper.get('author')
        title = paper.get('journal_title', paper.get('title')) if has_journal else paper.get('title')
        
        # Generate citekey: CapitalizedLastnameYear (e.g., Sarnaik2025)
        # We use the author string to extract the first author's last name
        first_author_token = author.split(',')[0].strip()
        last_name = first_author_token.split(' ')[-1].capitalize()
        year = paper.get('journal_year') or "2025"
        cite_key = f"{last_name}{year}"

        # Consolidate all extra metadata
        extra_fields = {
            "proceedings_name": paper.get("proceedings_name"),
            "proceedings_volume": paper.get("proceedings_volume"),
            "proceedings_pages": paper.get("proceedings_pages", "").replace('-', '--'),
            "proceedings_doi": paper.get("proceedings_doi"),
            "preprint_id": paper.get("preprint_id"),
            "preprint_doi": paper.get("preprint_doi")
        }

        if has_journal:
            vol, issue, pg = parse_journal_info(paper.get('journal_issue_pages', ''))
            entry_type = "article"
            main_fields = {
                "author": author,
                "title": title,
                "journal": paper.get('journal'),
                "volume": vol,
                "number": issue,
                "pages": pg,
                "year": year,
                "doi": paper.get('journal_doi')
            }
        else:
            entry_type = "inproceedings"
            main_fields = {
                "author": author,
                "title": title,
                "booktitle": paper.get('proceedings_name', 'RECOMB 2025'),
                "pages": paper.get('proceedings_pages', '').replace('-', '--'),
                "year": "2025",
                "doi": paper.get('proceedings_doi')
            }

        # Combine main and extra fields, filtering out empty values
        all_fields = {**main_fields, **extra_fields}
        
        # Build BibTeX entry string
        bib_str = f"@{entry_type}{{{cite_key},\n"
        for key, value in all_fields.items():
            if value: 
                bib_str += f"  {key} = {{{value}}},\n"
        bib_str = bib_str.rstrip(",\n") + "\n}"
        
        bib_entries.append(bib_str)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(bib_entries))
    print(f"Successfully converted {len(bib_entries)} entries to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RECOMB JSON to BibTeX.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    parser.add_argument("-o", "--output", required=True, help="Output BibTeX file")
    
    args = parser.parse_args()
    convert(args.input, args.output)
