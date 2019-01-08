#
# RPM Spec for pScheduler TEMPLATE Archiver
#

%define short	TEMPLATE
Name:		pscheduler-archiver-%{short}
Version:	1.0.2
Release:	1%{?dist}

Summary:	TEMPLATE archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 1.0.2

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
TEMPLATE archiver class for pScheduler


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
