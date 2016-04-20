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

Requires:	drop-in
# This is for pgcrypto
Requires:	postgresql95-contrib
Requires:	postgresql95-plpython
Requires:	postgresql-init
Requires:	postgresql-load
Requires:	pscheduler-account
Requires:	random-string


%description
The pScheduler database

%define db_user %{_pscheduler_user}
%define password_file %{_pscheduler_sysconfdir}/database-password
%define dsn_file %{_pscheduler_sysconfdir}/database-dsn

%define rpm_macros %{_pscheduler_rpmmacroprefix}%{name}

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

# RPM Macros
mkdir -p $(dirname $RPM_BUILD_ROOT/%{rpm_macros})
cat > $RPM_BUILD_ROOT/%{rpm_macros} <<EOF
# %{name} %{version}
%%_pscheduler_database_dsn_file %{dsn_file}
%%_pscheduler_database_password_file %{password_file}
EOF



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

awk -v "ROLE=${ROLE}" '{ printf "host=127.0.0.1 dbname=pscheduler user=%s password=%s\n", ROLE, $1 }' \
    "%{password_file}" \
    > "%{dsn_file}"



# Load the database

# TODO: Note that if these fail, the scriptlet stops but RPM doesn't
# exit zero.  This is apparently not getting fixed.
#
# Discussion:
#   https://bugzilla.redhat.com/show_bug.cgi?id=569930
#   http://rpm5.org/community/rpm-users/0834.html
#

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


# Allow the account we created to authenticate locally.

HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
	    | postgresql-load \
	    | head -1 \
	    | sed -e 's/^\s*//' )


drop-in -n -t %{name} - $HBA_FILE <<EOF
#
# pScheduler
#
# This user should never need to access the database from anywhere
# other than locally.
#

# TODO: SECURITY: This doesn't work consistently when set up for
# password authentication.  Find out why and fix it.
local     pscheduler      pscheduler                            trust
host      pscheduler      pscheduler     127.0.0.1/32           trust
EOF


service $(basename $(ls %{_initddir}/postgresql* | head -1)) restart



# TODO: Will eventually need to handle upgrades, but that's a ways off.



%preun
# Have to do this before the files are erased.
if [ "$1" = "0" ]
then
    postgresql-load %{_pscheduler_datadir}/database-teardown.sql
fi

%postun
HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
	    | postgresql-load \
	    | head -1 \
	    | sed -e 's/^\s*//' )

drop-in -r %{name} /dev/null $HBA_FILE

service $(basename $(ls %{_initddir}/postgresql* | head -1)) restart



%files
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{_pscheduler_datadir}/*
%verify(user group mode) %{password_file}
%verify(user group mode) %{dsn_file}
%{rpm_macros}
