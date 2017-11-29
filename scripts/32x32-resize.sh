#!/bin/sh

INDIR=$1
OUTDIR=$2
SIZE=32x32

mkdir -p $OUTDIR

FILES=$(cd $INDIR; find . -type f)

for attr in pure passion cool
do
    for r in 1 2 3 4 5
    do
	mkdir -p $OUTDIR/$attr/$r
    done
done

for fname in $FILES
do
    convert $INDIR/$fname -resize $SIZE \
	\( +clone -alpha opaque -fill white -colorize 100% \) +swap \
	-geometry +0+0 -compose Over -composite -alpha off \
	-gravity center -extent $SIZE \
	 $OUTDIR/$fname
done
