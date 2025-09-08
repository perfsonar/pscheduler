#
# RPM Spec for PostgreSQL Initializer
#

%define perfsonar_auto_version 5.2.2
%define perfsonar_auto_relnum 1

Name:		pscheduler-account
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Account for pScheduler
BuildArch:	noarch

License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

# No Source:

Provides:	%{name} = %{version}-%{release}

Requires:	rpm-post-wrapper

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
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'

if [ $1 -eq 1 ]  # One instance, new install
then
    groupadd --system '%{group}'

    # Note: The default behavior for this is to have the password
    # disabled.  That makes it su-able but not login-able.
    useradd \
        --comment '%{gecos}' \
        --gid '%{group}' \
        --home-dir '%{_tmppath}' \
        --no-create-home \
        --system \
        '%{user}'

elif [ $1 -eq 2 ]  # Upgrade
then

    # Make changes to an existing account (quietly)

    # Force the account home directory to be temporary space
    OUTPUT=$(usermod --home '%{_tmppath}' '%{user}' 2>&1) \
	|| echo $OUTPUT 1>&2
    
    # Don't allow logins
    OUTPUT=$(usermod --shell /sbin/nologin '%{user}' 2>&1) \
	|| echo $OUTPUT 1>&2

 fi


# Make sure the account is never never disabled or requires a password
# change.  Do this under all conditions to bring older versions into
# line.

chage \
    --expiredate -1 \
    --inactive -1 \
    --maxdays 99999 \
    '%{user}'
POST-WRAPPER-EOF



%postun
if [ $1 -eq 0 ]  # No more instances left.
then
    # This takes the group with it.
    userdel -r -f '%{user}'
fi


%files
%attr(444,root,root) %{_pscheduler_rpmmacroprefix}*
