%define binutils_target %{_target_platform}
%define isnative 1
%define enable_shared 1
%define run_testsuite 0

Summary: A GNU collection of binary utilities
Name: binutils
Version: 2.32
Release: 1
License: GPLv3+
Group: Development/Tools
URL: http://sources.redhat.com/binutils
Source: ftp://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.bz2
Source2: binutils-2.19.50.0.1-output-format.sed
Source200: precheckin.sh
Source201: README.PACKAGER

#----------------------------------------------------------------------------
# Patched from Fedora
#
# Purpose:  Use /lib64 and /usr/lib64 instead of /lib and /usr/lib in the
#           default library search path of 64-bit targets.
# Lifetime: Permanent, but it should not be.  This is a bug in the libtool
#           sources used in both binutils and gcc, (specifically the
#           libtool.m4 file).  These are based on a version released in 2009
#           (2.2.6?) rather than the latest version.  (Definitely fixed in
#           libtool version 2.4.6).
Patch1: binutils-2.20.51.0.2-libtool-lib64.patch

# Omit some RHEL/Fedora specific patches

# Purpose:  Disable an x86/x86_64 optimization that moves functions from the
#           PLT into the GOTPLT for faster access.  This optimization is
#           problematic for tools that want to intercept PLT entries, such
#           as ltrace and LD_AUDIT.  See BZs 1452111 and 1333481.
# Lifetime: Permanent.  But it should not be.
# FIXME:    Replace with a configure time option.
Patch6: binutils-2.29-revert-PLT-elision.patch

# Purpose:  Changes readelf so that when it displays extra information about
#           a symbol, this information is placed at the end of the line.
# Lifetime: Permanent.
# FIXME:    The proper fix would be to update the scripts that are expecting
#           a fixed output from readelf.  But it seems that some of them are
#           no longer being maintained.
Patch7: binutils-readelf-other-sym-info.patch

# Purpose:  Do not create PLT entries for AARCH64 IFUNC symbols referenced in
#           debug sections.
# Lifetime: Permanent.
# FIXME:    Find related bug.  Decide on permanency.
Patch8: binutils-2.27-aarch64-ifunc.patch

# Purpose:  Stop the binutils from statically linking with libstdc++.
# Lifetime: Permanent.
Patch9: binutils-do-not-link-with-static-libstdc++.patch

# Purpose:  Add a .attach_to_group pseudo-op to the assembler for
#           use by the annobin gcc plugin.
# Lifetime: Permanent.
Patch10: binutils-attach-to-group.patch

# Purpose:  Stop gold from complaining about relocs in the .gnu.build.attribute
#           section that reference symbols in discarded sections.
# Lifetime: Fixed in 2.33 (maybe)
Patch11: binutils-gold-ignore-discarded-note-relocs.patch

# Purpose:  Allow OS specific sections in section groups.
# Lifetime: Might be fixed in 2.33
Patch12: binutils-special-sections-in-groups.patch

# Purpose:  Fix linker testsuite failures.
# Lifetime: Fixed in 2.33 (possibly)
Patch13: binutils-fix-testsuite-failures.patch

# Purpose:  Improve objdump's handling of corrupt input files.
# Lifetime: Fixed in 2.33
Patch14: binutils-CVE-2019-9073.patch

# Purpose:  Stop illegal memory access parsing corrupt PE files.
# Lifetime: Fixed in 2.33
Patch15: binutils-CVE-2019-9074.patch

# Purpose:  Stop illegal memory access parsing corrupt archives.
# Lifetime: Fixed in 2.33
Patch16: binutils-CVE-2019-9075.patch

# Purpose:  Stop illegal memory access parsing a corrupt MIPS binary.
# Lifetime: Fixed in 2.33
Patch17: binutils-CVE-2019-9077.patch

# Purpose:  Stop a seg-fault when disassembling an EFI binary.
# Lifetime: Fixed in 2.33
Patch18: binutils-disassembling-efi-files.patch

