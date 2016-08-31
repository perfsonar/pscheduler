#
# RPM Spec for DNSPython Module
#

%define short	dnspython
Name:		python-%{short}
Version:	1.12.0
Release:	1%{?dist}
Summary:	DNS resolver library
BuildArch:	noarch
License:	BSD-derived
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Nominum, Inc.
Url:		https://www.dnspython.org

Source:		%{short}-%{version}.tar.gz

BuildRequires:	python-setuptools

%description
DNS resolver library


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
