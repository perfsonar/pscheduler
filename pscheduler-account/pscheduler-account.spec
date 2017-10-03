#
# RPM Spec for PostgreSQL Initializer
#

Name:		pscheduler-account
Version:	1.0.1.2
Release:	1%{?dist}

Summary:	Account for pScheduler
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No Source:

Provides:	%{name} = %{version}-%{release}

BuildRequires:	pscheduler-rpm
Requires: shadow-utils
Requires(post): shadow-utils

%define user pscheduler
%define group pscheduler
%define gecos pScheduler

%define macros %{_pscheduler_rpmmacroprefix}%{name}

%description
This package creates an account and group for pScheduler.

%install

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_rpmmacrodir}
cat > $RPM_BUILD_ROOT/%{macros} <<EOF
#
# RPM Macros for %{name} Version %{version}
#

%%_pscheduler_user %{user}
%%_pscheduler_group %{group}
EOF


%post

if [ $1 -eq 1 ]  # One instance, new install
then
    groupadd '%{group}'

    # Note: The default behavior for this is to have the password
    # disabled.  That makes it su-able but not login-able.
    useradd -c '%{gecos}' -g '%{group}' '%{user}'
fi

# Make sure the account is never never disabled or requires a password
# change.  Do this under all conditions to bring older versions into
# line.

chage \
    --expiredate -1 \
    --inactive -1 \
    --maxdays 99999 \
    '%{user}'



%postun
if [ $1 -eq 0 ]  # No more instances left.
then
    # This takes the group with it.
    userdel -r -f '%{user}'
fi


%files
%attr(444,root,root) %{_pscheduler_rpmmacroprefix}*
