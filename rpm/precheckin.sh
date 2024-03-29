#!/bin/bash

NAME=binutils
SPECNAME=${NAME}.spec
ARCHES="armv7hl i486 x86_64 aarch64"

for i in ${ARCHES} ; do
# cross spec files
    cat ./${SPECNAME} | sed -e "s#Name: .*#Name: cross-${i}-${NAME}#" > ./cross-${i}-${NAME}.spec
done

exit 0
