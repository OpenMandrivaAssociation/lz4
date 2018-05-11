%define	major	1

Name:		lz4
Version:	1.8.2
Release:	1
Summary:	Extremely fast compression algorithm
Group:		Archiving/Compression
License:	GPLv2+ and BSD
URL:		http://www.lz4.org/
Source0:	https://github.com/lz4/lz4/archive/v%{version}.tar.gz

%description
LZ4 is an extremely fast loss-less compression algorithm, providing compression
speed at 400 MB/s per core, scalable with multi-core CPU. It also features
an extremely fast decoder, with speed in multiple GB/s per core, typically
reaching RAM speed limits on multi-core systems.


%define	devname	%{mklibname -d %{name}}

%package -n	%{devname}
Summary:	Development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname lz4 %{major}}

%description -n	%{devname}
This package contains the header(.h) and library(.so) files required to build
applications using liblz4 library.

%define	static	%{mklibname -d -s %{name}}

%package -n	%{static}
Summary:	Static development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{mklibname -d lz4}

%description -n	%{static}
This package contains the static library files to statically link against the
liblz4 library.

%prep
%setup -q
echo '#!/bin/sh' > ./configure
chmod +x ./configure

for i in $(grep -rl "\-m32");do sed -i 's!-m32!!g' $i;done

%build
%global optflags %{optflags} -Ofast
%global ldflags %{ldflags}
%setup_compile_flags
%make CC=%{__cc} programs all VERBOSE=1

%install
%makeinstall_std PREFIX=%{_prefix} LIBDIR=%{_libdir} CC=%{__cc} LDFLAGS="%{ldflags}" mandir="%{_mandir}"

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
