#
# RPM Spec for pScheduler Esmond Archiver
#

%define short	esmond
Name:		pscheduler-archiver-esmond
Version:	0.0
Release:	1%{?dist}

Summary:	Esmond archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-core
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


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_archiver_doc}/*
