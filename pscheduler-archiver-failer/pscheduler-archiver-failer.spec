#
# RPM Spec for pScheduler Failer Archiver
#

%define short	failer
Name:		pscheduler-archiver-%{short}
Version:	1.0
Release:	0.17.rc2%{?dist}

Summary:	Sometimes-failing archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver is like the bitbucket archiver but fails randomly about
10% of the time.


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
