BEGIN {
    FS = "\": \"| \",|\",| {|\" : \""
    print "%% RECOMB 2025 BibTeX Entries\n"
}

# Identify the start of a paper object
/\{/ {
    is_paper = 1
    delete paper
}

# Capture keys and values
/\"[a-z_]+\":/ {
    # Clean up the key and value from the line
    gsub(/^[ \t]+\"/, "", $1)
    gsub(/\"$/, "", $1)
    key = $1
    
    val = $2
    gsub(/^ /, "", val)
    gsub(/\",?$/, "", val)
    
    paper[key] = val
}

# Identify the end of a paper object and print entry
/\}/ {
    if (paper["title"] != "" && paper["author"] != "") {
        # Generate a unique citation key: FirstAuthorYear
        split(paper["author"], authors, ",")
        split(authors[1], name, " ")
        citekey = tolower(name[length(name)]) paper["journal_year"] ? paper["journal_year"] : "2025"
        
        # Decide if it is @article (journal) or @inproceedings (conference)
        if (paper["journal"] != "") {
            print "@article{" citekey "_" substr(paper["proceedings_doi"], length(paper["proceedings_doi"])-1) ","
            print "  author = {" paper["author"] "},"
            print "  title = {" paper["title"] "},"
            print "  journal = {" paper["journal"] "},"
            print "  year = {" paper["journal_year"] "},"
            print "  volume = {" paper["journal_issue_pages"] "},"
            print "  doi = {" paper["journal_doi"] "}"
        } else {
            print "@inproceedings{" citekey "_" substr(paper["proceedings_doi"], length(paper["proceedings_doi"])-1) ","
            print "  author = {" paper["author"] "},"
            print "  title = {" paper["title"] "},"
            print "  booktitle = {" paper["proceedings_name"] "},"
            print "  year = {2025},"
            print "  pages = {" paper["proceedings_pages"] "},"
            print "  doi = {" paper["proceedings_doi"] "}"
        }
        print "}\n"
    }
    delete paper
}
