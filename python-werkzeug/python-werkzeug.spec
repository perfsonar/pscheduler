#
# RPM Spec for Python Module
#

%define short   werkzeug
Name:           %{_pscheduler_python}-%{short}
Version:        0.15.5
Release:        1%{?dist}
BuildArch:      noarch
Summary:        The Swiss Army knife of Python web development 
Group:          Development/Libraries
License:        BSD
URL:            http://werkzeug.pocoo.org/

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Provides:       %{name} = %{version}-%{release}
Prefix:         %{_prefix}

Source:         %{short}-%{version}.tar.gz

Requires:       %{_pscheduler_python}
BuildRequires:  %{_pscheduler_python}-devel
BuildRequires:  %{_pscheduler_python}-setuptools
BuildRequires:  %{_pscheduler_python}-sphinx

BuildRequires:  %{_pscheduler_python}-setuptools

%description
Werkzeug
========

Werkzeug started as simple collection of various utilities for WSGI
applications and has become one of the most advanced WSGI utility
modules.  It includes a powerful debugger, full featured request and
response objects, HTTP utilities to handle entity tags, cache control
headers, HTTP dates, cookie handling, file uploads, a powerful URL
routing system and a bunch of community contributed addon modules.

Werkzeug is unicode aware and doesn't enforce a specific template
engine, database adapter or anything else.  It doesn't even enforce
a specific way of handling requests and leaves all that up to the
developer. It's most useful for end user applications which should work
on as many server environments as possible (such as blogs, wikis,
bulletin boards, etc.).



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
