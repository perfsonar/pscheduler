Fix xinetd scripts so that they will work properly with the Debian package.

Author: Chris Taylor <ctaylor@debian.org> 
--- a/xinetd.d/nuttcp
+++ b/xinetd.d/nuttcp
@@ -5,7 +5,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args	= -S
 	log_on_failure	+= USERID
 	disable		= yes
--- a/xinetd.d/nuttcp4
+++ b/xinetd.d/nuttcp4
@@ -6,7 +6,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args     = -S -4
 	log_on_failure	+= USERID
 	disable		= yes
--- a/xinetd.d/nuttcp6
+++ b/xinetd.d/nuttcp6
@@ -7,7 +7,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args     = -S -6
 	log_on_failure	+= USERID
 	disable		= yes
