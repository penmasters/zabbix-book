# External authentication

## HTTP

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

### Basic authentication in Nginx

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

To generate hashed_password you can use `openssl` tool enetring the password
twice:
```
openssl passwd
Password:
Verifying - Password:
$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
```

### Basic authentication in Apache HTTPD

Find `<Directory "/usr/share/zabbix">` block in Apache HTTPD configuration file
that defines your Zabbix WebUI (in my case it is `/etc/zabbix/apache.conf`) and
add these lines:

???+ note
    By default configuration has `Require all granted`, remove this line.

```
    <Directory "/usr/share/zabbix">
        ...
        AuthType Basic
        AuthName "Restricted Content"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Directory>
```

Do not forget to restart apache2 service after making this change.

Create `/etc/apache2/.httpasswd` file that will have all the users with
passwords, do it by using `htpasswd` tool, to add user `test` execute:
```
sudo htpasswd -c /etc/apache2/.htpasswd test
New password: 
Re-type new password: 
Adding password for user test
```
To add more users to the file repeat the command without `-c` flag.

### Zabbix configuration for HTTP authentication

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
to sign out unless your authetnciation session expires. The only way to sign out
is to clear cookies in your browser. Then you'll have to go through the Web
server basic authentication procedure again.

## LDAP / AD

As any modern system Zabbix can perform users authentication using Lightweight
Directory Access Protocol (LDAP). In theory LDAP is very well defined open
protocol that should be vendor independent but its relative complexity plays a
role in every LDAP server implementation. Zabbix is known to work well with
Microsoft Active Directory and OpenLDAP server.

LDAP authentication can be configured in two modes:

- Users authentication
- Users authentication with users provisioning

### Users authentication mode

The process of the authenticating users follows this diagram.

![LDAP users authentication](ch02.3-ldap-auth-diagram.png){ align=center }

_2.3 LDAP users authentication_

As shown on the diagram a user that tries to log in must be pre-created in
Zabbix to be able to log in using LDAP. The database user records do not have
any fields "saying" that the user will be authenticated via LDAP, it's just
users' passwords stored in the database are ignored, instead, Zabbix goes to
a LDAP server to verify whether:

- user with a given username exists
- user provided the correct password

no other attributes configured for the user on the LDAP server side are taken
into account.

So when Zabbix is used by many users and groups, user management becomes not a
very trivial task as new people join different teams (or leave). This problem
is addressed by "users provisioning" and we'll cover this topic a bit later.
For now let's take a look at how to configure LDAP authentication.

### Configure LDAP

We believe that it is better to learn this topic by example so we'll be using
our own LDAP server that you can spin up in a container by executing:

```
# Install docker if you don't have it
# For Ubuntu
apt install docker-ce

# Start LDAP server container with pre-loaded data
docker run -p 3389:389 -p 6636:636 --name openldap-server --detach bgmot42/openldap-server:0.1.1
```

All users (including `ldap_search`) in this test LDAP server for simplicity
have the word `password` as their passwords.

Users `user1` and `user2` is a member of `zabbix-admins` LDAP group. User
`user3` is a member of `zabbix-users` LDAP group.

???+ Optional

    To visually see LDAP server data (and add your own configuration like users
    and groups) you can start this standard container
    `docker run -p 8081:80 -p 4443:443 --name phpldapadmin --hostname phpldapadmin\
    --link openldap-server:ldap-host --env PHPLDAPADMIN_LDAP_HOSTS=ldap-host\
    --detach osixia/phpldapadmin:0.9.0`
    Now you can access this LDAP server via https://<ip_address>:4443 (or any
    other port you configure to access this Docker container), click Login,
    enter “cn=admin,dc=example,dc=org” in Login DN field and “password” in
    Password field, click Authenticate. You should see the following structure
    of the LDAP server (picture shows ‘zabbix-admins’ group configuration):

    ![LDAP server data](ch02.4-ldap-ldap-server-data.png){ align=center }

    _2.4 LDAP server data_

Let's configure LDAP server settings in Zabbix. In Zabbix menu select
`Users | Authentication | LDAP settings`, then check the check-box
`Enable LDAP authentication` and click `Add` under `Servers` (change IP address
of your LDAP server and port number according to your set up):

