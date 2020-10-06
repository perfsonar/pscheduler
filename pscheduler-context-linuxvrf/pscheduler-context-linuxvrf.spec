#
# RPM Spec for a pScheduler context changer
#

# NOTE: This spec includes files beyond what the standard context
# changer spec installs, namely additions to sudoers.


%define short	linuxvrf
%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.b1.3

Name:		pscheduler-context-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Linux VRF context changer for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
Requires:	iproute

BuildRequires:	pscheduler-rpm >= 1.0.0.5.1


%define directory %{_includedir}/make

%description
This context changer changes the Linux virtual routing and
forwarding domain.


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_context_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


# Enable sudo for the slim part of 'ip' that we use.

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<'EOF'
#
# %{name}
#
Cmnd_Alias PSCHEDULER_CONTEXT_LINUXVRF=/sbin/ip vrf exec *
%{_pscheduler_user} ALL = (root) NOPASSWD: PSCHEDULER_CONTEXT_LINUXVRF
Defaults!PSCHEDULER_CONTEXT_LINUXVRF !requiretty
EOF



%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
