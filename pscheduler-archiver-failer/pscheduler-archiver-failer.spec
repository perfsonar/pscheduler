#
# RPM Spec for pScheduler Failer Archiver
#

%define short	failer
Name:		pscheduler-archiver-%{short}
Version:	1.1.5
Release:	1%{?dist}

Summary:	Sometimes-failing archiver class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 1.1.5

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
     install


%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
