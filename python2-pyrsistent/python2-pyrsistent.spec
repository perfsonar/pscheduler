#
# RPM Spec for Python Module
#

%define short	pyrsistent
Name:		python2-%{short}
Version:	0.14.11
Release:	1%{?dist}
Summary:	Persistent/Immutable/Functional data structures for Python

BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Provides:	python-%{short} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Tobias Gustaffson
URL:		https://github.com/tobgu/pyrsistent

Source:		%{short}-%{version}.tar.gz

Requires:       python

BuildRequires:  python
BuildRequires:  python-devel
BuildRequires:  python-setuptools

%description 
Pyrsistent is a number of persistent collections (by some referred to
as functional data structures). Persistent in the sense that they are
immutable.




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
