#!/bin/bash

NAME=binutils
SPECNAME=${NAME}.spec
ARCHES="armv5tel armv6l armv7l armv7hl armv7nhl armv7tnhl mipsel i486 x86_64"

for i in ${ARCHES} ; do
# cross spec files
    cat ./${SPECNAME} | sed -e "s#Name: .*#Name: cross-${i}-${NAME}#" > ./cross-${i}-${NAME}.spec
done

exit 0
