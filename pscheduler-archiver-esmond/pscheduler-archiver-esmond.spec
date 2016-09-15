#
# RPM Spec for pScheduler Esmond Archiver
#

%define short	esmond
Name:		pscheduler-archiver-esmond
Version:	1.0
Release:	0.2.rc1%{?dist}

Summary:	Esmond archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-requests

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver sends JSON test results to Esmond Measurement Archive


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_archiver_doc} \
     install


%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_archiver_doc}/*
