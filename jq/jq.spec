#
# RPM Spec for jq
#
# Partially adapted from the author's version at
# https://github.com/stedolan/jq/blob/master/jq.spec
#

%define short	jq
Name:		%{short}
Version:	1.5
Release:	1%{?dist}
Summary:	A filter program for JSON
BuildArch:	%(uname -m)
License:	CC-BY-3.0
Group:		Applications/Text

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Stephen Dolan <mu@netsoc.tcd.ie>
Url:		https://stedolan.github.io/jq

Source:		%{short}-%{version}.tar.gz

BuildRequires:  autoconf
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make


%description
jq is like sed for JSON data - you can use it to slice and filter and
map and transform structured data with the same ease that sed, awk,
grep and friends let you play with text.


# Don't do automagic post-build things.
%global		     debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}
# --disable-maintainer-mode is necessary for systems without Bison 3.0
./configure --prefix=%{_prefix} --disable-maintainer-mode


%build
make


%install
make install DESTDIR=%{buildroot}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%{_bindir}/*
%{_docdir}/*
%{_mandir}/man1/*
%{_includedir}/*
%{_prefix}/lib/*
