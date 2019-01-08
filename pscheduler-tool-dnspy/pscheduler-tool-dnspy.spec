#
# RPM Spec for pScheduler DNSpy Tool
#

%define short	dnspy
Name:		pscheduler-tool-%{short}
Version:	1.1.2
Release:	1%{?dist}

Summary:	DNS tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-dns
Requires:	python-pscheduler
Requires:	pscheduler-test-dns

BuildRequires:	pscheduler-rpm


%description
DNS tool class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install



%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}

