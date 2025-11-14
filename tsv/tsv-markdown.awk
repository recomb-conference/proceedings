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
	# nothing
	# print "\n"
}
else
{
	print "- **"$2"**. "$1"."
	if ($3 != "" && $3 != "NONE" && $3 != "N/A")
	{
		print "  - Proceedings: Research in Computational Molecular Biology. RECOMB 2023. Lecture Notes in Computer Science, vol 13976, pp "$3", Springer, Cham."
		print "    - DOI: ["$4"](https://doi.org/"$4")"
	}
	if ($5 != "" && $5 != "NONE" && $5 != "N/A")
	{
		temp = $5
		if ($5 ~ /bioRxiv/) 
		{
			sub(/^bioRxiv /, "", temp)
			print "  - Preprint: ["$5"](https://doi.org/10.1007/"temp")"
		}
		else if ($5 ~ /arXiv/)
		{
			sub(/^arXiv:/, "arXiv.", temp)
			print "  - Preprint: ["$5"](https://doi.org/10.48550/"temp")"
		}
		else if ($5 ~ /hal/)
		{
			print "  - Preprint: ["$5"](https://inria.hal.science/"temp")"
		}		
	}
	if ($6 != "" && $6 != "NONE" && $6 != "N/A")
	{
		if ($8 == "")
		{
			print "  - Journal: **"$7"**. "$1". *"$6"*, "$9", "$10"."
		}
		else
		{
			print "  - Journal: **"$7"**. "$8". *"$6"*, "$9", "$10"."
		}
		tmp = $11
    		gsub(/\r/, "", tmp)
		print "    - DOI: ["tmp"](https://doi.org/"tmp")"		
	}
	print "\n"
}  
}
