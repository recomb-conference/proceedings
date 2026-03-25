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
	print "\"title\": \"24th Annual International Conference on Research in Computational Molecular Biology\","
	print "\"location\": \"xx, yy\","
	print "\"dates\": \"June 22-25, 2020\","
	print "\"editor\": \"pc chair\","
	print "\"website\": \"https://recomb.org/recomb2022/\","
	print "\"proceedings\": \"https://recomb.org/proceedings/2020-2016/2020/\","
	print "\"papers\":"
    	print "["
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
	
	print "\t{"

	print "\t\t\"author\": \""authors"\","			
	print "\t\t\"title\": \""title"\","

	if (preprint != "" && preprint != "NONE" && preprint != "N/A")
	{
		temp = preprint
		if (preprint ~ /bioRxiv/) 
		{
			sub(/^bioRxiv /, "", temp)
			print "\t\t\"preprint_id\": \""preprint"\","
			print "\t\t\"preprint_doi\": \""doi_head"/"temp"\","
		}
		else if (preprint ~ /arXiv/)
		{
			sub(/^arXiv:/, "arXiv.", temp)
			print "\t\t\"preprint_id\": \""preprint"\","
			print "\t\t\"preprint_doi\": \""doi_head"/"temp"\","
		}
		else if (preprint ~ /medRxiv/)
		{
			sub(/^medRxiv /, "", temp)
			print "\t\t\"preprint_id\": \""preprint"\","
			print "\t\t\"preprint_doi\": \""doi_head"/"temp"\","
		}
		else if (preprint ~ /hal/)
		{
			print "\t\t\"preprint_id\": \""preprint"\","
			print "\t\t\"preprint_doi\": \"hal.science/"temp"\"," # not real doi		
		}		
	}
	if (journal != "" && journal != "NONE" && journal != "N/A")
	{
		print "\t\t\"journal\": \""journal"\","
		gsub(/^[ \t]+|[ \t]+$/, "", journal_title)
		print "\t\t\"journal_title\": \""journal_title"\","		
		if (journal_authors == "")
		{
			print "\t\t\"journal_authors\": \""authors"\","		
		}
		else
		{
			print "\t\t\"journal_authors\": \""journal_authors"\","
		}
		print "\t\t\"journal_issue_pages\": \""journal_issue_pages"\","
		print "\t\t\"journal_year\": \""journal_year"\","
		
		tmp = journal_doi
    		gsub(/\r/, "", tmp)
    		print "\t\t\"journal_doi\": \""tmp"\","
	}
	print "\t},"
}  
}

END {
	print "]\n}"
}
