#
# RPM Spec for a pScheduler context changer
#

%define short	changenothing
Name:		pscheduler-context-%{short}
Version:	1.0.2.2
Release:	1%{?dist}

Summary:	Null context changer class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server

BuildRequires:	pscheduler-rpm >= 1.0.0.5.1


%define directory %{_includedir}/make

%description
This context changer does nothing.


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_context_libexec}/%{short}

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
%{dest}
