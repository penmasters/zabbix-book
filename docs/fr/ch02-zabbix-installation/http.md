---
description : | Cette section du livre Zabbix, intitulée "Authentification
HTTP", explique comment sécuriser l'accès au frontend de Zabbix en utilisant les
méthodes d'authentification de serveur web. Elle couvre la configuration avec
Apache ou Nginx, l'intégration avec Zabbix, et comment l'authentification HTTP
ajoute une couche de protection supplémentaire à votre environnement de
surveillance.
---

# HTTP

L'authentification HTTP est l'une des méthodes d'authentification externe
fournies par Zabbix et peut être utilisée pour sécuriser davantage votre
interface Web Zabbix avec un mécanisme d'authentification de base au niveau du
serveur HTTP.

L'authentification HTTP de base protège les ressources du site Web (Zabbix
WebUI) avec un nom d'utilisateur et un mot de passe. Lorsqu'un utilisateur tente
d'accéder à Zabbix WebUI, le navigateur affiche une boîte de dialogue demandant
des informations d'identification avant d'envoyer quoi que ce soit au code php
de Zabbix WebUI.

Un serveur HTTP dispose d'un fichier contenant des informations d'identification
utilisées pour authentifier les utilisateurs.

???+ note

    IMPORTANT: usernames configured for basic authentication in HTTP server
    must exit in Zabbix. But only passwords configured in HTTP server are used
    for users authentication.

Voyons d'abord comment configurer l'authentification de base dans le serveur
HTTP.

???+ warning

    The examples below provide just minimum set of options to configure
    basic authentication. Please refer to respective HTTP server documentation
    for more details

## Authentification de base dans Nginx

Trouvez le bloc `location / {` dans les fichiers de configuration de Nginx, qui
définit votre WebUI Zabbix (ie : `/etc/nginx/conf.d/nginx.conf` file) et ajoutez
ces deux lignes :

```
    location / {
        ...
        auth_basic "Basic Auth Protected Site";
        auth_basic_user_file /etc/nginx/httpauth;
    }
```

N'oubliez pas de redémarrer le service Nginx après avoir effectué cette
modification.

Ensuite, vous devez créer `/etc/nginx/httpauth` un fichier qui contiendra les
mots de passe de tous les utilisateurs (assurez-vous de restreindre l'accès à ce
fichier). Le format de ce fichier est `nom_utilisateur :mot_de_passe_haché`, par
exemple, pour les utilisateurs `Admin` et `test` :

```
Admin:$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
test:$1$GXoDIOCA$u/n1kkDeFwcI4KhyHkY6p/
```

Pour générer un mot de passe haché, vous pouvez utiliser l'outil `openssl` en
entrant le mot de passe deux fois :
```
openssl passwd
Password:
Verifying - Password:
$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
```

## Authentification de base dans Apache HTTPD

Trouvez le bloc `<Directory "/usr/share/zabbix">` dans le fichier de
configuration Apache HTTP, il définit votre WebUI Zabbix (ie :
`/etc/zabbix/apache.conf`) et ajoutez ces lignes :

???+ note La configuration par défaut est `Require all granted`, supprimez cette
ligne.

Pour Ubuntu/Debian :
```
    <Directory "/usr/share/zabbix">
        ...
        AuthType Basic
        AuthName "Restricted Content"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Directory>
```

Pour RedHat :
```
    <Directory "/usr/share/zabbix">
        ...
        AuthType Basic
        AuthName "Restricted Content"
        AuthUserFile /etc/httpd/.htpasswd
        Require valid-user
    </Directory>
```

N'oubliez pas de redémarrer le service apache2 après avoir effectué cette
modification.

Créez le fichier `/etc/apache2/.httpasswd` (`/etc/httpd/.htpassword` pour
RedHat) qui contiendra tous les utilisateurs avec leurs mots de passe, en
utilisant l'outil `htpasswd`, pour ajouter l'utilisateur `test` exécuter :

Pour Ubuntu/Debian
```
sudo htpasswd -c /etc/apache2/.htpasswd test
New password: 
Re-type new password: 
Adding password for user test
```

Pour RedHat
```
sudo htpasswd -c /etc/httpd/.htpasswd test
New password: 
Re-type new password: 
Adding password for user test
```