![LDAP server settings in Zabbix](ch02.5-ldap-server-settings-in-zabbix.png){ align=center }

_2.5 LDAP server settings in Zabbix_

Following diagram can help you understand how to configure LDAP server in
Zabbix based on your LDAP server data structure:

![LDAP server to Zabbix](ch02.6-ldap-server-to-zabbix.png){ align=center }

_2.6 LDAP server to Zabbix_

“Special” _Distinguished Name_ (DN) _cn=ldap_search,dc=example,dc=org_ is used
for searching, i.e. Zabbix uses this DN to connect to LDAP server and of course
when you connect to LDAP server you need to be authenticated – this is why you
need to provide _Bind password_. This DN should have access to a sub-tree in
LDAP data hierarchy where all your users are configured. In our case all the
users configured “under” _ou=Users,dc=example,dc=org_, this DN is called base
DN and used by Zabbix as so to say “starting point” to start searching.

???+ Note

    technically it is possible to bind to LDAP server anonymously, without
    providing a password but this is a huge breach in security as the whole
    users sub-tree becomes available for anonymous (unauthenticated) search,
    i.e. effectively exposed to any LDAP client that can connect to LDAP server
    over TCP. The LDAP server we deployed previously in Docker container does
    not provide this functionality.

Click `Test` button and enter `user1` and `password` in the respective fields, the
test should be successful confirming Zabbix can authenticate users against LDAP
server.

???+ Note

    We can add multiple LDAP servers and use them for different `User groups`.

