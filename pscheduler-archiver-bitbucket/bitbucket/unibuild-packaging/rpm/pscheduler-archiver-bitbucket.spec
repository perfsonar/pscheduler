#
# RPM Spec for pScheduler Bitbucket Archiver
#

%define short	bitbucket
%define perfsonar_auto_version 5.2.2
%define perfsonar_auto_relnum 1

Name:		pscheduler-archiver-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Bitbucket archiver class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 1.1.6
Requires:	%{_pscheduler_python}-pscheduler
Requires:	rpm-post-wrapper

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver disposes of measurements by dropping them on the floor.


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


%post
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
pscheduler internal warmboot
POST-WRAPPER-EOF

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
