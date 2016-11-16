#
# RPM Spec for Python Werkzeug
#

%define short	werkzeug
Name:		python-%{short}
Version:	0.11.3
Release:	2%{?dist}
Summary:	WSGI Utilities for Python
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Armin Ronacher
URL:		http://werkzeug.pocoo.org

Source:		%{short}-%{version}.tar.gz

# This package replaces an older version built with a capital W, a
# convention Red Hat did not follow.
Obsoletes:	python-Werkzeug <= %{version}
Conflicts:	python-Werkzeug

Requires:	python

BuildRequires:	python
BuildRequires:	python-setuptools



%description
Werkzeug started as simple collection of various utilities for WSGI
applications and has become one of the most advanced WSGI utility
modules. It includes a powerful debugger, full featured request and
response objects, HTTP utilities to handle entity tags, cache control
headers, HTTP dates, cookie handling, file uploads, a powerful URL
routing system and a bunch of community contributed addon modules.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
