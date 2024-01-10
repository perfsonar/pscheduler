#
# RPM Spec for Python Flask
#

%define short	flask
Name:		python-%{short}
Version:	1.1.1
Release:	1%{?dist}
Summary:	A micro-framework for Python based on Werkzeug, Jinja 2 and good intentions
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Pallets Projects
URL:		https://palletsprojects.com/p/flask

Source:		%{short}-%{version}.tar.gz

Requires:	python
Requires:	python-click
Requires:	python-jinja2
Requires:	python-itsdangerous
Requires:	python-werkzeug

BuildRequires:	python
BuildRequires:	python-setuptools

%description
Flask is called a “micro-framework” because the idea to keep the core
simple but extensible. There is no database abstraction layer, no form
validation or anything else where different libraries already exist
that can handle that. However Flask knows the concept of extensions
that can add this functionality into your application as if it was
implemented in Flask itself. There are currently extensions for object
relational mappers, form validation, upload handling, various open
authentication technologies and more.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install \
    --root=$RPM_BUILD_ROOT \
    --single-version-externally-managed \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
