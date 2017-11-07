#
# RPM Spec for Python Module
#

%define short	pyasn1
Name:		python2-%{short}
Version:	0.3.7
Release:	1%{?dist}
Summary:	ASN1 for Python
BuildArch:	%(uname -m)
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Ilya Etingof <etingof@gmail.com>
URL:		https://github.com/etingof/pyasn1

Source:		%{short}-%{version}.tar.gz

Requires:       python

BuildRequires:  python
BuildRequires:  python-setuptools

%description
ASN1 for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


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
