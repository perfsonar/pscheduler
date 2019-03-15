#
# RPM Spec for jq
#
# Partially adapted from the author's version at
# https://github.com/stedolan/jq/blob/master/jq.spec
#

%define short	jq
Name:		%{short}
Version:	1.6
Release:	1%{?dist}
Summary:	A filter program for JSON
BuildArch:	%(uname -m)
License:	BSD
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Stephen Dolan <mu@netsoc.tcd.ie>
URL:		https://stedolan.github.io/jq

Source:		%{short}-%{version}.tar.gz

Patch0:		%{short}-%{version}-00-jv_is_integer_large.patch



BuildRequires:  autoconf
BuildRequires:  bison > 3.0
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make


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
echo "%{version}+pscheduler-patches"
EOF

%patch0 -p1



%build
autoreconf --install
#./configure --prefix=%{_prefix} --libdir=%{_libdir}
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