# Patch from Suse
Patch19: binutils-2.32-asneeded.patch

# MIPS gold support is not working as far as we know. The configure
# --enable-gold seems to be a no-op so it's left in to make it easier
# to fix when gold is supported in MIPS.
%define has_gold 1
%ifarch mips mipsel
%define has_gold 0
%endif
%if "%{name}" == "cross-mipsel-binutils"
%define has_gold 0
%endif

%if "%{name}" != "binutils"
%if "%{name}" != "cross-mipsel-binutils" && "%{name}" != "cross-i486-binutils" && "%{name}" != "cross-x86_64-binutils" && "%{name}" != "cross-aarch64-binutils"
%define binutils_target %(echo %{name} | sed -e "s/cross-\\(.*\\)-binutils/\\1/")-meego-linux-gnueabi
%else
%define binutils_target %(echo %{name} | sed -e "s/cross-\\(.*\\)-binutils/\\1/")-meego-linux-gnu
%endif
%define _prefix /opt/cross
%define enable_shared 0
%define isnative 0
%define run_testsuite 0
%define cross %{binutils_target}-
# single target atm.
ExclusiveArch: %ix86 x86_64
%endif

# Docs requirements
BuildRequires: texinfo >= 4.0, gettext, flex, bison, zlib-devel

# Required for: ld-bootstrap/bootstrap.exp bootstrap with --static
# It should not be required for: ld-elf/elf.exp static {preinit,init,fini} array
%if %{run_testsuite}
BuildRequires: dejagnu, zlib-static, glibc-static, sharutils
%endif
BuildRequires: elfutils-libelf-devel
Conflicts: gcc-c++ < 4.0.0

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%define _gnu %{nil}
%endif

%description
Binutils is a collection of binary utilities, including ar (for
creating, modifying and extracting from archives), as (a family of GNU
assemblers), gprof (for displaying call graph profile data), ld (the
GNU linker), nm (for listing symbols from object files), objcopy (for
copying and translating object files), objdump (for displaying
information from object files), ranlib (for generating an index for
the contents of an archive), readelf (for displaying detailed
information about binary files), size (for listing the section sizes
of an object or archive file), strings (for listing printable strings
from files), strip (for discarding symbols), and addr2line (for
converting addresses to file and line).

%package devel
Summary: BFD and opcodes static libraries and header files
Group: System/Libraries
Requires: zlib-devel
Requires: %{name} = %{version}-%{release}

%description devel
This package contains BFD and opcodes static libraries and associated
header files.  Only *.a libraries are included, because BFD doesn't
have a stable ABI.  Developers starting new projects are strongly encouraged
to consider using libelf instead of BFD.

%package doc
Summary: Documentation for %{name}
Group:   Documentation
Requires: %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description doc
Man and info pages for %{name}.

%prep
%setup -q -n %{name}-%{version}/upstream
%autopatch -p1

# For this package, autotools are really only intended to be run by maintainers.
# The configure script is maintained in the repo by them for packaging.

# On ppc64 we might use 64KiB pages
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc
# LTP sucks
perl -pi -e 's/i\[3-7\]86/i[34567]86/g' */conf*
sed -i -e 's/%''{release}/%{release}/g' bfd/Makefile{.am,.in}
sed -i -e '/^libopcodes_la_\(DEPENDENCIES\|LIBADD\)/s,$, ../bfd/libbfd.la,' opcodes/Makefile.{am,in}
# Build libbfd.so and libopcodes.so with -Bsymbolic-functions if possible.
if gcc %{optflags} -v --help 2>&1 | grep -q -- -Bsymbolic-functions; then
sed -i -e 's/^libbfd_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' bfd/Makefile.{am,in}
sed -i -e 's/^libopcodes_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' opcodes/Makefile.{am,in}
fi
# $PACKAGE is used for the gettext catalog name.
sed -i -e 's/^ PACKAGE=/ PACKAGE=%{?cross}/' */configure
# Undo the name change to run the testsuite.
for tool in binutils gas ld
do
  sed -i -e "2aDEJATOOL = $tool" $tool/Makefile.am
  sed -i -e "s/^DEJATOOL = .*/DEJATOOL = $tool/" $tool/Makefile.in
