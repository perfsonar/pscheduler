#
# RPM Spec for Python Flask
#

%define short	Flask
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

Source:		%{short}-%{version}.tar.gz

Requires:	python
Requires:	python-Jinja2
Requires:	python-Werkzeug
Requires:	python-itsdangerous

BuildRequires:	python
BuildRequires:	python-Jinja2
BuildRequires:	python-Werkzeug
BuildRequires:	python-itsdangerous


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
