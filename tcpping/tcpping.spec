#
# RPM Spec for tcpping
#

Name: tcpping
Version: 0.1
Release: 1%{?dist}
Summary: Dead simple TCP Ping tool 
License: AGPL3
Group: Applications/Internet
URL: https://github.com/guhl1956/tcpping
Source: %{name}-%{version}.tar.gz

%description
Dead simple TCP Ping tool 


# Don't bulid a debug package
%global debug_package %{nil}


%prep
%setup -q

%install
mkdir -p ${RPM_BUILD_ROOT}/%{_bindir}
cp %{name}.py ${RPM_BUILD_ROOT}/%{_bindir}/%{name}


%files
%doc README.md LICENSE.txt
%{_bindir}/*
