BEGIN {
    inside=0
    printf("- path: %s\n  frontmatter:\n", pathname)
}
{
    if($0 ~ /^---$/)
        if(inside)
            exit 0
        else {
            if(NR>1) exit 0
            inside=1
        }
    else
        if(inside) print "    " $0
}
END {}