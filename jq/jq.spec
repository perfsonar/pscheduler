#
# RPM Spec for jq
#
# Partially adapted from the author's version at
# https://github.com/stedolan/jq/blob/master/jq.spec
#


# This is the version of jq we build, plus our patches
%define actual_version 1.6

# The jq developers don't do bugfix releases, so our is numbered with
# a bugfix release number to force our patched version to be
# considered newer and installed.  This is because of the integer
# patch, which has been accepted into jq but not yet released.
%define release_version %{actual_version}.10

%define short	jq
Name:		%{short}
Version:	%{release_version}
Release:	2%{?dist}
Summary:	A filter program for JSON
BuildArch:	%(uname -m)
License:	BSD
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Stephen Dolan <mu@netsoc.tcd.ie>
URL:		https://stedolan.github.io/jq

Source:		%{short}-%{actual_version}.tar.gz

Patch0:		%{short}-%{actual_version}-00-jv_is_integer_large.patch


Requires:	oniguruma >= 6.8.2

BuildRequires:  autoconf
BuildRequires:  bison > 3.0
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  oniguruma-devel >= 6.8.2


%description
jq is like sed for JSON data - you can use it to slice and filter and
map and transform structured data with the same ease that sed, awk,
grep and friends let you play with text.

NOTE:  This version contains a bugfix patch that the jq maintainers
       have not yet released.  Its version number was bumped to %{release_version}
       to keep it ahead of EPEL and the jq developers (%{actual_version}).

%package devel
Summary:	Development files for %{name}
Requires:	%{name} = %{version}-%{release}

%description devel
Development files for %{name}


# Don't do automagic post-build things.
%global		     debug_package %{nil}


%prep
%setup -q -n %{name}-%{actual_version}

# Replace the version generator with one that doesn't depend on git
cat > scripts/version <<EOF
#!/bin/sh
echo "%{version}+pscheduler-patches"
EOF

%patch0 -p1



%build
autoreconf -fi
%configure --disable-static --disable-maintainer-mode
make DESTDIR=%{buildroot}


%install
make DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -exec rm -f {} ';'


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%{_bindir}/*
%{_docdir}/*
%{_mandir}/man1/*
%{_libdir}/libjq.so.*

%files devel
%{_includedir}/*
%{_libdir}/libjq.so
