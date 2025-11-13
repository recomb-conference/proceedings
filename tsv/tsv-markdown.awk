{
	print "- **"$2"**. "$1"."
	print "  - Proceedings: Research in Computational Molecular Biology. RECOMB 2023. Lecture Notes in Computer Science, vol 13976, pp "$3", Springer, Cham."
	print "    - DOI: ["$4"](https://doi.org/"$4")"
	if ($5 != "")
	{
		temp = $5
		sub(/^bioRxiv /, "", temp)
		print "  - Preprint: ["$5"](https://doi.org/"temp")"
	}
	if ($6 != "NONE")
	{
		print "  - Journal: **"$7"**. *"$6"*, "$8", "$9"."
		print "    - DOI: ["$10"](https://doi.org/"$10")"		
	}
	print "\n"
}
