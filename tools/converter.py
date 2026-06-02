#!/usr/bin/env python3
import argparse
import csv
import sys
import json

def get_ordinal(n):
    """Returns the number with its ordinal suffix (e.g. 1st, 2nd, 3rd, 4th)."""
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def convert_tsv(input_tsv, output_md, output_json):
    metadata = {}
    publications = []

    # Read the TSV file and extract both the header variables and publications
    try:
        with open(input_tsv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            
            parsing_publications = False
            for row in reader:
                if not row:
                    continue
                
                key = row[0].strip()
                
                # Switch to parsing mode when hitting the publications header
                if key == '#Authors':
                    parsing_publications = True
                    continue
                
                if not parsing_publications:
                    if key.startswith('#'):
                        val = row[1].strip() if len(row) > 1 else ''
                        metadata[key] = val
                else:
                    publications.append(row)
                    
    except FileNotFoundError:
        print(f"\n[ERROR] The input file '{input_tsv}' was not found.")
        print("Please check the file path and try again.\n")
        sys.exit(1)

    # Extract required header fields with default fallbacks
    year_str = metadata.get('#Year', '')
    location = metadata.get('#Location', '')
    dates = metadata.get('#Dates', '')
    pc_chair = metadata.get('#PC_Chair', '')
    org_committee = metadata.get('#Organization_Committee', '')
    keynotes = metadata.get('#Keynotes', '')
    website = metadata.get('#Website', '') 
    
    # Store Proceedings variables
    proc_type = metadata.get('#Proceedings_Type', 'NONE')
    proc_vol = metadata.get('#Proceedings_Volume', '')
    
    # Calculate iteration and bounds
    year = int(year_str) if year_str.isdigit() else 2018
    iteration = year - 1996 
    
    # Format the dates string to ensure it includes the year for the JSON output
    json_dates = dates
    if dates and str(year) not in dates:
        json_dates = f"{dates}, {year}"
    
    # Dynamic Parent Logic
    remainder = year % 5
    upper_bound = year if remainder == 0 else year + (5 - remainder)
    lower_bound = max(1997, upper_bound - 4)
    
    parent = f"{upper_bound}-{lower_bound}"
    nav_order = upper_bound - year + 1

    md_content = ""
    json_data = {}
    
    # Init Markdown Base
    if output_md:
        # Format the website as a Markdown link if it exists
        website_line = f"**Website:** [{website}]({website})  \n" if website else ""
        md_content = f"""---
title: {year}
nav_order: {nav_order}
parent: {parent}
---

# RECOMB {year} Proceedings

### {location}, {dates}, {year}  
**PC Chair:** {pc_chair}  
**Organization Committee:** {org_committee}  
**Keynote Speakers:** {keynotes}  
{website_line}
## List of Publications
"""
    # Init JSON Base
    if output_json:
        conf_title = f"{get_ordinal(iteration)} Annual International Conference on Research in Computational Molecular Biology"
        json_data = {
            "title": conf_title,
            "location": location,
            "dates": json_dates,
            "pc_chair": pc_chair,
            "organization_committee": org_committee,
            "keynotes": keynotes,
            "website": website,
            "papers": []
        }

    # --- PROCESS PUBLICATIONS ROW BY ROW ---
    for row in publications:
        # Skip empty lines in the publication block
        if not row or not row[0].strip():
            continue
            
        authors = row[0].strip()
        title = row[1].strip() if len(row) > 1 else ''
        pages = row[2].strip() if len(row) > 2 else ''
        proc_doi = row[3].strip() if len(row) > 3 else ''
        
        # Base JSON paper object prep
        paper_obj = {}
        if output_json:
            paper_obj["author"] = authors
            paper_obj["title"] = title
            
        if output_md:
            md_content += f"\n\n- **{title}**. {authors}.\n"
        
        # 1. Proceedings Format based on type
        if proc_type == 'LNCS':
            proc_str = f"Research in Computational Molecular Biology. RECOMB {year}. Lecture Notes in Computer Science, vol {proc_vol}, pp {pages}, Springer, Cham."
            if output_md:
                md_content += f"  - Proceedings: {proc_str}\n"
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    md_content += f"    - DOI: [{proc_doi}](https://doi.org/{proc_doi})\n"
            if output_json:
                paper_obj["proceedings_name"] = proc_str
                if proc_vol: paper_obj["proceedings_volume"] = proc_vol
                if pages: paper_obj["proceedings_pages"] = pages
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    paper_obj["proceedings_doi"] = proc_doi
                    
        elif proc_type == 'ACM':
            proc_str = f"Research in Computational Molecular Biology. RECOMB {year}, pp {pages}. Association for Computing Machinery, New York, NY, USA."
            if output_md:
                md_content += f"  - Proceedings: {proc_str}\n"
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    md_content += f"    - DOI: [{proc_doi}](https://doi.org/{proc_doi})\n"
            if output_json:
                paper_obj["proceedings_name"] = proc_str
                if pages: paper_obj["proceedings_pages"] = pages
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    paper_obj["proceedings_doi"] = proc_doi
                
        # 2. Preprint Format
        if len(row) > 4:
            preprint_text = row[4].strip()
            if preprint_text and preprint_text.upper() not in ('NONE', 'N/A', ''):
                
                # --- HAL LOGIC ---
                if preprint_text.lower().startswith('hal'):
                    hal_url = f"https://hal.science/{preprint_text}"
                    if output_md:
                        md_content += f"  - Preprint: [{preprint_text}]({hal_url})\n"
                    if output_json:
                        paper_obj["preprint_id"] = preprint_text
                        paper_obj["preprint_url"] = hal_url 
                        
                else:
                    # --- STANDARD DOI LOGIC ---
                    preprint_prefix = row[5].strip() if len(row) > 5 else ''
                    
                    # Normalize prefix and build link
                    if not preprint_prefix.endswith('/'):
                        if preprint_prefix == '10.4855': 
                            preprint_prefix = '10.48550/'
                        elif preprint_prefix:
                            preprint_prefix += '/'
                    
                    if preprint_text.startswith('bioRxiv'):
                        doi_id = preprint_text.replace('bioRxiv', '').replace(' ', '')
                        link_val = f"{preprint_prefix}{doi_id}"
                    elif preprint_text.startswith('arXiv:'):
                        url_id = preprint_text.replace('arXiv:', 'arXiv.')
                        link_val = f"{preprint_prefix}{url_id}"
                    else:
                        link_val = f"{preprint_prefix}{preprint_text}"
                        
                    if output_md:
                        md_content += f"  - Preprint: [{preprint_text}](https://doi.org/{link_val})\n"
                    if output_json:
                        paper_obj["preprint_id"] = preprint_text
                        paper_obj["preprint_doi"] = link_val
                
        # 3. Journal Format
        if len(row) > 6:
            j_name = row[6].strip()
            if j_name and j_name.upper() not in ('NONE', 'N/A', ''):
                j_title = row[7].strip() if len(row) > 7 else ''
                j_authors = row[8].strip() if len(row) > 8 else ''
                j_vol = row[9].strip() if len(row) > 9 else ''
                j_year = row[10].strip() if len(row) > 10 else ''
                j_doi = row[11].strip() if len(row) > 11 else ''
                
                if output_md:
                    md_content += f"  - Journal: **{j_title}**. {j_authors}. *{j_name}*, {j_vol}, {j_year}.\n"
                    if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                        md_content += f"    - DOI: [{j_doi}](https://doi.org/{j_doi})\n"
                
                if output_json:
                    paper_obj["journal"] = j_name
                    if j_title: paper_obj["journal_title"] = j_title
                    if j_authors: paper_obj["journal_authors"] = j_authors
                    if j_vol: paper_obj["journal_issue_pages"] = j_vol
                    if j_year: paper_obj["journal_year"] = j_year
                    if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                        paper_obj["journal_doi"] = j_doi
                        
        if output_json:
            json_data["papers"].append(paper_obj)

    # --- WRITE FILES ---
    if output_md:
        try:
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"[SUCCESS] Markdown format saved to: '{output_md}'")
        except Exception as e:
            print(f"\n[ERROR] Could not write to file '{output_md}': {e}\n")
            
    if output_json:
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"[SUCCESS] JSON format saved to: '{output_json}'")
        except Exception as e:
            print(f"\n[ERROR] Could not write to file '{output_json}': {e}\n")

if __name__ == "__main__":
    custom_epilog = """
Examples:
  ./converter.py -i "data.tsv" -md "output.md"
  ./converter.py -i "data.tsv" -json "output.json"
  ./converter.py -i "data.tsv" -md "output.md" -json "output.json"
"""
    parser = argparse.ArgumentParser(
        description='Convert RECOMB TSV files into Markdown and/or JSON format.',
        epilog=custom_epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--input', required=True, help='Path to the input TSV file')
    parser.add_argument('-md', '--markdown', help='Path to the output Markdown file')
    parser.add_argument('-json', '--json', help='Path to the output JSON file')
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    try:
        args = parser.parse_args()
        
        if not args.markdown and not args.json:
            parser.error("\n[ERROR] You must provide an output path! Provide at least one: -md OR -json")
            
        convert_tsv(args.input, args.markdown, args.json)
    except SystemExit:
        sys.exit(1)
