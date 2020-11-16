# lz4 is used by systemd, libsystemd is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 1

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%bcond_without pgo

Name:		lz4
Version:	1.9.3
Release:	1
Summary:	Extremely fast compression algorithm
Group:		Archiving/Compression
License:	GPLv2+ and BSD
URL:		http://www.lz4.org/
Source0:	https://github.com/lz4/lz4/archive/v%{version}.tar.gz
BuildRequires:	glibc-devel

%description
LZ4 is an extremely fast loss-less compression algorithm, providing compression
speed at 400 MB/s per core, scalable with multi-core CPU. It also features
an extremely fast decoder, with speed in multiple GB/s per core, typically
reaching RAM speed limits on multi-core systems.

%define devname %{mklibname -d %{name}}
%define dev32name lib%{name}-devel

%package -n %{devname}
Summary:	Development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname lz4 %{major}}

%description -n %{devname}
This package contains the header(.h) and library(.so) files required to build
applications using liblz4 library.

%define static %{mklibname -d -s %{name}}
%define static32 lib%{name}-static-devel

%package -n %{static}
Summary:	Static development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname -d lz4}

%description -n %{static}
This package contains the static library files to statically link against the
liblz4 library.

%if %{with compat32}
%define lib32name lib%{name}%{major}
%package -n %{lib32name}
Summary:	LZ4 compression library (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
LZ4 compression library (32-bit)

%files -n %{lib32name}
%{_prefix}/lib/lib%{name}.so.%{major}*

%package -n %{dev32name}
Summary:	Development files for the LZ4 compression library (32-bit)
Group:		Development/C
Requires:	%{devname} = %{EVRD}
Requires:	%{lib32name} = %{EVRD}

%description -n %{dev32name}
Development files for the LZ4 compression library (32-bit)

%files -n %{dev32name}
%{_prefix}/lib/lib%{name}.so
%{_prefix}/lib/pkgconfig/*.pc

%package -n %{static32}
Summary:	Static development library for lz4 (32-bit)
Group:		Development/C
License:	BSD
Requires:	%{dev32name} = %{EVRD}

%description -n %{static32}
This package contains the static library files to statically link against the
liblz4 library.

%files -n %{static32}
%{_prefix}/lib/*.a
%endif

%prep
%autosetup -p1
echo '#!/bin/sh' > ./configure
chmod +x ./configure

for i in $(grep -rl "\-m32");do sed -i 's!-m32!!g' $i;done

%build
%setup_compile_flags

%if %{with compat32}
mkdir build32
cp -a $(ls -1 |grep -v build32) build32
cd build32
CFLAGS="$(echo %{optflags} |sed -e 's,-m64,,g;s,-flto,,g') -m32" \
CXXFLAGS="$(echo %{optflags} |sed -e 's,-m64,,g;s,-flto,,g') -m32" \
LDFLAGS="$(echo %{ldflags} |sed -e 's,-m64,,g;s,-flto,,g') -m32" \
%make_build CC="gcc -m32" CXX="g++ -m32" LD="gcc -m32" all VERBOSE=1
cd ..
%endif

%if %{with pgo}
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" \
%make_build CC=%{__cc} programs all VERBOSE=1

./tests/fullbench -c ./lib/lz4.c
./tests/fullbench -d ./lib/lz4.c

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile $(find . -type f -name "*.profile.d")
make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%make_build CC=%{__cc} programs all VERBOSE=1

%install
%if %{with compat32}
cd build32
%make_install PREFIX=%{_prefix} LIBDIR=%{_prefix}/lib CC="gcc -m32" LDFLAGS="%{ldflags} -m32" mandir="%{_mandir}"
rm -rf %{buildroot}%{_bindir}/* %{buildroot}%{_mandir}
cd ..
%endif
%make_install PREFIX=%{_prefix} LIBDIR=%{_libdir} CC=%{__cc} LDFLAGS="%{ldflags}" mandir="%{_mandir}"

%files
%doc NEWS
%{_bindir}/lz4
%{_bindir}/lz4c
%{_bindir}/lz4cat
%{_bindir}/unlz4
%{_mandir}/man1/*lz4*.1*

%{libpackage %{name} %{major}}

%files -n %{devname}
%doc lib/LICENSE
%{_includedir}/*.h
%{_libdir}/liblz4.so
%{_libdir}/pkgconfig/liblz4.pc

%files -n %{static}
%{_libdir}/liblz4.a
