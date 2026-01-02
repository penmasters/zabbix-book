---
description: |
    This section from The Zabbix Book, titled "HTTP Authentication," explains how
    to secure Zabbix frontend access using web server authentication methods. It
    covers setup with Apache or Nginx, integration with Zabbix, and how HTTP auth
    adds an extra protection layer to your monitoring environment.
tags: [advanced]
---

# HTTP

HTTP authenticatie is een van de externe authenticatiemethoden die Zabbix biedt
en kan worden gebruikt om je Zabbix WebUI extra te beveiligen met een
basisauthenticatiemechanisme op HTTP-serverniveau.

Basis HTTP authenticatie beschermt website (Zabbix WebUI) bronnen met een
gebruikersnaam en wachtwoord. Wanneer een gebruiker toegang probeert te krijgen
tot de Zabbix WebUI, zal de browser een dialoogvenster laten verschijnen waarin
gevraagd wordt naar de gebruikersnaam en wachtwoord voordat er iets verzonden
wordt naar de Zabbix WebUI php code.

Een HTTP-server heeft een bestand met referenties dat wordt gebruikt om
gebruikers te authenticeren.

???+ note

    IMPORTANT: usernames configured for basic authentication in HTTP server
    must exit in Zabbix. But only passwords configured in HTTP server are used
    for users authentication.

Laten we eerst eens kijken hoe we basisauthenticatie kunnen configureren in HTTP
server.

???+ warning

    The examples below provide just minimum set of options to configure
    basic authentication. Please refer to respective HTTP server documentation
    for more details

## Basisauthenticatie in Nginx

Zoek `location / {` block in Nginx configuratiebestand dat je Zabbix WebUI
definieert (in mijn Zabbix implementatie is dat `/etc/nginx/conf.d/nginx.conf`
bestand) en voeg deze twee regels toe:

```
    location / {
        ...
        auth_basic "Basic Auth Protected Site";
        auth_basic_user_file /etc/nginx/httpauth;
    }
```

Vergeet niet om de Nginx service te herstarten na het maken van deze wijziging.

Dan moet je het bestand `/etc/nginx/httpauth` aanmaken dat het wachtwoord van
alle gebruikers bijhoudt (zorg ervoor dat je de toegang tot dit bestand
beperkt). Het formaat van dit bestand is `gebruikersnaam:hashed_wachtwoord`,
bijvoorbeeld voor gebruikers `Admin` en `test`:

```
Admin:$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
test:$1$GXoDIOCA$u/n1kkDeFwcI4KhyHkY6p/
```

Om hashed_password te genereren kun je `openssl` gebruiken en het wachtwoord
twee keer in voeren:
```
openssl passwd
Password:
Verifying - Password:
$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
```

## Basisverificatie in Apache HTTPD

Find `<Directory "/usr/share/zabbix">` block in Apache HTTPD configuration file
that defines your Zabbix WebUI (in my case it is `/etc/zabbix/apache.conf`) and
add these lines:

???+ note By default configuration has `Require all granted`, remove this line.

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

Create `/etc/apache2/.httpasswd` (`/etc/httpd/.htpassword` for RedHat) file that
will have all the users with passwords, do it by using `htpasswd` tool, to add
user `test` execute:

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
to configure Zabbix server. In Zabbix menu select `Users | Authentication | HTTP
settings` and check `Enable HTTP authentication` check-box. Click `Update` and
confirm the changes by clicking `OK` button.

![HTTP users authentication](ch02.1-http-auth-settings.png){ align=center }

_2.1 HTTP users authentication_

`Remove domain name` field should have a comma separated list of domains that
Zabbix will remove from provided username, e.g. if a user enters "test@myzabbix"
or "myzabbix\test" and we have "myzabbix" in this field then the user will be
logged in with username "test".

Unchecking `Case-sensitive login` check-box will tell Zabbix to not pay
attention to capital/small letters in usernames, e.g. "tEst" and "test" will
become equally legitimate usernames even if in Zabbix we have only "test" user
configured.

Note that `Default login form` is set to "Zabbix login form". Now if you sign
out you will see "Sign in with HTTP" link below Username and Password fields. If
you click on the link you will be automatically logged in into Zabbix WebUI with
the same username you previously used. Or you can enter different Username and
Password and normally log in into Zabbix WebUI as different user.

![HTTP users authentication login](ch02.2-http-auth-login.png){ align=center }

_2.2 HTTP users authentication login form_

If you select "HTTP login form" in `Default login form` drop-down you won't see
standard Zabbix login form when you try to log out. You actually won't be able
to sign out unless your authentication session expires. The only way to sign out
is to clear cookies in your browser. Then you'll have to go through the Web
server basic authentication procedure again.

---

## Conclusion

Configuring HTTP level authentication adds a critical layer of access control to
your Zabbix Web UI by leveraging your web server's native authentication
mechanisms. Whether using Nginx or Apache, this approach ensures that users are
prompted for credentials before even reaching Zabbix, effectively guarding
against unauthorized access at the HTTP entry point. Key considerations include
ensuring that usernames used in the HTTP authentication are already defined
within Zabbix itself only the password from the web server matters for
credential checks and correctly setting up Zabbix's HTTP authentication settings
(such as domain removal and case sensitivity options). By coordinating web
server authentication settings with Zabbix's internal configuration, you can
achieve seamless and secure user login workflows that blend frontend usability
with robust protective measures.

## Questions

- What advantage does HTTP (web server based) authentication provide compared to
  Zabbix's internal authentication mechanism? (Consider protection at the web
  server layer before the user even reaches the Zabbix UI.)

- Why is it essential that a user must exist in Zabbix even when HTTP
  authentication is enabled and why does the Zabbix password become irrelevant
  in that case?

- What are the configuration options in Zabbix's frontend under “Administration
  → Authentication” for HTTP authentication, and how might each affect login
  behavior? Examples include enabling/disabling case sensitivity, domain
  stripping, and choice of login form.

- Suppose you disable case sensitive logins and maintain both 'Admin' and
  'admin' accounts in Zabbix. How will HTTP authentication behave, and what
  outcome should you expect?

- Imagine troubleshooting a login failure when using HTTP authentication: What
  steps would you take to ensure the web server’s authentication is configured
  correctly before examining Zabbix settings?

- From a security standpoint, when would HTTP authentication alone be
  insufficient and what other authentication methods (e.g., LDAP, SAML, MFA)
  might you layer on top for added security?

## Useful URLs

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http)
