#!/usr/bin/env python3
import argparse
import csv
import sys

def convert_tsv_to_markdown(input_tsv, output_md):
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
    
    # Store Proceedings variables to be used in the loop
    proc_type = metadata.get('#Proceedings_Type', 'NONE')
    proc_vol = metadata.get('#Proceedings_Volume', '')
    
    # Calculate iteration and dynamic front-matter bounds
    year = int(year_str) if year_str.isdigit() else 2018
    iteration = year - 1996 
    
    # Dynamic Parent Logic (Divisible by 5, Minimum bound 1997)
    remainder = year % 5
    upper_bound = year if remainder == 0 else year + (5 - remainder)
    lower_bound = max(1997, upper_bound - 4)
    
    parent = f"{upper_bound}-{lower_bound}"
    nav_order = upper_bound - year + 1

    # Format the markdown header
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

## List of Publications
"""

    # --- PROCESS PUBLICATIONS ROW BY ROW ---
    for row in publications:
        # Skip empty lines in the publication block
        if not row or not row[0].strip():
            continue
            
        authors = row[0].strip()
        title = row[1].strip() if len(row) > 1 else ''
        pages = row[2].strip() if len(row) > 2 else ''
        proc_doi = row[3].strip() if len(row) > 3 else ''
        
        # Base format for every paper
        md_content += f"\n\n- **{title}**. {authors}.\n"
        
        # 1. Proceedings Format based on type (LNCS, ACM, NONE)
        if proc_type == 'LNCS':
            md_content += f"  - Proceedings: Research in Computational Molecular Biology. RECOMB {year}. Lecture Notes in Computer Science, vol {proc_vol}, pp {pages}, Springer, Cham.\n"
            if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                md_content += f"    - DOI: [{proc_doi}](https://doi.org/{proc_doi})\n"
        
        elif proc_type == 'ACM':
            md_content += f"  - Proceedings: Research in Computational Molecular Biology. RECOMB {year}, pp {pages}. Association for Computing Machinery, New York, NY, USA.\n"
            if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                md_content += f"    - DOI: [{proc_doi}](https://doi.org/{proc_doi})\n"
                
        # 2. Preprint Format
        if len(row) > 4:
            preprint_text = row[4].strip()
            if preprint_text and preprint_text.upper() not in ('NONE', 'N/A'):
                preprint_prefix = row[5].strip() if len(row) > 5 else ''
                
                # Normalize the prefix to cleanly build the link
                if not preprint_prefix.endswith('/'):
                    # Fix standard CrossRef missing 0 for arXiv prefix (10.4855 -> 10.48550/)
                    if preprint_prefix == '10.4855': 
                        preprint_prefix = '10.48550/'
                    elif preprint_prefix:
                        preprint_prefix += '/'
                
                if preprint_text.startswith('bioRxiv'):
                    # Remove the string "bioRxiv" and trim any inner spaces
                    doi_id = preprint_text.replace('bioRxiv', '').replace(' ', '')
                    link_url = f"{preprint_prefix}{doi_id}"
                
                elif preprint_text.startswith('arXiv:'):
                    # For DOI links, replace ":" with "." so crossref resolves properly
                    url_id = preprint_text.replace('arXiv:', 'arXiv.')
                    link_url = f"{preprint_prefix}{url_id}"
                
                else:
                    # Fallback straight concatenation
                    link_url = f"{preprint_prefix}{preprint_text}"
                    
                md_content += f"  - Preprint: [{preprint_text}](https://doi.org/{link_url})\n"
                
        # 3. Journal Format (If present)
        if len(row) > 6:
            j_name = row[6].strip()
            if j_name and j_name.upper() not in ('NONE', 'N/A', ''):
                j_title = row[7].strip() if len(row) > 7 else ''
                j_authors = row[8].strip() if len(row) > 8 else ''
                j_vol = row[9].strip() if len(row) > 9 else ''
                j_year = row[10].strip() if len(row) > 10 else ''
                j_doi = row[11].strip() if len(row) > 11 else ''
                
                md_content += f"  - Journal: **{j_title}**. {j_authors}. *{j_name}*, {j_vol}, {j_year}.\n"
                if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                    md_content += f"    - DOI: [{j_doi}](https://doi.org/{j_doi})\n"

    # Write the completed output
    try:
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"\nSuccess! Full file converted and saved to '{output_md}'.")
        print(f"Year: {year} | Parent: {parent} | Iteration: {iteration}\n")
    except Exception as e:
        print(f"\n[ERROR] Could not write to file '{output_md}': {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    custom_epilog = """
Examples:
  ./converter.py -i "RECOMB Proceedings - Official List - 2018.tsv" -md "2018.md"
  python3 converter.py -i data.tsv -md output.md
"""
    parser = argparse.ArgumentParser(
        description='Convert RECOMB TSV files into Markdown format including all publications.',
        epilog=custom_epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--input', required=True, help='Path to the input TSV file')
    parser.add_argument('-md', '--markdown', required=True, help='Path to the output Markdown file')
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    try:
        args = parser.parse_args()
        convert_tsv_to_markdown(args.input, args.markdown)
    except SystemExit:
        sys.exit(1)
