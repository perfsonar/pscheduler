#
# RPM Spec for Python Itsdangerous
#

%define short	itsdangerous
Name:		%{_pscheduler_python}-%{short}
Version:	1.1.0
Release:	1%{?dist}
Summary:	JSON Signature Module
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Pallets Projects
URL:		https://palletsprojects.com/p/itsdangerous

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools


%description
JSON signature module



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


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
