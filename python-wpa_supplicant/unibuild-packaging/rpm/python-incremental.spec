#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	wpa_supplicant
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	0.2
Release:	1%{?dist}
Summary:	Python DBus interface to wpa_supplicant
BuildArch:	%(uname -m)
License:	MPL 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Url:		https://pypi.org/project/wpa_supplicant

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:	%{_pscheduler_python_epel}-click >= 6.0

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools

%description
Python DBus interface to wpa_supplicant

# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global              debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}



%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    --single-version-externally-managed \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