done
touch */configure


%build

echo target is %{binutils_target}
export CFLAGS="$RPM_OPT_FLAGS"
CARGS=

%if %{isnative}
case %{binutils_target} in i?86*|aarch64*)
  CARGS="$CARGS --enable-64-bit-bfd"
  ;;
esac
case %{binutils_target} in x86_64*|i?86*|aarch64*)
  CARGS="$CARGS --enable-targets=x86_64-pep"
  ;;
esac
%endif

%if 0%{?_with_debug:1}
CFLAGS="$CFLAGS -O0 -ggdb2"
%define enable_shared 0
%endif

# We could optimize the cross builds size by --enable-shared but the produced
# binaries may be less convenient in the embedded environment.
./configure \
  --build=%{_target_platform} --host=%{_target_platform} \
  --target=%{binutils_target} --prefix=%{_exec_prefix} \
%if !%{isnative} 
  --enable-targets=%{_host} \
  --with-sysroot=%{_prefix}/%{binutils_target}/sys-root \
  --program-prefix=%{cross} \
%endif
%if %{enable_shared}
  --enable-shared \
%else
  --disable-shared \
%endif
  $CARGS \
  --enable-gold \
  --enable-deterministic-archives \
  --disable-werror \
  --enable-lto \
  --enable-relro \
  --with-bugurl=http://bugs.merproject.org
make %{_smp_mflags} tooldir=%{_prefix} all
make %{_smp_mflags} tooldir=%{_prefix} info

# Do not use %%check as it is run after %%install where libbfd.so is rebuild
# with -fvisibility=hidden no longer being usable in its shared form.
%if !%{run_testsuite}
echo ====================TESTSUITE DISABLED=========================
%else
make -k check < /dev/null || :
echo ====================TESTING=========================
cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
echo ====================TESTING END=====================
for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
do
  ln $file binutils-%{_target_platform}-$(basename $file) || :
done
tar cjf binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
uuencode binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}.tar.bz2
rm -f binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
%endif

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
%if %{isnative}
make prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info

# Rebuild libiberty.a with -fPIC.
# Future: Remove it together with its header file, projects should bundle it.
make -C libiberty clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libiberty

# Rebuild libbfd.a with -fPIC.
# Without the hidden visibility the 3rd party shared libraries would export
# the bfd non-stable ABI.
make -C bfd clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS -fvisibility=hidden" -C bfd

# Rebuild libopcodes.a with -fPIC.
%make_build -C opcodes clean
%make_build CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C opcodes

install -m 644 bfd/libbfd.a %{buildroot}%{_libdir}
install -m 644 libiberty/libiberty.a %{buildroot}%{_libdir}
install -m 644 include/libiberty.h %{buildroot}%{_includedir}
install -m 644 include/demangle.h %{buildroot}%{_includedir}
# Remove Windows/Novell only man pages
rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres}*

%if %{enable_shared}
chmod +x %{buildroot}%{_libdir}/lib*.so*
%endif

# Prevent programs to link against libbfd and libopcodes dynamically,
# they are changing far too often
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.la

%if "%{__isa_bits}" == "64"
# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_includedir}/bfd.h
%endif
# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
%ifarch %{ix86} x86_64 
sed -i -e '/^#include "ansidecl.h"/{p;s~^.*$~#include <bits/wordsize.h>~;}' \
    -e 's/^#define BFD_DEFAULT_TARGET_SIZE \(32\|64\) *$/#define BFD_DEFAULT_TARGET_SIZE __WORDSIZE/' \
    -e 's/^#define BFD_HOST_64BIT_LONG [01] *$/#define BFD_HOST_64BIT_LONG (__WORDSIZE == 64)/' \
    -e 's/^#define BFD_HOST_64_BIT \(long \)\?long *$/#if __WORDSIZE == 32\
#define BFD_HOST_64_BIT long long\
#else\
#define BFD_HOST_64_BIT long\
#endif/' \
    -e 's/^#define BFD_HOST_U_64_BIT unsigned \(long \)\?long *$/#define BFD_HOST_U_64_BIT unsigned BFD_HOST_64_BIT/' \
    %{buildroot}%{_includedir}/bfd.h
