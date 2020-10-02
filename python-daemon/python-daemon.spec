#
# RPM Spec for a Python Module
#

%define short	daemon
Name:		%{_pscheduler_python}-%{short}
Version:	2.2.3
Release:	1%{?dist}
Summary:	Daemonizer library for Python
BuildArch:	noarch
License:	ASL 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Ben Finney <ben+python@benfinney.id.au>
Url:		https://pagure.io/python-daemon

Source:		python-%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools

%description
Daemonizer library for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n python-%{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
