# Notes on Building PostgreSQL

This is temporarily in the sources until we sort out how PgSQL will be
distributed.  PGDG's distribution points are all off-R&E.

The SRPMs can be found at https://yum.postgresql.org/srpms/12/redhat.

Generally, you'll want the `rhel-<RELEASE>-<ARCHITECTURE>` version.

## To Change to a New Version

Run a diff between the existing RPM spec and the original stored along
side it and hold onto the results.

Remove all traces of the old version from the directory and Git.  This should 

Fetch the SRPM from PGDG.  For Pg 12.2, the command was:
```
wget https://yum.postgresql.org/srpms/12/redhat/rhel-7-x86_64/postgresql12-12.2-2PGDG.rhel7.src.rpm
```

Unpack the SRPM:
```
rpm2cpio postgresql12-12.2-2PGDG.rhel7.src.rpm | cpio -i
```

Preserve the RPM spec:
```
cp postgresql-12.spec postgresql-12.spec.orig
```

See if the RPM spec wil build as-is (unlikely).  If not, go through
the changes to the previous version's spec and apply similar changes
to the new one.
