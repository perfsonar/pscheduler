#
# Adapted from the EPEL package
#

Name: oniguruma
Version: 6.9.6
Release: 1%{?dist}
Summary: Regular expressions library
License: BSD
Group: Development/Librariesd
URL: https://github.com/kkos/oniguruma/

Source: %{name}-%{version}.tar.gz

BuildRequires: autoconf

%description
Oniguruma is a regular expressions library.  The characteristics of
the library is that different character encoding for every regular
expression object can be specified.  (supported APIs: GNU regex, POSIX
and Oniguruma native)


# Don't bulid a debug package

%global debug_package %{nil}


%prep
%setup -q


%build
./autogen.sh
%configure
%{__make}

%install
%make_install

%files
%{_bindir}/*
%{_libdir}/*
#/usr/lib64/pkgconfig/oniguruma.pc




%package -n %{name}-devel
Summary: Header files for %{name} development
Group: Development/Libraries
Provides: %{name}-devel = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

%description -n %{name}-devel
Header files for %{name} development

%files -n %{name}-devel
%defattr(-,root,root)
%{_includedir}/*
