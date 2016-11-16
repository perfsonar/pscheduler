#
# RPM Spec for Python Flask
#

%define short	flask
Name:		python-%{short}
Version:	0.10.1
Release:	1%{?dist}
Summary:	The Flask microframework
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Armin Ronacher
URL:		http://flask.pocoo.org

# This package replaces an older version built with a capital F, a
# convention Red Hat did not follow.
Obsoletes:	python-Flask <= %{version}
Conflicts:	python-Flask

Source:		%{short}-%{version}.tar.gz

Requires:	python
Requires:	python-jinja2
Requires:	python-werkzeug
Requires:	python-itsdangerous

BuildRequires:	python
BuildRequires:	python-jinja2
BuildRequires:	python-werkzeug
BuildRequires:	python-itsdangerous
BuildRequires:	python-setuptools

%description
Flask is a microframework for Python based on Werkzeug, Jinja 2 and
good intentions.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}

# The delivered tarball contains some stray Git files which causes git
# against the source tree to misbehave.  Wipe 'em.
find . -name '.git*' | xargs rm -rf


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
