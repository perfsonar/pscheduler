#
# RPM Spec for pScheduler Ping Tool
#

%define short	ping
Name:		pscheduler-tool-%{short}
Version:	1.0.2.4
Release:	1%{?dist}

Summary:	pScheduler Ping Tool
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-account
Requires:	python-ipaddr
Requires:	python-pscheduler
Requires:	pscheduler-test-rtt
Requires:	python-icmperror
# This supplies ping.
Requires:	iputils
Requires:	sudo

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	iputils


%description
pScheduler Ping Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%install
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


# Enable sudo for ping

PING=$(which ping)

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF
#
# %{name}
#
Cmnd_Alias PSCHEDULER_TOOL_PING = ${PING}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${PING}
Defaults!PSCHEDULER_TOOL_PING !requiretty


EOF


%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
