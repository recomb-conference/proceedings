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
}
{
if ($1 ~ /Authors/)
{
	# just get LNCS volume	
	match($4, /[0-9]+/)
	lncs_volume = substr($4, RSTART, RLENGTH)
	print "{"
	print "\"title\": \"27th Annual International Conference on Research in Computational Molecular Biology\","
	print "\"location\": \"İstanbul, Türkiye\","
	print "\"dates\": \"April 16-19, 2023\","
	print "\"editor\": \"Haixu Tang\","
	print "\"website\": \"https://recomb.org/recomb2023/\","
	print "\"proceedings\": \"https://recomb.org/proceedings/2025-2021/2023\","
	print "\"papers\": ["
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
	
	print "\t{"

	print "\t\t\"author\": \""authors"\","			
	print "\t\t\"title\": \""title"\","
	
	if (lncs_pages != "" && lncs_pages != "NONE" && lncs_pages != "N/A")
	{	
		print "\t\t\"proceedings_name\": \"Research in Computational Molecular Biology. Lecture Notes in Computer Science.\""
		print "\t\t\"proceedings_volume\": \""lncs_volume"\""
		print "\t\t\"proceedings_pages\": \""lncs_pages"\""
		print "\t\t\"proceedings_doi\": \""lncs_doi"\""
	}
	if (preprint != "" && preprint != "NONE" && preprint != "N/A")
	{
		temp = preprint
		if (preprint ~ /bioRxiv/) 
		{
			sub(/^bioRxiv /, "", temp)
			print "\t\t\"preprint_id\": \""preprint"\""
			print "\t\t\"preprint_doi\": \"10.1101/"temp"\""
		}
		else if (preprint ~ /arXiv/)
		{
			sub(/^arXiv:/, "arXiv.", temp)
			print "\t\t\"preprint_id\": \""preprint"\""
			print "\t\t\"preprint_doi\": \"10.48550/"temp"\""
		}
		else if (preprint ~ /hal/)
		{
			print "\t\t\"preprint_id\": \""preprint"\""
			print "\t\t\"preprint_doi\": \"hal.science/"temp"\"" # not real doi		
		}		
	}
	if (journal != "" && journal != "NONE" && journal != "N/A")
	{
		print "\t\t\"journal\": \""journal"\""
		print "\t\t\"journal_title\": \""journal_title"\""		
		if (journal_authors == "")
		{
			print "\t\t\"journal_authors\": \""authors"\""		
		}
		else
		{
			print "\t\t\"journal_authors\": \""journal_authors"\""
		}
		print "\t\t\"journal_issue_pages\": \""journal_issue_pages"\""
		print "\t\t\"journal_year\": \""journal_year"\""
		
		tmp = journal_doi
    		gsub(/\r/, "", tmp)
    		print "\t\t\"journal_doi\": \""tmp"\""
	}
	print "\t}"
}  
}

END {
	print "]\n}"
}
