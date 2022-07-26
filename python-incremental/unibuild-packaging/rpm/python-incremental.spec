#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	incremental
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	21.3.0
Release:	1%{?dist}
Summary:	Incremental is a small library that versions your Python projects.
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Twisted Matrix
Url:		https://github.com/twisted/constantly

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:	%{_pscheduler_python_epel}-click >= 6.0

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools

%description
Incremental is a small library that versions your Python projects.

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
