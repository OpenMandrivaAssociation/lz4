%define	major 1
%define	libname %mklibname lz4 %{major}
%define	devname %mklibname -d lz4

Name:		lz4
Version:	r123
Release:	2
Summary:	Extremely fast compression algorithm

Group:		Archiving/Compression
License:	GPLv2+ and BSD
URL:		https://code.google.com/p/lz4/
Source0:	https://github.com/Cyan4973/lz4/archive/%{version}/%{name}-%{version}.tar.gz
Requires:	%{libname} = %{EVRD}

%description
LZ4 is an extremely fast loss-less compression algorithm, providing compression
speed at 400 MB/s per core, scalable with multi-core CPU. It also features
an extremely fast decoder, with speed in multiple GB/s per core, typically
reaching RAM speed limits on multi-core systems.

%package -n	%{libname}
Summary:	Library for lz4
Group:		System/Libraries
License:	BSD

%description -n	%{libname}
LZ4 library.

%package -n	%{devname}
Summary:	Development library for lz4
Group:		Development/C
License:	BSD
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
This package contains the header(.h) and library(.so) files required to build
applications using liblz4 library.

%prep
%setup -q

%build
%setup_compile_flags
%make

%install
%makeinstall_std LIBDIR=%{_libdir}
chmod -x %{buildroot}%{_includedir}/*.h
rm %{buildroot}%{_libdir}/liblz4.a


%files
%doc programs/COPYING NEWS
%{_bindir}/lz4
%{_bindir}/lz4c
%{_bindir}/lz4cat
%{_mandir}/man1/lz4*

%files -n	%{libname}
%{_libdir}/liblz4.so.%{major}*

%files -n	%{devname}
%doc LICENSE
%{_includedir}/*.h
%{_libdir}/liblz4.so
%{_libdir}/pkgconfig/liblz4.pc
