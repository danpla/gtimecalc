#!/bin/sh

APPNAME='gtimecalc'

cp ../data/$APPNAME.desktop $APPNAME.desktop.in
sed -e '/Comment\[/ d' \
    -e 's/Comment/_Comment/' \
    -i $APPNAME.desktop.in
intltool-extract --quiet --type=gettext/ini $APPNAME.desktop.in


xgettext --files-from=POTFILES.in --from-code=UTF-8 -c \
    -D.. -D. --output=$APPNAME.pot --keyword=N_ $APPNAME.desktop.in.h

for f in *.po;
do
    echo $f
    msgmerge -q --update --no-fuzzy-matching --backup=off $f $APPNAME.pot;
done


intltool-merge --quiet --desktop-style \
    . $APPNAME.desktop.in ../data/$APPNAME.desktop
rm -f $APPNAME.desktop.in.h
rm -f $APPNAME.desktop.in
