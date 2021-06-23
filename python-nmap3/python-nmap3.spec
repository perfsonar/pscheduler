#
# RPM Spec for Python nmap3 Module
#

%define short	nmap3
%define actual  python3-nmap
Name:		%{_pscheduler_python}-%{short}
Version:	1.5.0
Release:	%{?dist}
Summary:	python3 library for nmap port scanner
BuildArch:	noarch
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Wangolo Joel <info@nmmapper.com>
Url:		https://www.nmmapper.com/

Source:		%{actual}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:       %{_pscheduler_python_epel}-simplejson
Requires:      	nmap

BuildRequires:	%{_pscheduler_python}-setuptools

%description
A python 3 library which helps in using nmap port scanner. The way this tools works is by defining each nmap command into a python function making it very easy to use sophisticated nmap commands in other python scripts. Nmap is a complicated piece of software used for reconnaissance on target networks, over the years new features have been added making it more sophisticated.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{actual}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
