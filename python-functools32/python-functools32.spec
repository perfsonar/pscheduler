#
# RPM Spec for Python functools32
#

# NOTE: This spec does some unusual things to handle the dash in the
# package's version number.  Do not use it as a template.

%define short	functools32
%define pkg_ver 3.2.3
%define pkg_patch 2
%define pkg_verpatch %{pkg_ver}-%{pkg_patch}

Name:		python-%{short}
Version:	%{pkg_ver}_%{pkg_patch}
Release:	1%{?dist}
Summary:	Backport of Python 3.2 Functools
BuildArch:	noarch
License:	PSF
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		ENDOH takanao
URL:		https://github.com/MiCHiLU/python-functools32

Source:		%{short}-%{pkg_verpatch}.tar.gz

Requires:	python

BuildRequires:	python


%description
This is a backport of the functools standard library module from
Python 3.2.3 for use on Python 2.7 and PyPy. It includes new features
lru_cache (Least-recently-used cache decorator).




# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{pkg_verpatch}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
