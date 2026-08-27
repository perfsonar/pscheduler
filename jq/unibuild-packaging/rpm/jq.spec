#
# RPM Spec for jq
#
# Partially adapted from the author's version at
# https://github.com/stedolan/jq/blob/master/jq.spec
#

Name:		jq
Version:	1.8.2
Release:	1
Summary:	A filter program for JSON
BuildArch:	%(uname -m)
License:	BSD
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The JQ Project
URL:		https://jqlang.org

Source:		%{name}-%{version}.tar.gz


Requires:	oniguruma

BuildRequires:  autoconf
BuildRequires:  bison > 3.0
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  oniguruma-devel


%description
jq is like sed for JSON data - you can use it to slice and filter and
map and transform structured data with the same ease that sed, awk,
grep and friends let you play with text.

%package devel
Summary:	Development files for %{name}
Requires:	%{name} = %{version}-%{release}

%description devel
Development files for %{name}


# Don't do automagic post-build things.
%global		     debug_package %{nil}


%prep
%setup -q -n %{name}-%{version}

# Replace the version generator with one that doesn't depend on git
cat > scripts/version <<EOF
#!/bin/sh
echo "%{version}"
EOF


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
%{_libdir}/pkgconfig/*

%files devel
%{_includedir}/*
%{_libdir}/libjq.so
