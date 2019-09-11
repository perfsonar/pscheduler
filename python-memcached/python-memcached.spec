#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	memcached
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	1.59
Release:	1%{?dist}
Summary:	Python interface to memcached
BuildArch:	%(uname -m)
License:	PSF
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Sean Reifschneider <jaf00@gmail.com>
Url:		https://github.com/linsomniac/python-memcached

Source:		python-%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools

%description
Python interface to memcached


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{long}-%{version}



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
