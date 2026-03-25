# $1: Authors
# $2: Title
# $3: LNCS Pages
# $4: LNCS DOI	
# $5: Preprint
# $6: Journal	
# $7: Title (Journal version)	
# $8: Journal Authors
# $9: Issue and Pages
# $10: Journal Year
# $11: Journal DOI

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

	if ($3 ~ /LNCS/)
	{
		# just get LNCS volume	
		match($4, /[0-9]+/)
		lncs_volume = substr($4, RSTART, RLENGTH)
		proceedings_type = "lncs"
	}
	else if ($3 ~ /ACM/)
	{
		proceedings_type = "acm"
		lncs_volume = ""
	}
}
else
{
	authors = $1
	title = $2
	lncs_pages = $3
	lncs_doi = $4
	preprint = $5
	journal = $6
	journal_title = $7
	journal_authors = $8
	journal_issue_pages = $9
	journal_year = $10
	journal_doi = $11

	print "- **"title"**. "authors"."
	if (proceedings_type == "lncs")
	{
		if (lncs_pages != "" && lncs_pages != "NONE" && lncs_pages != "N/A")
		{
			print "  - Proceedings: Research in Computational Molecular Biology. RECOMB "recomb_year". Lecture Notes in Computer Science, vol "lncs_volume", pp "lncs_pages", Springer, Cham."
			print "    - DOI: ["lncs_doi"](https://doi.org/"lncs_doi")"
		}
	}
	else
	{
		if (lncs_pages != "" && lncs_pages != "NONE" && lncs_pages != "N/A")
		{
			print "  - Proceedings: Research in Computational Molecular Biology. RECOMB "recomb_year", pp "lncs_pages". Association for Computing Machinery, New York, NY, USA."
			print "    - DOI: ["lncs_doi"](https://doi.org/"lncs_doi")"
		}
	}
	if (preprint != "" && preprint != "NONE" && preprint != "N/A")
	{
		temp = preprint
		if (preprint ~ /bioRxiv/) 
		{
			sub(/^bioRxiv /, "", temp)
			print "  - Preprint: ["preprint"](https://doi.org/10.1101/"temp")"
		}
		else if (preprint ~ /arXiv/)
		{
			sub(/^arXiv:/, "arXiv.", temp)
			print "  - Preprint: ["preprint"](https://doi.org/10.48550/"temp")"
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