%endif
touch -r bfd/bfd-in2.h %{buildroot}%{_includedir}/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE2}")"

tee %{buildroot}%{_libdir}/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz dependency is unexpected by legacy build scripts.  */
INPUT ( %{_libdir}/libbfd.a -liberty -lz )
EOH

tee %{buildroot}%{_libdir}/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd )
EOH

%else # !%{isnative}
# For cross-binutils we drop the documentation.
rm -rf %{buildroot}%{_infodir}
# We keep these as one can have native + cross binutils of different versions.
#rm -rf %{buildroot}%{_datadir}/locale
#rm -rf %{buildroot}%{_mandir}
rm -rf %{buildroot}%{_libdir}/libiberty.a
%endif # !%{isnative}

# This one comes from gcc
rm -f %{buildroot}%{_infodir}/dir
rm -rf %{buildroot}%{_prefix}/%{binutils_target}

%find_lang %{?cross}binutils
%find_lang %{?cross}opcodes
%find_lang %{?cross}bfd
%find_lang %{?cross}gas
%find_lang %{?cross}ld
%find_lang %{?cross}gprof
%if %{has_gold}
%find_lang %{?cross}gold
cat %{?cross}gold.lang >> %{?cross}binutils.lang
%endif
cat %{?cross}opcodes.lang >> %{?cross}binutils.lang
cat %{?cross}bfd.lang >> %{?cross}binutils.lang
cat %{?cross}gas.lang >> %{?cross}binutils.lang
cat %{?cross}ld.lang >> %{?cross}binutils.lang
cat %{?cross}gprof.lang >> %{?cross}binutils.lang

# move doc files
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 README %{buildroot}%{_docdir}/%{name}-%{version}

%clean
rm -rf %{buildroot}

%if %{isnative}
%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post doc
%install_info --info-dir=%{_infodir} %{_infodir}/as.info
%install_info --info-dir=%{_infodir} %{_infodir}/binutils.info
%install_info --info-dir=%{_infodir} %{_infodir}/gprof.info
%install_info --info-dir=%{_infodir} %{_infodir}/ld.info
%install_info --info-dir=%{_infodir} %{_infodir}/standards.info
%install_info --info-dir=%{_infodir} %{_infodir}/configure.info
%install_info --info-dir=%{_infodir} %{_infodir}/bfd.info
exit 0

%preun doc
if [ $1 = 0 ] ;then
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/as.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/ld.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/standards.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/configure.info
  %install_info --delete --info-dir=%{_infodir} %{_infodir}/bfd.info
fi
exit 0

%endif # %{isnative}

%files -f %{?cross}binutils.lang
%defattr(-,root,root,-)
%license COPYING3
%{_bindir}/*
%{_datadir}/gdb/syscalls/*.xml
%{_datadir}/gdb/syscalls/*.dtd
%{_datadir}/gdb/system-gdbinit/*.py*
%if %{enable_shared}
%{_libdir}/lib*.so
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%endif

%if "%{name}" == "cross-i486-binutils"
%exclude %{_includedir}/*
%exclude %{_libdir}/*.a
%exclude %{_libdir}/*.la
%endif

%files doc
%defattr(-,root,root,-)
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/man1/*
%{_mandir}/man5/*
%if %{isnative}
%{_infodir}/*info*
%endif

%if %{isnative}
%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.so
%{_libdir}/lib*.a
%endif # %{isnative}
