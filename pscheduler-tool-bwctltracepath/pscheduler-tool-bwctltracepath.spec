#
# RPM Spec for pScheduler BWCTL Tracepath Tool
#

%define short	bwctltracepath
Name:		pscheduler-tool-%{short}
Version:	1.1.6
Release:	1%{?dist}

Summary:	pScheduler BWCTL Tracepath Tool (DISABLED)
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-test-trace

BuildRequires:	pscheduler-rpm


%description
pScheduler BWCTL Tracepath Tool (DISABLED)


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
