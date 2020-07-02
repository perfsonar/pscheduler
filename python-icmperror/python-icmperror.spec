#
# RPM Spec for Python pScheduler Module
#

%define short	icmperror
Name:		%{_pscheduler_python}-%{short}
Version:	0.1
Release:	1%{?dist}
Summary:	Functions for translating ICMP error codes to enumerated values
BuildArch:	noarch
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The perfSONAR Development Team
Url:		http://www.perfsonar.net

Source0:	%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools


%description
Functions for translating ICMP error codes to enumerated values


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
