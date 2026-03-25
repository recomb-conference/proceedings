# $1: Authors
# $2: Title
# $3: Preprint DOI Head	
# $4: Preprint
# $5: Journal	
# $6: Title (Journal version)	
# $7: Journal Authors
# $8: Issue and Pages
# $9: Journal Year
# $10: Journal DOI

BEGIN {
    FS = "\t"      # or ":", ",", " "
    print ""
    print "## List of Publications"
    print ""
}
{
if ($1 ~ /Authors/)
{
	match($2, /[0-9]+/)
	recomb_year = substr($2, RSTART, RLENGTH) 

}
else
{
	authors = $1
	title = $2
	doi_head = $3
	preprint = $4
	journal = $5
	journal_title = $6
	journal_authors = $7
	journal_issue_pages = $8
	journal_year = $9
	journal_doi = $10

	print "- **"title"**. "authors"."
	if (preprint != "" && preprint != "NONE" && preprint != "N/A")
	{
		temp = preprint
		if (preprint ~ /bioRxiv/) 
		{
			sub(/^bioRxiv /, "", temp)
			print "  - Preprint: ["preprint"](https://doi.org/"doi_head"/"temp")"
		}
		else if (preprint ~ /arXiv/)
		{
			sub(/^arXiv:/, "arXiv.", temp)
			print "  - Preprint: ["preprint"](https://doi.org/"doi_head"/"temp")"
		}
		else if (preprint ~ /medRxiv/)
		{
			sub(/^medRxiv /, "", temp)
			print "  - Preprint: ["preprint"](https://doi.org/"doi_head"/"temp")"
		}
		else if (preprint ~ /hal/)
		{
			print "  - Preprint: ["preprint"](https://hal.science/"temp")"
		}		
	}
	if (journal != "" && journal != "NONE" && journal != "N/A")
	{
		gsub(/^[ \t]+|[ \t]+$/, "", journal_title)
		if (journal_authors == "")
		{
			print "  - Journal: **"journal_title"**. "authors". *"journal"*, "journal_issue_pages", "journal_year"."
		}
		else
		{
			print "  - Journal: **"journal_title"**. "journal_authors". *"journal"*, "journal_issue_pages", "journal_year"."
		}
		tmp = journal_doi
    		gsub(/\r/, "", tmp)
		print "    - DOI: ["tmp"](https://doi.org/"tmp")"		
	}
	print "\n"
}  
}
