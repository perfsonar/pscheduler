#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	typing_extensions
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	4.3.0
Release:	1%{?dist}
Summary:	Type compatibility for older Pythons
BuildArch:	%(uname -m)
License:	PSF
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Guido van Rossum et al.
Url:		https://pypi.org/project/typing-extensions/

Source0:	%{short}-%{version}.tar.gz
Source1:	setup.py
Source2:	__init__.py

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-devel
BuildRequires:	%{_pscheduler_python}-test
BuildRequires:	%{_pscheduler_python_epel}-pytest


%description
Type compatibility for older Pythons


# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global              debug_package %{nil}


%prep
%autosetup -n %{short}-%{version}



%build
ln -s src %{short}
cp ${RPM_SOURCE_DIR}/setup.py .
cp ${RPM_SOURCE_DIR}/__init__.py %{short}
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    --record=INSTALLED_FILES \
    -O1


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
