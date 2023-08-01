%define binutils_target %{_target_platform}
%define isnative 1
%define enable_shared 1
%define run_testsuite 0
# Default: build binutils-gprofng package.
%bcond_without gprofng

Summary: A GNU collection of binary utilities
Name: binutils
Version: 2.41
Release: 1
License: GPLv3+
URL: https://github.com/sailfishos/binutils
Source: %{name}-%{version}.tar.bz2
Source1: binutils_2.41-1ubuntu1.debian.tar.gz
Source2: binutils-2.19.50.0.1-output-format.sed
Source200: precheckin.sh
Source201: README.PACKAGER
Patch2: binutils-2.32-asneeded.patch

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

%ifnarch %{ix86} x86_64 aarch64
%undefine with_gprofng
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
# Disable gprofng for cross builds
%undefine with_gprofng
%define cross %{binutils_target}-
# single target atm.
ExclusiveArch: %ix86 x86_64
%endif

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
Requires: zlib-devel
Requires: %{name} = %{version}-%{release}

%description devel
This package contains BFD and opcodes static libraries and associated
header files.  Only *.a libraries are included, because BFD doesn't
have a stable ABI.  Developers starting new projects are strongly encouraged
to consider using libelf instead of BFD.

%package doc
Summary: Documentation for %{name}
Requires: %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description doc
Man and info pages for %{name}.

%if %{with gprofng}
%package gprofng
Summary: Next Generating code profiling tool
Provides: gprofng = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

%description gprofng
Gprofng is the GNU Next Generation profiler for analyzing the performance
of Linux applications.  Gprofng allows you to:
%endif

%prep
%setup -q -n %{name}-%{version}/upstream
tar xfz %{SOURCE1}
sed -i 's|^001_ld_makefile_patch.patch$||g' debian/patches/series
cat debian/patches/series | grep -v ^# | grep -v ^$ | while read line
do
  echo "Using patch: $line"
  patch -p1 -i debian/patches/$line
done

%patch2 -p1 -b .asneeded
# From here on this is based on Fedora's build

# For this package, autotools are really only intended to be run by maintainers.
# The configure script is maintained in the repo by them for packaging.

# On ppc64 we might use 64KiB pages

# Fedora uses 64KiB page sizes on aarch64 and ppc.
# This means even simple hello world type programs are 64KiB+ in size.
# In order to save a decent amount of space in images use the default 4KiB
# page sizes aarch64. Arch Linux for example also uses 4KiB page sizes
# for aarch64.
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
# sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
# sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc
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
%configure \
  --build=%{_target_platform} --host=%{_target_platform} \
  --target=%{binutils_target} \
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
  --enable-plugins \
  --enable-deterministic-archives \
  --disable-werror \
  --disable-gdb \
  --disable-gdbserver \
%if %{with gprofng}
  --enable-gprofng=yes \
%else
  --enable-gprofng=no \
%endif
  --disable-readline \
  --disable-sim \
  --disable-libdecnumber \
  --enable-lto \
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

# Rebuild libsframe.a with -fPIC.
%make_build -s -C libsframe clean
%set_build_flags
%make_build -s CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libsframe

install -m 644 bfd/.libs/libbfd.a %{buildroot}%{_libdir}
install -m 644 libiberty/libiberty.a %{buildroot}%{_libdir}
install -m 644 include/libiberty.h %{buildroot}%{_includedir}
install -m 644 include/demangle.h %{buildroot}%{_includedir}
install -m 644 libsframe/.libs/libsframe.a %{buildroot}%{_libdir}

# Remove Windows/Novell only man pages
rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres}*

%if %{enable_shared}
chmod +x %{buildroot}%{_libdir}/lib*.so*
%endif

# Prevent programs to link against libbfd and libopcodes dynamically,
# they are changing far too often
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/*.la

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

/* The libz & libsframe dependencies are unexpected by legacy build scripts.  */
/* The libdl dependency is for plugin support.  (BZ 889134)  */
INPUT ( %{_libdir}/libbfd.a %{_libdir}/libsframe.a -liberty -lz -ldl )
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
# Include all the bin tools explictly so build fails when they change
%{_bindir}/%{?cross}addr2line
%{_bindir}/%{?cross}ar
%{_bindir}/%{?cross}as
%{_bindir}/%{?cross}c++filt
%{_bindir}/%{?cross}dwp
%{_bindir}/%{?cross}elfedit
%{_bindir}/%{?cross}gprof
%{_bindir}/%{?cross}ld
%{_bindir}/%{?cross}ld.bfd
%{_bindir}/%{?cross}ld.gold
%{_bindir}/%{?cross}nm
%{_bindir}/%{?cross}objcopy
%{_bindir}/%{?cross}objdump
%{_bindir}/%{?cross}ranlib
%{_bindir}/%{?cross}readelf
%{_bindir}/%{?cross}size
%{_bindir}/%{?cross}strings
%{_bindir}/%{?cross}strip
%if %{enable_shared}
%{_libdir}/lib*.so
%{_libdir}/libctf*so.*
%if %{with gprofng}
%{_libdir}/libgprofng.so.*
%endif
%{_libdir}/libsframe*so.*
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%{_libdir}/bfd-plugins/libdep.so
%endif

%if !%{isnative}
%exclude %{_includedir}/*
%exclude %{_libdir}/*.a
%exclude %{_libdir}/*.la
%exclude %{_libdir}/bfd-plugins/*.a
%endif

%files doc
%defattr(-,root,root,-)
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/man1/*
%exclude %{_mandir}/man1/gp-*
%exclude %{_mandir}/man1/gprofng*
%if %{isnative}
%{_infodir}/*info*
%endif

%if %{isnative}
%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/libbfd.so
%if %{with gprofng}
%{_libdir}/libgprofng.so
%endif
%{_libdir}/libopcodes.so
%{_libdir}/lib*.a
%endif # %{isnative}

%if %{with gprofng}
%files gprofng
%{_bindir}/gp-*
%{_bindir}/gprofng
%{_mandir}/man1/gp-*
%{_mandir}/man1/gprofng*
%{_infodir}/gprofng.info.*
%dir %{_libdir}/gprofng
%{_libdir}/gprofng/*
%{_sysconfdir}/gprofng.rc
%endif
