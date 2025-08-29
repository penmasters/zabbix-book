---
description: |
---

# HTTP

HTTP authentication is one of external authentication methods provided by
Zabbix and can be used to additionally secure your Zabbix WebUI with
basic authentication mechanism at HTTP server level.

Basic HTTP authentication protects Website (Zabbix WebUI) resources with a
username and password. When a user attempts to access Zabbix WebUI, the
browser pops up a dialog asking for credentials before sending anything over
to Zabbix WebUI php code.

An HTTP server has a file with credentials that is used to authenticate users.

???+ note

    IMPORTANT: usernames configured for basic authentication in HTTP server
    must exit in Zabbix. But only passwords configured in HTTP server are used
    for users authentication.

First let's see how we can configure basic authentication in HTTP server.

???+ warning

    The examples below provide just minimum set of options to configure
    basic authentication. Please refer to respective HTTP server documentation
    for more details

## Basic authentication in Nginx

Find `location / {` block in Nginx configuration file that defines your Zabbix
WebUI (in my Zabbix deployment it is `/etc/nginx/conf.d/nginx.conf` file) and
add these two lines:

```
    location / {
        ...
        auth_basic "Basic Auth Protected Site";
        auth_basic_user_file /etc/nginx/httpauth;
    }
```

Do not forget to restart Nginx service after making this change.

Then you need to create `/etc/nginx/httpauth` file which will keep all users'
password (make sure to restrict access to this file). Format of this file is
`username:hashed_password`, for example, for
users `Admin` and `test`:

```
Admin:$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
test:$1$GXoDIOCA$u/n1kkDeFwcI4KhyHkY6p/
```

To generate hashed_password you can use `openssl` tool entering the password
twice:
```
openssl passwd
Password:
Verifying - Password:
$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
```

## Basic authentication in Apache HTTPD

Find `<Directory "/usr/share/zabbix">` block in Apache HTTPD configuration file
that defines your Zabbix WebUI (in my case it is `/etc/zabbix/apache.conf`) and
add these lines:

???+ note
    By default configuration has `Require all granted`, remove this line.

For Ubuntu/Debian:
```
    <Directory "/usr/share/zabbix">
        ...
        AuthType Basic
        AuthName "Restricted Content"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Directory>
```

For RedHat:
```
    <Directory "/usr/share/zabbix">
        ...
        AuthType Basic
        AuthName "Restricted Content"
        AuthUserFile /etc/httpd/.htpasswd
        Require valid-user
    </Directory>
```

Do not forget to restart apache2 service after making this change.

Create `/etc/apache2/.httpasswd` (`/etc/httpd/.htpassword` for RedHat) file that will have all the users with
passwords, do it by using `htpasswd` tool, to add user `test` execute:

For Ubuntu/Debian
```
sudo htpasswd -c /etc/apache2/.htpasswd test
New password: 
Re-type new password: 
Adding password for user test
```

For RedHat
```
sudo htpasswd -c /etc/httpd/.htpasswd test
New password: 
Re-type new password: 
Adding password for user test
```

To add more users to the file repeat the command without `-c` flag.

## Zabbix configuration for HTTP authentication

When we have a WEB server configured with basic authentication it is high time
to configure Zabbix server. In Zabbix menu select `Users | Authentication |
HTTP settings` and check `Enable HTTP authentication` check-box. Click `Update`
and confirm the changes by clicking `OK` button.

![HTTP users authentication](ch02.1-http-auth-settings.png){ align=center }

_2.1 HTTP users authentication_

`Remove domain name` field should have a comma separated list of domains that
Zabbix will remove from provided username, e.g. if a user enters
"test@myzabbix" or "myzabbix\test" and we have "myzabbix" in this field then
the user will be logged in with username "test".

Unchecking `Case-sensitive login` check-box will tell Zabbix to not pay
attention to capital/small letters in usernames, e.g. "tEst" and "test" will
become equally legitimate usernames even if in Zabbix we have only "test"
user configured.

Note that `Default login form` is set to "Zabbix login form". Now if you sign
out you will see "Sign in with HTTP" link below Username and Password fields.
If you click on the link you will be automatically logged in into Zabbix WebUI
with the same username you previously used. Or you can enter different
Username and Password and normally log in into Zabbix WebUI as different user.

![HTTP users authentication login](ch02.2-http-auth-login.png){ align=center }

_2.2 HTTP users authentication login form_

If you select "HTTP login form" in `Default login form` drop-down you won't see
standard Zabbix login form when you try to log out. You actually won't be able
to sign out unless your authentication session expires. The only way to sign out
is to clear cookies in your browser. Then you'll have to go through the Web
server basic authentication procedure again.

---

## Conclusion

## Questions

## Useful URLs
