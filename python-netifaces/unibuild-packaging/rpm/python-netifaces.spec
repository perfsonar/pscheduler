#
# RPM Spec for Python netifaces
#

%define short netifaces

Name:		%{_pscheduler_python}-%{short}
Version:	0.11.0
Release:	1%{?dist}
Summary:	Network interface enumeration for Python
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Alistair Houghton
URL:		https://github.com/al45tair/netifaces

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-devel
BuildRequires:	%{_pscheduler_python}-setuptools


%define internal_version %(echo '%{version}' | tr . _)
%define tar_path netifaces-release_%{internal_version}

%description
Network interface enumeration for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{tar_path}


%build
python setup.py build


%install
python setup.py install \
    --root=$RPM_BUILD_ROOT \
    --single-version-externally-managed \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