To test real users login using LDAP authentication we need to create user
groups and users in Zabbix. In Zabbix menu select `Users | User groups`. Make
sure `Zabbix administrators` group exists (we'll need it later) and create new
group `Zabbix users` by clicking `Create user group` button. Enter "Zabbix
users" in `Group name` field, select "LDAP" in `Frontend access` drop-down that
will make Zabbix to authenticate users belonging to this group against LDAP
server and in `LDAP server` drop-down select LDAP server we earlier configured
"Test LDAP server". Click `Add` button to create this User group:

![Add user group in zabbix](ch02.7-ldap-add-user-group-in-zabbix.png){ align=center }

_2.7 Add user group in zabbix_

Now we need to create our test user. In Zabbix menu select `Users | Users` and
click `Create user` button. Then enter "user3" in `Username` field. Select
"Zabbix users" in `Groups` field. What you enter in `Password` and `Password
(once again)` fields does not matter as Zabbix will not try to use this
password, instead it will go to LDAP server to authenticate this user since
it's a member of the User group that has authentication method `LDAP`, just
make sure you enter the same string in these two fields and it satisfied your
password strength policy defined in `Users | Authentication`.

![Add user in Zabbix](ch02.8-ldap-add-user-in-zabbix.png){ align=center }

_2.8 Add user in Zabbix_

Then click `Permissions` tab and select "User role" in `Role` field:

![Add user in Zabbix - permissions](ch02.9-ldap-add-user-in-zabbix-permissions.png){ align=center }

_2.9 Add user in Zabbix - permissions_

Click `Add` button to create the user.

We are ready to test our LDAP server authentication! Click `Sign out` in Zabbix
menu and login with "user3" as Username and "password" as `Password`, if you
carefully followed the steps above you should successfully login with User role
permissions.

Click `Sign out` again and login as Admin again to proceed.

### Just-in-Time user provisioning

Now let's talk about really cool feature Zabbix provides - "Just-in-Time user
provisioning (JIT) available since Zabbix 6.4.

This picture illustrates on high level how it works:
![LDAP JIT explained](ch02.10-ldap-jit-explained.png){ align=center }

_2.10 LDAP JIT explained_

Here when Zabbix gets a username and password from the Zabbix Login form it
goes to the LDAP server and gets all the information available for this user
including his/her LDAP groups membership and e-mail address. Obviously, it
gets all that only if the correct (from LDAP server perspective) username and
password were provided. Then Zabbix goes through pre-configured mapping that
defines users from which `LDAP group` goes to which `Zabbix user group`. If at
least one match is found then a `Zabbix user` is created in the Zabbix database
belonging to a `Zabbix user group` and having a `Zabbix user role` according to
configured “match”. So far sounds pretty simple, right? Now let’s go into
details about how all this should be configured.

In `Users | Authentication` we need to do two things:

- Set `Default authentication` to _LDAP_. When JIT is turned off then type of
  authentication is defined based on the _User group_ a user that tries to login
  belongs to. In case of JIT the user does not exist in Zabbix yet thus obviously
  does not belong to any _User group_ so _Default_ method authentication is used
  and we want it to be _LDAP_.

- Provide `Deprovisioned users group`. This group must be literally _disabled_
  otherwise you won't be able to select it here. This is the Zabbix user group
  where all _de-provisioned_ users will be put into so effectively will get
  disabled from accessing Zabbix.

  ![Default authentication](ch02.11-ldap-default-authentication.png){ align=center }

  _2.11 Default authentication_

  Click `Update` button`.

- Enable JIT provisioning check-box which obviously needs to be checked for this
  feature to work. It's done in our _Test LDAP server_ configuration - select
  `Users | Authentication | LDAP settings` and click on our server in `Servers`
  section. After enabling this check-box we'll see some other fields related to
  JIT to be filled in and what we put in there depends on the method we choose to
  perform JIT.

#### Group configuration method “memberOf”

All users in our LDAP server have _memberOf_ attribute which defines what LDAP
groups every user belongs to, e.g. if we perform a LDAP query for _user1_ user
we’ll get that its _memberOf_ attribute has this value:

**memberOf**: cn=**zabbix-admins**,ou=Group,dc=example,dc=org

Note, that your real LDAP server can have totally different LDAP attribute that
provides users’ group membership, and of course, you can easily configure what
attribute to use when searching for user’s LDAP groups by putting it into `User
group membership attribute` field:

![LDAP groups mapping](ch02.12-ldap-groups-mapping.png){ align=center }

_2.12 LDAP groups mapping_

In the picture above we are telling Zabbix to use _memberOf_ attribute to
extract DN defining user’s group membership (in this case it is
_cn=zabbix-admins,out=Group,dc=example,dc=org_) and take only _cn_ attribute
from that DN (in this case it is _zabbix-admins_) to use in searching for a
match in User group mapping rules. Then we define as many mapping rules as we
want. In the picture above we have two rules:

- All users belonging to _zabbix-users_ LDAP group will be created in Zabbix as
  members of _Zabbix users group_ with _User_ role
- All users belonging to _zabbix-admins_ LDAP group will be created in Zabbix
  as members of _Zabbix administrators_ group with _Super admin_ role

#### Group configuration method “groupOfNames”

There is another method of finding users’ group membership called
“groupOfNames” it is not as efficient as “memberOf” method but can provide much
more flexibility if needed. Here Zabbix is not querying LDAP server for a user
instead it is searching for LDAP groups based on a given criterion (filter).
It’s easier to explain with pictures depicting an example:

![LDAP server group of names](ch02.13-ldap-group-of-names.png){ align=center }

_2.13 LDAP server groupOfNames_

Firstly we define LDAP “sub-tree” where Zabbix will be searching for LDAP
groups – note _ou=Group,dc=example,dc=org_ in Group base DN field. Then in the
field `Group name attribute` field we what attribute to use when we search in
mapping rules (in this case we take _cn_, i.e. only _zabbix-admins_ from full
DN _cn=zabbix-admins,ou=Group,dc=example,dc=org_). Each LDAP group in our LDAP
server has _member_ attribute that has all users that belong to this LDAP group
(look at the right picture) so we put _member_ in `Group member attribute`
field. Each user’s DN will help us construct `Group filter` field. Now pay
attention: `Reference attribute` field defines what LDAP user’s attribute
Zabbix will use in the `Group filter`, i.e. _%{ref}_ will be replaced with the
value of this attribute (here we are talking about the user’s attributes – we
already authenticated this user, i.e. got all its attributes from LDAP server).
To sum up what I've said above Zabbix:

1. Authenticates the user with entered Username and Password against LDAP
   server getting all user’s LDAP attributes
2. Uses `Reference attribute` and `Group filter` fields to construct a filter
   (when user1 logs in the filter will be (_member=uid=user1,ou=Users,dc=example,
   dc=org_)
3. Performs LDAP query to get all LDAP groups with member attribute (configured
   in `Group member attribute` field) containing constructed in step 2) filter
4. Goes through all LDAP groups received in step 3) and picks `cn` attribute
   (configured in `Group name attribute` field) and finds a match in User group
   mapping rules

Looks a bit complicated but all you really need to know is the structure of
your LDAP data.

#### Ready to test

Now when you login with _user1_ or _user2_ username then these users will be
created by Zabbix and put into _Zabbix administrators_ user group, when you
login with _user3_ username then this user will be created by Zabbix and put
into _Zabbix users_ user group:

![Test user1](ch02.14-ldap-jit-test-user1.png){ align=center }

_2.14 Test user1_

![Test user3](ch02.15-ldap-jit-test-user3.png){ align=center }

_2.15 Test user3_

## SAML

---

### Google

Integrating Security Assertion Markup Language (SAML) for authentication within
Zabbix presents a non-trivial configuration challenge. This process necessitates
meticulous management of cryptographic certificates and the precise definition
of attribute filters. Furthermore, the official Zabbix documentation, while
comprehensive, can initially appear terse.

#### Initial Configuration: Certificate Generation

The foundational step in SAML integration involves the generation of a `private key`
and a corresponding X.509 certificate. These cryptographic assets are critical
for establishing a secure trust relationship between Zabbix and the Identity Provider
(IdP).

By default, Zabbix expects these files to reside within the `ui/conf/certs/`
directory. However, for environments requiring customized storage locations, the
zabbix.conf.php configuration file allows for the specification of alternative
paths.

Let's create our private key and certificate file.

```bash
cd /usr/share/zabbix/ui/conf/certs/
openssl req -newkey rsa:2048 -nodes -keyout sp.key -x509 -days 365 -out sp.crt
```

Following the generation and placement of the Zabbix Service Provider (SP) certificates,
the next critical phase involves configuring the Identity Provider (IdP). In this
context, we will focus on Google Workspace as the IdP.

Retrieving the IdP Certificate (idp.crt) from Google Workspace:

1. **Access the Google Workspace Admin Console:** Log in to your Google Workspace
   administrator account.
2. **Navigate to Applications:** Within the admin console, locate and select the
   "Apps" section.
3. **Access Web and Mobile Apps:** Choose `Web and mobile apps` from the available
   options.
4. **Create a New Application:** Initiate the creation of a new application to
   facilitate SAML integration. This action will trigger Google Workspace to generate
   the necessary IdP certificate.
   ![Add google app](ch02.16-add-google-app.png)

_2.16 create
new application_

5. **Download the IdP Certificate:** Within the newly created application's settings,
   locate and download the idp.crt file. This certificate is crucial for establishing
   trust between Zabbix and Google Workspace.
6. **Placement of idp.crt:** Copy the downloaded `idp.crt` file to the same directory
   as the SP certificates in Zabbix, under `ui/conf/certs/`.

![Add google app](ch02.17-saml-download.png)

_2.17 add
certificate_

---

#### SAML Attribute Mapping and Group Authorization

A key aspect of SAML configuration is the mapping of attributes between Google
Workspace and Zabbix. This mapping defines how user information is transferred
and interpreted.

**Attribute Mapping:**

- It is strongly recommended to map the Google Workspace "Primary Email" attribute
  to the Zabbix "Username" field. This ensures seamless user login using their
  Google Workspace email addresses.
- Furthermore, mapping relevant Google Workspace group attributes allows for granular
  control over Zabbix user access. For instance, specific Google Workspace groups
  can be authorized to access particular Zabbix resources or functionalities.

**Group Authorization:**

- Within the Google Workspace application settings, define the groups that are
  authorized to utilize SAML authentication with Zabbix.
- This configuration enables the administrator to control which users can use
  SAML to log into Zabbix.
- In Zabbix, you will also need to create matching user groups and configure
  the authentication to use those groups.

**Configuration Example (Conceptual):**

- Google Workspace Attribute: "Primary Email" -> Zabbix Attribute: "Username"
- Google Workspace Attribute: "Group Membership" -> Zabbix Attribute: "User Group"

This attribute mapping ensures that users can log in using their familiar Google
Workspace credentials and that their access privileges within Zabbix are determined
by their Google Workspace group memberships.

![saml mappings](ch02.18-saml-mappings.png)

_2.18 SAML
mappings_

---

#### Zabbix SAML Configuration

With the IdP certificate and attribute mappings established within Google Workspace,
the final step involves configuring Zabbix to complete the SAML integration.

**Accessing SAML Settings in Zabbix:**

- **Navigate to User Management:** Log in to the Zabbix web interface as an administrator.
- **Access Authentication Settings:** Go to "Users" -> "Authentication" in the
  left-hand menu.
- **Select SAML Settings:** Choose the "SAML settings" tab.

**Configuring SAML Parameters:**

Within the "SAML settings" tab, the following parameters must be configured:

- **IdP Entity ID:** This value uniquely identifies the Identity Provider
  (Google Workspace in this case). It can be retrieved from the Google Workspace
  SAML configuration metadata.
- **SSO Service URL:** This URL specifies the endpoint where Zabbix should send
  authentication requests to Google Workspace. This URL is also found within the
  Google Workspace SAML configuration metadata.
  - **Retrieving Metadata:** To obtain the IdP entity ID and SSO service URL, within
    the Google Workspace SAML application configuration, select the option to `Download
metadata`. This XML file contains the necessary values.
- **Username Attribute:** Set this to "username." This specifies the attribute
  within the SAML assertion that Zabbix should use to identify the user.
- **SP Entity ID:** This value uniquely identifies the Zabbix Service Provider.
  It should be a URL or URI that matches the Zabbix server's hostname.
- **Sign:** Select `Assertions`. This configures Zabbix to require that the SAML
  assertions from Google Workspace are digitally signed, ensuring their integrity.

Example Configuration (Conceptual)

- IdP entity ID: [https://accounts.google.com/o/saml2?idpid=your_idp_id](https://accounts.google.com/o/saml2?idpid=your_idp_id)
- SSO service URL: [https://accounts.google.com/o/saml2/idp/SSO?idpid=your_idp_id&SAMLRequest=your_request](https://accounts.google.com/o/saml2/idp/SSO?idpid=your_idp_id&SAMLRequest=your_request)
- Username attribute: username
- SP entity ID: https://your_zabbix_server/zabbix
- Sign: Assertions

![google saml config](ch02.19-saml-zabbix-options.png)

_2.19 SAML
config_

**Additional Configuration Options:**

The Zabbix documentation provides a comprehensive overview of additional SAML
configuration options. Consult the official Zabbix documentation for advanced settings,
such as attribute mapping customization, session timeouts, and error handling configurations.

**Verification and Testing:**

After configuring the SAML settings, it is crucial to thoroughly test the integration.
Attempt to log in to Zabbix using your Google Workspace credentials. Verify that
user attributes are correctly mapped and that group-based access control is
functioning as expected.

**Troubleshooting:**

If authentication fails, review the Zabbix server logs and the Google Workspace
audit logs for potential error messages. Ensure that the certificate paths are
correct, the attribute mappings are accurate, and the network connectivity between
Zabbix and Google Workspace is stable.

#### SAML Media Type mappings

After successfully configuring SAML authentication, the final step is to integrate
media type mappings directly within the SAML settings. This ensures that media
delivery is dynamically determined based on SAML attributes.

**Mapping Media Types within SAML Configuration:**

- **Navigate to SAML Settings:** In the Zabbix web interface, go to "Users" ->
  "Authentication" and select the "SAML settings" tab.
- **Locate Media Mapping Section:** Within the SAML settings, look for the section
  related to media type mapping. This section might be labeled "Media mappings"
  or similar.
- **Add Media Mapping:** Click "Add" to create a new media type mapping.
- **Select Media Type:** Choose the desired media type, such as "Gmail relay."
- **Specify Attribute:** In the attribute field, enter the SAML attribute that
  contains the user's email address (typically "username," aligning with the
  primary email attribute mapping).
- **Configure Active Period :** Specify the active period for this media type.
  This allows for time-based control of notifications.
- **Configure Severity Levels:** Configure the severity levels for which this
  media type should be used.

Example Configuration (Conceptual):

- Media Type: Gmail relay
- Attribute: username
- Active Period: 08:00-17:00 (Monday-Friday)
- Severity Levels: High, Disaster

Rationale:

By mapping media types directly within the SAML configuration, Zabbix can dynamically
determine the appropriate media delivery method based on the SAML attributes received
from the IdP. This eliminates the need for manual media configuration within individual
user profiles when SAML authentication is in use.

Key Considerations:

- Ensure that the SAML attribute used for media mapping accurately corresponds to
  the user's email address.
- Verify that the chosen media type is correctly configured within Zabbix.
- Consult the Zabbix documentation for specific information about the SAML media
  mapping functionality, as the exact configuration options may vary depending on
  the Zabbix version.

#### Final Configuration: Frontend Configuration Adjustments

After configuring the SAML settings within the Zabbix backend and Google Workspace,
the final step involves adjusting the Zabbix frontend configuration. This ensures
that the frontend correctly handles SAML authentication requests.

Modifying `zabbix.conf.php`:

- **Locate Configuration File**: Access the Zabbix frontend configuration file,
  typically located at /etc/zabbix/web/zabbix.conf.php.

- **Edit Configuration:** Open the zabbix.conf.php file using a text editor with
  root or administrative privileges.

- **Configure SAML Settings:** Within the file, locate or add the following
  configuration directives:

`php
// Uncomment to override the default paths to SP private key, SP and IdP X.509 certificates,
// and to set extra settings.
$SSO['SP_KEY']                  = 'conf/certs/sp.key';
$SSO['SP_CERT']                 = 'conf/certs/sp.crt';
$SSO['IDP_CERT']                = 'conf/certs/idp.crt';
//$SSO['SETTINGS']              = [];
`

---

### MS Cloud

---

### Okta

---

## Multi factor authentication

We all know that before you can start configuring Zabbix via WebUI you have to
sign in. Zabbix has several options to provide better security for user passwords
by configuring password policy:

- Requirement for Minimum password length
- Requirements for password to contain an uppercase and a lowercase Latin letter,
  a digit, a special character
- Requirement to avoid easy-to-guess passwords

To secure sign in process even more you can configure multi factor authentication
(MFA). MFA protects Zabbix by using a second source of validation before granting
access to its WebUI after a user enters his/her password correctly. Zabbix offers
to types of MFA - Time-based one-time password (TOTP) and Duo MFA provider.

---

### Time-based one-time password

In the menu select `Users` section and then `Authentication`

![MFA Settings initial](ch02.20-mfa_settings_initial.png){ width=90% }

_2.20 Initial MFA settings_

Now in `MFA settings` tab select the `Enable multi-factor authentication` check-box,
then select `TOTP` in Type drop-down list.

![MFA Settings TOTP](ch02.21-mfa_settings_TOTP_new.png){ width=90% }

_2.21 New MFA method_

In `Hash function` drop-down list you can choose SHA-1, SHA-256 or SHA-512, the higher
number is the better security.

In `Code lentgh` you can select how many digits will be generated for you by Authenticator
application on your phone.

Click `Add` and then `Update`. Now you have TOTP MFA configured and it is the default
method of MFA.

![MFA Settings TOTP configured](ch02.22-mfa_settings_TOTP_configured.png){ width=90% }

_2.22 New MFA method added_

Now you need to tell Zabbix for which User group (or groups) to use MFA. Let's create
a User group that would require MFA.

In the menu select `Users` section and then `User groups`, then click `Create user
group` button

![MFA list of user groups](ch02.23-mfa_create_user_groups.png){ width=90% }

_2.23 Create user group_

In `Group name` put "test". Note that `Multi-factor authentication` field is "Default",
as currently we have only one MFA method configured it does not matter whether we
select "Default" or "TOTP1" that we created above. You also can disable MFA for
all users belonging to this User group. Click `Add` button to create "test" User
group.

![MFA new user group](ch02.24-mfa_new_user_group.png){ width=90% }

_2.24 New user group configuration_

???+ Note

    MFA method is defined on per User group basis, i.e. MFA method configured for
    a User group will be applied to all users belonging to this group.

Let's add a user to this user group. In the menu select `Users` section and then
`Users`, then click `Create user` button

![MFA create user](ch02.25-mfa_create_user.png){ width=90% }

_2.25 Create user_

Fill in `Username`, `Password` and `Password (once again)` fields. Make sure you
select `test` user group in `Groups` field.

![MFA new user](ch02.26-mfa_new_user.png){ width=90% }

_2.26 New user configuration_

Then switch to `Permissions` tab and select any role.

![MFA new user permissions](ch02ю27-mfa_new_user_permissions.png){ width=90% }

_2.27 New user permissions_

Click `Add` button to add the user.

Now we can test how TOTP MFA works. Sign out and then try to sign in as a test user
you just created. You will be presented with a QR code. That means that the user
`test` has not been enrolled in TOTP MFA yet.

![MFA TOTP QR code](ch02.28-mfa_totp_qr_code.png){ width=30% }

_2.28 TOTP QR code_

On your phone you need to install either "Microsoft authenticator" or "Google authenticator"
application. The procedure of adding new QR code is quite similar, here is how it
looks in "Google authenticator". Tap `Add a code` and then `Scan a QR code`. You'll
be immediately presented with a 6 digit code (remember we selected 6 in `Code length`
when we configured TOTP MFA?)

![MFA TOTP auth app1](ch02.29-mfa_totp_auth_app1.png){ width=32% }

_2.29 Authenticator app, step 1_

![MFA TOTP auth app2](ch02.30-mfa_totp_auth_app2.png){ width=32% }

_2.30 Authenticator app, step 2_

![MFA TOTP auth app3](ch02.31-mfa_totp_auth_app3.png){ width=32% }

_2.31 Authenticator app, step 3_

Enter this code into `Verification code` field of your login screen and click
`Sign in`, if you did everything right you are logged in into Zabbix at this point.
At this point the user "test" is considered enrolled into TOTP MFA and Zabbix stores
a special code used for further authentications in its database. The next time
user "test" tries to login into Zabbix there will be only a field to enter
verification code

![MFA TOTP second login](ch02.32-mfa_totp_second_login.png){ width=32% }

_2.32 Verification code request_

???+ warning

    For TOTP MFA to work your Zabbix server must have correct time. Sometimes
    it's not the case especially if you are working with containers so pay attention
    to this.

If a user changes (or loses) his/her phone, then Zabbix administrator should reset
his/her enrolment. To do that in the menu select `Users` then mark a check-box to
the left of "test" user and click "Reset TOTP secret" button.

![MFA TOTP reset password](ch02.33-mfa_totp_reset_password.png){ width=99% }

_2.33 Reset TOTP secret_

After you reset TOTP secret the "test" user will have to undergo enrolment procedure
again.

---

### Duo MFA provider

Duo is a very famous security platform that provides a lot of security related features/products.
To read more please visit [Duo](https://duo.com/). Here we'll talk about Duo only
in regards to Zabbix MFA.

???+ warning

    For Duo MFA to work your Zabbix WebUI must be configured to work with HTTPS
    (valid certificate is not required, self-signed certificate will work).

First of all you need to create an account with Duo (it's free to manage up to
10 users) then login into Duo, you are an admin here. In the menu on the left select
`Applications` and click `Protect an Application` button.

![MFA DUO applications](ch02.34-mfa_duo_applications.png){ width=99% }

_2.34 DUO Applications menu_

Then you will see WebSDK in applications list, click on it

![MFA DUO applications list](ch02.35-mfa_duo_applications_list.png){ width=99% }

_2.35 DUO Applications list_

Here you'll see all the data needed for Zabbix.

![MFA DUO ](ch02.36-mfa_duo_data.png){ width=99% }

_2.36 DUO WebSDK application settings_

Now let's go to Zabbix. First we need to configure Duo MFA method. In the menu select
`Users` and click `Authentication`. Then on `MFA settings` tab click `Add` in
`Methods` section.

![MFA DUO ](ch02.37-mfa_duo_add_method.png){ width=99% }

_2.37 Add MFA method_

Fill in all the fields with data from Duo Dashboard -> Applications -> Web SDK page
(see screenshot above) and click `Add`, then click `Update` to update Authentication
settings.

![MFA DUO ](ch02.38-mfa_duo_method_data.png){ width=99% }

_2.38 DUO method settings_

After the MFA method is configured let's switch the "Test" group to use Duo MFA.
In the menu select `Users` and click `User groups`, then click "test" group. In
the field `Multi-factor authentication` select "DUO1" and click `Update`.

![MFA DUO ](ch02.39-mfa_duo_user_group.png){ width=99% }

_2.39 DUO MFA authentication method for user group_

Everything is ready. Let's test it. Sign out of Zabbix and sign back in with "test"
user. You should see a welcome screen from Duo. Click several `Next` buttons.

![MFA DUO ](ch02.40-mfa_duo_welcome.png){ width=32% }

_2.40 Enrollling into DUO, step1_

![MFA DUO ](ch02.41-mfa_duo_welcome1.png){ width=32% }

_2.41 Enrollling into DUO, step2_

![MFA DUO ](ch02.42-mfa_duo_welcome2.png){ width=32% }

_2.42 Enrollling into DUO, step3_

Then you need to select the method of authentication.

![MFA DUO ](ch02.43-mfa_duo_auth_method.png){ width=50% }

_2.43 Enrollling into DUO, step4_

It is up to you what to select you can experiment with all these methods. Let's
select "Duo Mobile" (you need to install "Duo mobile" application on your device).
Click `I have a tablet` (it's just easier to activate your device this way) and
confirm that you installed "Duo mobile" on your phone. At this point you should
see a QR code that you need to scan in "Duo mobile" application.

![MFA DUO ](ch02.44-mfa_duo_duo_app.png){ width=32% }

_2.44 Enrollling into DUO, step5_

![MFA DUO ](ch02.45-mfa_duo_confirm_app_installed.png){ width=32% }

_2.45 Enrollling into DUO, step6_

![MFA DUO ](ch02.46-mfa_duo_scan_qr.png){ width=32% }

_2.46 Enrollling into DUO, step7_

Open "Duo mobile" on your phone. If you did not have this application previously
installed (thus no accounts enrolled) you will see couple of welcome screens.

![MFA DUO ](ch02.47-mfa_duo_phone_welcome.png){ width=48% }

_2.47 Configure DUO app, step 1_

![MFA DUO ](ch02.48-mfa_duo_phone_add_account.png){ width=48% }

_2.48 Configure DUO app, step 2_

Tap on "Use a QR code" and then scan the code presented by Duo in your Zabbix login
screen. After you do that you will see that the account is enrolled to your Duo
MFA. Enter account name and tap "Done" and you will see the account in the list
of all accounts enrolled into Duo MFA on this device. In Zabbix WebUI you will
also see a confirmation, click "Continue".

![MFA DUO ](ch02.49-mfa_duo_phone_account_added.png){ width=32% }

_2.49 Configure DUO app, step 3_

![MFA DUO ](ch02.50-mfa_duo_phone_accounts.png){ width=32% }

_2.50 Configure DUO app, step 4_

![MFA DUO ](ch02.51-mfa_duo_enrollement_confirmation.png){ width=32% }

_2.51 Enrollment confirmation_

Duo will ask you now whether you want to add another method of authentication,
click `Skip for now` and you'll see a confirmation that set up completed. Click
`Login with Duo` and a notification will be pushed to your device.

![MFA DUO ](ch02.52-mfa_duo_another_method.png){ width=32% }

_2.52 Add another way to login_

![MFA DUO ](ch02.53-mfa_duo_setup_completed.png){ width=32% }

_2.53 MFA DUO set up completed_

![MFA DUO ](ch02.54-mfa_duo_push_sent.png){ width=32% }

_2.54 DUO push notification sent_

Now just tap on "Approve" on your device and you will be logged in into Zabbix.

![MFA DUO ](ch02.55-mfa_duo_phone_push_notification.png){ width=50% }

_2.55 DUO push notification on the phone_

Duo MFA enrolment complete. If you sign out and sign in back then immediately a
push notification will be sent to your device and all you need is tap on
"Approve". Also you will see the user "test" in Duo where you can delete the user,
or deactivate just click on it and experiment.

![MFA DUO ](ch02.56-mfa_duo_users.png){ width=98% }

_2.56 New user registered in DUO_

## Conclusion

In conclusion, integrating external authentication mechanisms like SAML with Zabbix
significantly enhances security and streamlines user management. While the configuration
process involves meticulous steps across both the Zabbix backend and frontend,
as well as the external Identity Provider, the benefits are substantial. By centralizing
authentication, organizations can enforce consistent access policies, simplify
user onboarding and offboarding, and improve overall security posture. Ultimately,
external authentication provides a robust and scalable solution for managing user
access within complex Zabbix environments.

## Questions

## Useful URLs

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http)

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/ldap](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/ldap)

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/saml](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/saml)

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa)
