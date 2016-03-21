#
# RPM Spec for pScheduler Database
#

Name:		pscheduler-database
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler database
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql-init
Requires:	postgresql-load
Requires:	random-string


%description
The pScheduler database

%define db_user %{_pscheduler_user}
%define password_file %{_pscheduler_sysconfdir}/database-password
%define dsn_file %{_pscheduler_sysconfdir}/database-dsn

%prep
%setup -q

%build
make

%install
make DATADIR=$RPM_BUILD_ROOT/%{_pscheduler_datadir} install

# These will be populated on installation
for FILE in %{password_file} %{dsn_file}
do
    DIR=$(dirname "$RPM_BUILD_ROOT/${FILE}")
    mkdir -p "${DIR}"
    touch "$RPM_BUILD_ROOT/${FILE}"
    chmod 440 "$RPM_BUILD_ROOT/${FILE}"
done


%post
# Generate a password if the file is empty, which is the case after
# the first install.
#
# TODO: This might be annoying if someone intentionally sets the
# password up as empty.
if [ ! -s '%{password_file}' ]
then
    random-string --quote-safe > '%{password_file}'
fi

# Check our assumptions
if [ "$(wc -l < '%{password_file}')" -ne 1 ]
then
    echo "INTERNAL ERROR: " \
        "Password file %{password_file} must contain exactly one line." 1>&2
    exit 1
fi


# Figure out the role that owns the database.

ROLE=$(fgrep 'CREATE ROLE' %{_pscheduler_datadir}/database-build-super.sql \
	     | head -1 \
	     | awk '{ print $3 }')

if [ -z "${ROLE}" ]
then
	echo "Can't find role name in SQL" 1>&2
	exit 1
fi



# Generate the DSN file

awk -v "ROLE=${ROLE}" '{ printf "dbname=pscheduler user=%s password=%s\n", ROLE, $1 }' \
    "%{password_file}" \
    > "%{dsn_file}"



# Load the database

# TODO: Note that if these fail, the scriptlet stops but RPM doesn't
# exit zero.  This is apparently not getting fixed.
#
# Discussion:
#   https://bugzilla.redhat.com/show_bug.cgi?id=569930
#   http://rpm5.org/community/rpm-users/0834.html

postgresql-load %{_pscheduler_datadir}/database-build-super.sql
postgresql-load --role '%{db_user}' %{_pscheduler_datadir}/database-build.sql

# Securely set the password for the role to match the one we generated.

ROLESQL="${TMP:-/tmp}/%{name}.$$"
touch "${ROLESQL}"
chmod 400 "${ROLESQL}"

printf "ALTER ROLE ${ROLE} WITH UNENCRYPTED PASSWORD '" > "${ROLESQL}"
tr -d "\n" < "%{password_file}" >> "${ROLESQL}"
printf "';\n"  >> "${ROLESQL}"

postgresql-load "${ROLESQL}"
rm -f "${ROLESQL}"

# TODO: What do we want to do about trust in pg_hba.conf?  Local user
# only and nothing over the network should be sufficient.

# TODO: Will eventually need to handle upgrades, but that's a ways off.



%preun
# Have to do this before the files are erased.
if [ "$1" = "0" ]
then
    postgresql-load %{_pscheduler_datadir}/database-teardown.sql
fi




%files
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{_pscheduler_datadir}/*
%verify(user group mode) %{password_file}
%verify(user group mode) %{dsn_file}
