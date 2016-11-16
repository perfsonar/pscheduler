#
# RPM Spec for Python Jinja2
#

%define short	jinja2
Name:		python-%{short}
Version:	2.8
Release:	2%{?dist}
Summary:	The Jinja templating system
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Armin Ronacher
URL:		http://jinja.pocoo.org

Source:		%{short}-%{version}.tar.gz

# This package replaces an older version built with a capital J, a
# convention Red Hat did not follow.
Obsoletes:	python-Jinja2 <= %{version}
Provides:	python-Jinja2

Requires:	python
Requires:	python-markupsafe

BuildRequires:	python
BuildRequires:	python-setuptools

%description
A small but fast and easy to use stand-alone template engine written
in pure python.



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
