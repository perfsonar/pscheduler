#
# RPM Spec for a pScheduler context changer
#

# NOTE: This spec includes files beyond what the standard context
# changer spec installs, namely additions to sudoers.


%define short	linuxnns
Name:		pscheduler-context-%{short}
Version:	1.0.2.6
Release:	1%{?dist}

Summary:	Linux network namespace context changer for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	iproute

BuildRequires:	pscheduler-rpm >= 1.0.0.5.1


%define directory %{_includedir}/make

%description
This context changer changes the Linux network namespace.


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
Cmnd_Alias PSCHEDULER_CONTEXT_LINUXNNS=/sbin/ip netns exec *
%{_pscheduler_user} ALL = (root) NOPASSWD: PSCHEDULER_CONTEXT_LINUXNNS
Defaults!PSCHEDULER_CONTEXT_LINUXNNS !requiretty
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
