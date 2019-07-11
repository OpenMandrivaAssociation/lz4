%define major 1

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%bcond_without pgo

Name:		lz4
Version:	1.9.1
Release:	2
Summary:	Extremely fast compression algorithm
Group:		Archiving/Compression
License:	GPLv2+ and BSD
URL:		http://www.lz4.org/
Source0:	https://github.com/lz4/lz4/archive/%{name}-%{version}.tar.gz
BuildRequires:	glibc-devel

%description
LZ4 is an extremely fast loss-less compression algorithm, providing compression
speed at 400 MB/s per core, scalable with multi-core CPU. It also features
an extremely fast decoder, with speed in multiple GB/s per core, typically
reaching RAM speed limits on multi-core systems.


%define devname %{mklibname -d %{name}}

%package -n %{devname}
Summary:	Development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname lz4 %{major}}

%description -n %{devname}
This package contains the header(.h) and library(.so) files required to build
applications using liblz4 library.

%define static %{mklibname -d -s %{name}}

%package -n %{static}
Summary:	Static development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname -d lz4}

%description -n %{static}
This package contains the static library files to statically link against the
liblz4 library.

%prep
%autosetup -p1
echo '#!/bin/sh' > ./configure
chmod +x ./configure

for i in $(grep -rl "\-m32");do sed -i 's!-m32!!g' $i;done

%build
%setup_compile_flags
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
[ ! -s ./test/*.profile.d ] && printf '%s\n' 'profile is empty' && exit 1
llvm-profdata merge --output=%{name}.profile ./test/*.profile.d
make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%make_build CC=%{__cc} programs all VERBOSE=1

%install
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
