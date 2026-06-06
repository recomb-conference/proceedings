#!/usr/bin/env python3
import argparse
import csv
import sys
import json
import re

def get_ordinal(n):
    """Returns the number with its ordinal suffix (e.g. 1st, 2nd, 3rd, 4th)."""
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def convert_tsv(input_tsv, output_md, output_json, output_bib):
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
    bib_content = ""
    
    # Init Markdown Base
    if output_md:
        website_line = f"**Website:** [{website}]({website})  \n" if website else ""
        json_url = f"https://recomb.org/proceedings/json/recomb{year}.json"
        bib_url = f"https://recomb.org/proceedings/bibtex/recomb{year}.bib"
        exports_line = f"**Export:** [JSON]({json_url}) | [BibTeX]({bib_url})  \n"
        
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
{website_line}{exports_line}
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
        if not row or not row[0].strip():
            continue
            
        # 1. CORE VARIABLES
        authors = row[0].strip()
        title = row[1].strip() if len(row) > 1 else ''
        pages = row[2].strip() if len(row) > 2 else ''
        proc_doi = row[3].strip() if len(row) > 3 else ''
        
        # 2. PROCEEDINGS STRING FORMATTING
        proc_str = ""
        if proc_type == 'LNCS':
            proc_str = f"Research in Computational Molecular Biology. RECOMB {year}. Lecture Notes in Computer Science, vol {proc_vol}, pp {pages}, Springer, Cham."
        elif proc_type == 'ACM':
            proc_str = f"Research in Computational Molecular Biology. RECOMB {year}, pp {pages}. Association for Computing Machinery, New York, NY, USA."
            
        # 3. PREPRINT URL FORMATTING
        hal_url = ""
        link_val = ""
        preprint_text = ""
        
        if len(row) > 4:
            preprint_text = row[4].strip()
            if preprint_text and preprint_text.upper() not in ('NONE', 'N/A', ''):
                if preprint_text.lower().startswith('hal'):
                    hal_url = f"https://hal.science/{preprint_text}"
                else:
                    preprint_prefix = row[5].strip() if len(row) > 5 else ''
                    if not preprint_prefix.endswith('/'):
                        if preprint_prefix == '10.4855': preprint_prefix = '10.48550/'
                        elif preprint_prefix: preprint_prefix += '/'
                    
                    if preprint_text.startswith('bioRxiv'):
                        doi_id = preprint_text.replace('bioRxiv', '').replace(' ', '')
                        link_val = f"{preprint_prefix}{doi_id}"
                    elif preprint_text.startswith('arXiv:'):
                        url_id = preprint_text.replace('arXiv:', 'arXiv.')
                        link_val = f"{preprint_prefix}{url_id}"
                    else:
                        link_val = f"{preprint_prefix}{preprint_text}"
                        
        # 4. JOURNAL VARIABLES FORMATTING
        j_name = j_title = j_authors = j_vol_str = j_year = j_doi = ""
        has_journal = False
        if len(row) > 6:
            j_name = row[6].strip()
            if j_name and j_name.upper() not in ('NONE', 'N/A', ''):
                has_journal = True
                j_title = row[7].strip() if len(row) > 7 else ''
                j_authors = row[8].strip() if len(row) > 8 else ''
                j_vol_str = row[9].strip() if len(row) > 9 else ''
                j_year = row[10].strip() if len(row) > 10 else ''
                j_doi = row[11].strip() if len(row) > 11 else ''

        # --- BUILD MARKDOWN ---
        if output_md:
            md_content += f"\n\n- **{title}**. {authors}.\n"
            if proc_str:
                md_content += f"  - Proceedings: {proc_str}\n"
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    md_content += f"    - DOI: [{proc_doi}](https://doi.org/{proc_doi})\n"
            
            if hal_url:
                md_content += f"  - Preprint: [{preprint_text}]({hal_url})\n"
            elif link_val:
                md_content += f"  - Preprint: [{preprint_text}](https://doi.org/{link_val})\n"
                
            if has_journal:
                md_content += f"  - Journal: **{j_title}**. {j_authors}. *{j_name}*, {j_vol_str}, {j_year}.\n"
                if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                    md_content += f"    - DOI: [{j_doi}](https://doi.org/{j_doi})\n"

        # --- BUILD JSON ---
        if output_json:
            paper_obj = {
                "author": authors,
                "title": title
            }
            if proc_str:
                paper_obj["proceedings_name"] = proc_str
                if proc_vol and proc_type == 'LNCS': paper_obj["proceedings_volume"] = proc_vol
                if pages: paper_obj["proceedings_pages"] = pages
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    paper_obj["proceedings_doi"] = proc_doi
                    
            if preprint_text and preprint_text.upper() not in ('NONE', 'N/A', ''):
                paper_obj["preprint_id"] = preprint_text
                if hal_url: paper_obj["preprint_url"] = hal_url
                elif link_val: paper_obj["preprint_doi"] = link_val
                
            if has_journal:
                paper_obj["journal"] = j_name
                if j_title: paper_obj["journal_title"] = j_title
                if j_authors: paper_obj["journal_authors"] = j_authors
                if j_vol_str: paper_obj["journal_issue_pages"] = j_vol_str
                if j_year: paper_obj["journal_year"] = j_year
                if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                    paper_obj["journal_doi"] = j_doi
                    
            json_data["papers"].append(paper_obj)

        # --- BUILD BIBTEX ---
        if output_bib:
            bib_authors = j_authors if (has_journal and j_authors) else authors
            
            # Extract first author's last name for the bib key
            if not bib_authors: last_name = "Unknown"
            else:
                first_auth = bib_authors.split(' and ')[0] if ' and ' in bib_authors else bib_authors.split(',')[0]
                last_name = first_auth.strip().split(' ')[-1]
                
            bib_entry = ""
            if has_journal:
                b_year = j_year if j_year else str(year)
                bib_key = f"{last_name}{b_year}"
                bib_entry += f"@article{{{bib_key},\n"
                bib_entry += f"  author = {{{bib_authors}}},\n"
                bib_entry += f"  title = {{{j_title if j_title else title}}},\n"
                bib_entry += f"  journal = {{{j_name}}},\n"
                
                # Split Volume/Num/Pages if strictly formatted like "30(11): 1146-1181"
                if j_vol_str:
                    m = re.match(r"([^()]+)\(([^()]+)\):\s*(.*)", j_vol_str)
                    if m:
                        bib_entry += f"  volume = {{{m.group(1).strip()}}},\n"
                        bib_entry += f"  number = {{{m.group(2).strip()}}},\n"
                        bib_entry += f"  pages = {{{m.group(3).strip().replace('-', '--').replace('–', '--')}}},\n"
                    else:
                        bib_entry += f"  volume = {{{j_vol_str}}},\n"
                        
                bib_entry += f"  year = {{{b_year}}},\n"
                if j_doi and j_doi.upper() not in ('NONE', 'N/A', ''):
                    bib_entry += f"  doi = {{{j_doi}}},\n"
            else:
                bib_key = f"{last_name}{year}"
                bib_entry += f"@inproceedings{{{bib_key},\n"
                bib_entry += f"  author = {{{bib_authors}}},\n"
                bib_entry += f"  title = {{{title}}},\n"
                if proc_str: bib_entry += f"  booktitle = {{{proc_str}}},\n"
                if pages: bib_entry += f"  pages = {{{pages.replace('-', '--').replace('–', '--')}}},\n"
                bib_entry += f"  year = {{{year}}},\n"
                if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                    bib_entry += f"  doi = {{{proc_doi}}},\n"
                    
            # Inject Common Custom Proceedings Fields
            if proc_str: bib_entry += f"  proceedings_name = {{{proc_str}}},\n"
            if proc_vol: bib_entry += f"  proceedings_volume = {{{proc_vol}}},\n"
            if pages: bib_entry += f"  proceedings_pages = {{{pages.replace('-', '--').replace('–', '--')}}},\n"
            if proc_doi and proc_doi.upper() not in ('NONE', 'N/A', ''):
                bib_entry += f"  proceedings_doi = {{{proc_doi}}},\n"

            # Inject Preprint Common Fields
            if preprint_text and preprint_text.upper() not in ('NONE', 'N/A', ''):
                bib_entry += f"  preprint_id = {{{preprint_text}}},\n"
                if hal_url: bib_entry += f"  preprint_url = {{{hal_url}}},\n"
                elif link_val: bib_entry += f"  preprint_doi = {{{link_val}}},\n"

            bib_entry = bib_entry.rstrip(',\n') + "\n}\n\n"
            bib_content += bib_entry

    # --- WRITE FILES TO DISK ---
    if output_md:
        try:
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"[SUCCESS] Markdown format saved to: '{output_md}'")
        except Exception as e: print(f"\n[ERROR] Could not write '{output_md}': {e}\n")
            
    if output_json:
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"[SUCCESS] JSON format saved to: '{output_json}'")
        except Exception as e: print(f"\n[ERROR] Could not write '{output_json}': {e}\n")
            
    if output_bib:
        try:
            with open(output_bib, 'w', encoding='utf-8') as f:
                f.write(bib_content)
            print(f"[SUCCESS] BibTeX format saved to: '{output_bib}'")
        except Exception as e: print(f"\n[ERROR] Could not write '{output_bib}': {e}\n")

if __name__ == "__main__":
    custom_epilog = """
Examples:
  ./converter.py -i "data.tsv" -md "output.md"
  ./converter.py -i "data.tsv" -json "output.json" -bib "output.bib"
  ./converter.py -i "data.tsv" -md "output.md" -json "output.json" -bib "output.bib"
"""
    parser = argparse.ArgumentParser(
        description='Convert RECOMB TSV files into Markdown, JSON, and/or BibTeX format.',
        epilog=custom_epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--input', required=True, help='Path to the input TSV file')
    parser.add_argument('-md', '--markdown', help='Path to the output Markdown file')
    parser.add_argument('-json', '--json', help='Path to the output JSON file')
    parser.add_argument('-bib', '--bibtex', help='Path to the output BibTeX file')
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    try:
        args = parser.parse_args()
        if not args.markdown and not args.json and not args.bibtex:
            parser.error("\n[ERROR] You must provide an output path! Provide at least one: -md, -json, OR -bib")
            
        convert_tsv(args.input, args.markdown, args.json, args.bibtex)
    except SystemExit:
        sys.exit(1)
