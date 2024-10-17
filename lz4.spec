# lz4 is used by systemd, libsystemd is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 1

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%if %{cross_compiling}
%bcond_with pgo
%else
%bcond_without pgo
%endif

Name:		lz4
Version:	1.10.0
Release:	1
Summary:	Extremely fast compression algorithm
Group:		Archiving/Compression
License:	GPLv2+ and BSD
URL:		https://www.lz4.org/
Source0:	https://github.com/lz4/lz4/archive/v%{version}.tar.gz
Patch0:		lz4-1.10.0-cmake-build-fullbench.patch
BuildRequires:	cmake
BuildRequires:	ninja

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
Requires:	%{mklibname lz4}

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
BuildRequires:	libc6

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
%{_prefix}/lib/cmake/lz4

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

%build
cd build/cmake

%if %{with compat32}
%cmake32 \
	-DBUILD_STATIC_LIBS:BOOL=ON \
	-G Ninja
%ninja_build
cd ..
%endif

%if %{with pgo} && ! %{cross_compiling}
CFLAGS="%{optflags} -fprofile-generate -mllvm -vp-counters-per-site=16" \
CXXFLAGS="%{optflags} -fprofile-generate -mllvm -vp-counters-per-site=16" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%cmake \
	-DBUILD_STATIC_LIBS:BOOL=ON \
	-DBUILD_BENCHMARKS:BOOL=ON \
	-G Ninja

%ninja_build
export LD_LIBRARY_PATH="$(pwd)"

./fullbench -c ../../../lib/lz4.c
./fullbench -d ../../../lib/lz4.c

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw
rm -rf build/meson*
rm -rf /build/*ninja*
cd ..

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%cmake \
	-DBUILD_STATIC_LIBS:BOOL=ON \
	-G Ninja

%ninja_build

%install
%if %{with compat32}
%ninja_install -C build/cmake/build32
rm -rf %{buildroot}%{_bindir}/* %{buildroot}%{_mandir}
%endif
%ninja_install -C build/cmake/build
ln -s lz4 %{buildroot}%{_bindir}/lz4c

%files
%doc NEWS
%{_bindir}/lz4
%{_bindir}/lz4c
%{_bindir}/lz4cat
%{_bindir}/unlz4
%doc %{_mandir}/man1/*lz4*.1*

%{libpackage %{name} %{major}}

%files -n %{devname}
%doc lib/LICENSE
%{_includedir}/*.h
%{_libdir}/liblz4.so
%{_libdir}/pkgconfig/liblz4.pc
%{_libdir}/cmake/lz4

%files -n %{static}
%{_libdir}/liblz4.a
