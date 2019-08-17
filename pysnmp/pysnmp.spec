#
# RPM Spec for Python pysnmp Module
#

%define short	pysnmp
Name:		%{short}
Version:	4.3.9
Release:	1%{?dist}
Summary:	Python library for SNMP
BuildArch:	noarch
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

#Vendor:		TODO: Add this
#Url:		TODO: Add this

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:	%{_pscheduler_python}-pyasn1 >= 0.3.7

BuildRequires:	%{_pscheduler_python}-setuptools


%description 
Python library for SNMP


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
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
