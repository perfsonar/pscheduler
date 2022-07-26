#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	txdbus
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	1.1.2
Release:	1%{?dist}
Summary:	Pure python interface to DBus
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Tom Cocagne
Url:		https://github.com/twisted/constantly

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:	%{_pscheduler_python}-Twisted

BuildRequires:	%{_pscheduler_python}-setuptools

%description
Pure python interface to DBus

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
