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

Requires:	python
Requires:	python2-pyasn1 >= 0.3.7

BuildRequires:	python-setuptools


%description 
Python library for SNMP


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES -O1


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
