Fix xinetd scripts so that they will work properly with the Debian package.

Author: Chris Taylor <ctaylor@debian.org> 
--- nuttcp-5.5.5.orig/xinetd.d/nuttcp
+++ nuttcp-5.5.5/xinetd.d/nuttcp
@@ -5,7 +5,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args	= -S
 	log_on_failure	+= USERID
 	disable		= yes
--- nuttcp-5.5.5.orig/xinetd.d/nuttcp4
+++ nuttcp-5.5.5/xinetd.d/nuttcp4
@@ -6,7 +6,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args     = -S -4
 	log_on_failure	+= USERID
 	disable		= yes
--- nuttcp-5.5.5.orig/xinetd.d/nuttcp6
+++ nuttcp-5.5.5/xinetd.d/nuttcp6
@@ -7,7 +7,7 @@
 	socket_type	= stream        
 	wait		= no
 	user		= nobody
-	server		= /usr/local/bin/nuttcp
+	server		= /usr/bin/nuttcp
 	server_args     = -S -6
 	log_on_failure	+= USERID
 	disable		= yes
