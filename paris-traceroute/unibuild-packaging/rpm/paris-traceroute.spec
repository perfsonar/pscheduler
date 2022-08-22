#
# RPM Spec for paris-traceroute
#

%define short paris-traceroute
Name:		%{short}
Version:	1.0
Release:	1%{?dist}
Summary:	A smarter traceroute
BuildArch:	%(uname -m)
License:	MIT
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		UPMC Sorbonne Universités
Url:		http://www.paris-traceroute.net

Source:		%{short}-%{version}.tar.gz

BuildRequires:  autoconf
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make


%description
A smarter traceroute

%global debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}
./autogen.sh
./configure --prefix=%{_prefix}


%build
make


%install
make DESTDIR=%{buildroot} install

# Remove things we don't want.

rm %{buildroot}/%{_bindir}/ping
# These use /lib explicitly because some distros use lib64.
rm -r %{buildroot}/%{_prefix}/lib/pkgconfig


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
%{_prefix}/lib/*


#
# Development Subpackage
#

%package -n %{name}-devel
Summary: Header files for %{name} development
Group: Development/Libraries
Provides: %{name}-devel = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

%description -n %{name}-devel
Header files for %{name} development

%files -n %{name}-devel
%defattr(-,root,root)
%{_includedir}/paristraceroute