Pour ajouter d'autres utilisateurs au fichier, répétez la commande sans l'option
`-c`.

## Configuration de Zabbix pour l'authentification HTTP

Une fois le serveur WEB configuré avec l'authentification de base, il est temps
de configurer le serveur Zabbix. Dans le menu Zabbix, sélectionnez `Users |
Authentication | HTTP settings` et cochez la case `Enable HTTP authentication`.
Cliquez sur `Update` et confirmez les changements en cliquant sur `OK`.

![Authentification des utilisateurs HTTP](ch02.1-http-auth-settings.png){
align=center }

_2.1 Authentification des utilisateurs HTTP_

`Remove domain name` Le champ doit contenir une liste de domaines séparés par
des virgules que Zabbix supprimera du nom d'utilisateur fourni. Par exemple, si
un utilisateur entre "test@myzabbix" ou "myzabbix\test" et que nous avons
"myzabbix" dans ce champ, l'utilisateur sera connecté avec le nom d'utilisateur
"test".

Décocher la case `Case-sensitive login` indiquera à Zabbix de ne pas tenir
compte des majuscules/minuscules dans les noms d'utilisateur, par exemple "tEst"
et "test" deviendront des noms d'utilisateur tout aussi légitimes même si dans
Zabbix nous n'avons que l'utilisateur "test" de configuré.

Notez que le `formulaire de connexion par défaut` est réglé sur "Zabbix login
form". Maintenant, si vous vous déconnectez, vous verrez le lien "Sign in with
HTTP" (se connecter avec HTTP) sous les champs Username (nom d'utilisateur) et
Password (mot de passe). Si vous cliquez sur ce lien, vous serez automatiquement
connecté à Zabbix WebUI avec le même nom d'utilisateur que celui que vous avez
utilisé précédemment. Vous pouvez également saisir un nom d'utilisateur et un
mot de passe différents et vous connecter normalement à Zabbix WebUI en tant
qu'utilisateur différent.

[HTTP users authentication login](ch02.2-http-auth-login.png){ align=center }

_2.2 Formulaire d'authentification des utilisateurs HTTP_

Si vous sélectionnez "HTTP login form" dans le menu déroulant `Default login
form`, vous ne verrez pas le formulaire de connexion standard de Zabbix lorsque
vous essayerez de vous déconnecter. En fait, vous ne pourrez pas vous
déconnecter à moins que votre session d'authentification n'expire. La seule
façon de se déconnecter est d'effacer les cookies dans votre navigateur. Vous
devrez alors suivre à nouveau la procédure d'authentification de base du serveur
Web.

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

- Quel est l'avantage de l'authentification HTTP (basée sur le serveur web) par
  rapport au mécanisme d'authentification interne de Zabbix ? (Pensez à la
  protection au niveau du serveur web avant même que l'utilisateur n'atteigne
  l'interface utilisateur de Zabbix).

- Pourquoi est-il essentiel qu'un utilisateur existe dans Zabbix même lorsque
  l'authentification HTTP est activée et pourquoi le mot de passe Zabbix
  n'est-il pas pertinent dans ce cas ?

- Quelles sont les options de configuration dans le frontend de Zabbix sous
  "Administration → Authentification" pour l'authentification HTTP, et comment
  chacune d'entre elles peut-elle affecter le comportement de connexion ? Les
  exemples incluent l'activation/désactivation de la sensibilité à la casse, la
  suppression du domaine et le choix du formulaire de connexion.

- Supposons que vous désactiviez la sensibilité à la casse des logins et que
  vous mainteniez les deux comptes 'Admin' et 'admin' dans Zabbix. Comment
  l'authentification HTTP se comportera-t-elle, et à quel résultat devez-vous
  vous attendre ?

- Imaginez la résolution d'un problème d'échec de connexion lors de
  l'utilisation de l'authentification HTTP : Quelles mesures prendriez-vous pour
  vous assurer que l'authentification du serveur web est configurée correctement
  avant d'examiner les paramètres de Zabbix ?

- From a security standpoint, when would HTTP authentication alone be
  insufficient and what other authentication methods (e.g., LDAP, SAML, MFA)
  might you layer on top for added security?

## URL utiles

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http)
