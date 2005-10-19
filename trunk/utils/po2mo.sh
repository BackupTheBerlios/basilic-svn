#!/bin/sh

# Usage : 
# $ po2mo i18ndomain podir modir
# i18ndomain is the i18n domain (ex : plone)
# podir is where this script will (recursively) find po files
# modir needs to be a "locales" dir, needed directory will be built there

domain=$1
echo -e "Converting all po files concerning $domain domain, from $2 to $3"

for file in `find "$2" -name "$domain-*.po"`; do
    filename=`basename $file`
    language=`echo "$filename" | sed 's/'$domain'-//'`
    language=`echo "$language" | sed 's/\.po$//'`
    out=`echo "$filename" | sed 's/\.po$/.mo/'`
    outdir=$3/$language/LC_MESSAGES/
    mkdir -p $outdir
    echo -e "   Generating into $outdir"
    msgfmt -o "$outdir/$lang/$domain.mo" "$file" 2> /dev/null
done

