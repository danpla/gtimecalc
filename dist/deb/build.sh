#!/bin/sh

APPNAME='gtimecalc'
DATA_DIR='../..'

BUILD_DIR=build
mkdir -p $BUILD_DIR

mkdir -p $BUILD_DIR/usr
cp -r $DATA_DIR/bin $BUILD_DIR/usr

INSTALL_DIR=$BUILD_DIR/usr/share

mkdir -p $INSTALL_DIR
rsync -a --exclude=*__pycache__* $DATA_DIR/$APPNAME $INSTALL_DIR


# Compile mo
grep -v '^#' $DATA_DIR/po/LINGUAS | while read -r lang;
  do
    modir=$INSTALL_DIR/locale/$lang/LC_MESSAGES;
    mkdir -p $modir;
    msgfmt $DATA_DIR/po/$lang.po -o $modir/$APPNAME.mo;
  done

# Icons
ICON_DIR=$INSTALL_DIR/icons
mkdir -p $ICON_DIR
rsync -a --exclude=*x*/*/*.svg $DATA_DIR/data/icons/hicolor $ICON_DIR

# Desktop file
DESKTOP_DIR=$INSTALL_DIR/applications
mkdir -p $DESKTOP_DIR
cp $DATA_DIR/data/$APPNAME.desktop $DESKTOP_DIR

# Docs
DOC_DIR=$INSTALL_DIR/doc/$APPNAME
mkdir -p $DOC_DIR

cp $DATA_DIR/LICENSE $DOC_DIR/copyright

cp $DATA_DIR/doc/manual.md $DOC_DIR/README
gzip -9 $DOC_DIR/README

cp $DATA_DIR/CHANGELOG.md $DOC_DIR/changelog
gzip -9 $DOC_DIR/changelog

cp changelog $DOC_DIR/changelog.Debian
gzip -9 $DOC_DIR/changelog.Debian


# DEBIAN
DEB_DIR=$BUILD_DIR/DEBIAN
mkdir -p $DEB_DIR

cp postinst prerm $DEB_DIR
cp control.in $DEB_DIR/control

set -- `cd $DATA_DIR/$APPNAME; python3 -B -c \
  'from app_info import *; print(VERSION, WEBSITE)'`
version=$1
website=$2
size=`find $BUILD_DIR -type f -not -path "$DEB_DIR/*" -print0 |
  xargs -r0 du --apparent-size -chk | tail -n -1 | awk '{print $1}'`

sed \
  -e "s/@VERSION@/$version/" \
  -e "s/@SIZE@/$size/" \
  -e "s,@URL@,$website," \
  -i $DEB_DIR/control


chmod -R u+rwX,go+rX,go-w $BUILD_DIR
chmod +x $DEB_DIR/postinst $DEB_DIR/prerm $BUILD_DIR/usr/bin/$APPNAME


fakeroot dpkg-deb --build $BUILD_DIR .

rm -rf $BUILD_DIR
