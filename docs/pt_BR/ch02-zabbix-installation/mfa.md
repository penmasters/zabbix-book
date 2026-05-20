---
descripton: |
    This section from The Zabbix Book, titled "Duo MFA Provider," explains how
    to integrate Duo Security with Zabbix for multi-factor authentication. It
    covers setup, configuration, and login testing, adding an extra security
    layer to protect access to the Zabbix frontend.
tags: [advanced]
---

# Autenticação multifatorial

Todos nós sabemos que, antes de começar a configurar o Zabbix via WebUI, é
necessário fazer o login. O Zabbix tem várias opções para fornecer melhor
segurança para as senhas dos usuários, configurando a política de senha:

- Requisito para o tamanho mínimo da senha
- Requisitos para que a senha contenha uma letra latina maiúscula e uma
  minúscula, um dígito e um caractere especial
- Requisito para evitar senhas fáceis de adivinhar

Para proteger ainda mais o processo de login, você pode configurar a
autenticação multifator (MFA). A MFA protege o Zabbix usando uma segunda fonte
de validação antes de conceder acesso à sua WebUI depois que um usuário digita
sua senha corretamente. O Zabbix oferece dois tipos de MFA - Time-based one-time
password (TOTP) e Duo MFA provider.

---

## Senha de uso único baseada em tempo

No menu, selecione `Users` section e, em seguida, `Authentication`

![MFA Settings initial](ch02.20-mfa_settings_initial.png){ width=90% }

_2.20 Configurações iniciais do MFA_

Agora, na guia `MFA settings`, marque a caixa de seleção `Enable multi-factor
authentication` e, em seguida, selecione `TOTP` na lista suspensa Type.

![MFA Settings TOTP](ch02.21-mfa_settings_TOTP_new.png){ width=90% }

_2.21 Novo método MFA_

Na lista suspensa `Hash function`, você pode escolher SHA-1, SHA-256 ou SHA-512;
quanto maior o número, maior a segurança.

Em `Code lentgh`, você pode selecionar quantos dígitos serão gerados para você
pelo aplicativo Authenticator no seu telefone.

Clique em `Add` e depois em `Update`. Agora você tem o TOTP MFA configurado e
ele é o método padrão de MFA.

![Configurações de MFA TOTP
configuradas](ch02.22-mfa_settings_TOTP_configured.png){ width=90% }

_2.22 Novo método MFA adicionado_

Agora você precisa informar ao Zabbix para qual grupo de usuários (ou grupos)
usar a MFA. Vamos criar um grupo de usuários que exigiria a MFA.

No menu, selecione a seção `Users` e, em seguida, `User groups`, depois clique
no botão `Create user group`

![Lista MFA de grupos de usuários](ch02.23-mfa_create_user_groups.png){
width=90% }

_2.23 Criar grupo de usuários_

Em `Group name`, coloque "test". Observe que o campo `Multi-factor
authentication` é "Default" (Padrão), pois como atualmente temos apenas um
método MFA configurado, não importa se selecionamos "Default" (Padrão) ou
"TOTP1" que criamos acima. Você também pode desativar a MFA para todos os
usuários pertencentes a esse grupo de usuários. Clique no botão `Add` para criar
o grupo de usuários "test".

![MFA novo grupo de usuários](ch02.24-mfa_new_user_group.png){ width=90% }

_2.24 Nova configuração de grupo de usuários_

???+ Nota

    MFA method is defined on per User group basis, i.e. MFA method configured for
    a User group will be applied to all users belonging to this group.

Vamos adicionar um usuário a esse grupo de usuários. No menu, selecione a seção
`Users` e, em seguida, `Users`, depois clique no botão `Create user`

![MFA criar usuário](ch02.25-mfa_create_user.png){ width=90% }

_2.25 Criar usuário_

Preencha os campos `Nome de usuário`, `Senha` e `Senha (mais uma vez)`.
Certifique-se de selecionar o grupo de usuários `test` no campo `Groups`.

![MFA novo usuário](ch02.26-mfa_new_user.png){ width=90% }

_2.26 Nova configuração de usuário_

Em seguida, acesse a guia `Permissions` e selecione qualquer função.

![Permissões de novo usuário MFA](ch02.27-mfa_new_user_permissions.png){
width=90% }

_2.27 Novas permissões de usuário_

Clique no botão `Add` para adicionar o usuário.

Agora podemos testar como o TOTP MFA funciona. Saia e tente entrar como um
usuário de teste que você acabou de criar. Será apresentado a você um código QR.
Isso significa que o usuário `test` ainda não foi registrado no TOTP MFA.

![Código QR do MFA TOTP](ch02.28-mfa_totp_qr_code.png){ width=30% }

_2.28 Código QR TOTP_

Em seu telefone, é necessário instalar o aplicativo "Microsoft authenticator" ou
"Google authenticator". O procedimento para adicionar um novo código QR é
bastante semelhante; veja como fica no "Google authenticator". Toque em `Add a
code` e, em seguida, em `Scan a QR code`. Você verá imediatamente um código de 6
dígitos (lembra-se de que selecionamos 6 em `Comprimento do código` quando
configuramos o TOTP MFA?)

![MFA TOTP auth app1](ch02.29-mfa_totp_auth_app1.png){ width=32% }

_2.29 Aplicativo Authenticator, etapa 1_

![MFA TOTP auth app2](ch02.30-mfa_totp_auth_app2.png){ width=32% }

_2.30 Aplicativo Authenticator, etapa 2_

![MFA TOTP auth app3](ch02.31-mfa_totp_auth_app3.png){ width=32% }

_2.31 Aplicativo Authenticator, etapa 3_

Digite este código no campo `Verification code` da sua tela de login e clique em
`Sign in`, se você fez tudo certo, você está logado no Zabbix neste momento.
Nesse momento, o usuário "teste" é considerado inscrito no TOTP MFA e o Zabbix
armazena em seu banco de dados um código especial utilizado para outras
autenticações. Na próxima vez que o usuário "teste" tentar fazer o login no
Zabbix, haverá apenas um campo para inserir o código de verificação

![MFA TOTP segundo login](ch02.32-mfa_totp_second_login.png){ width=32% }

_2.32 Solicitação de código de verificação_

???+ Aviso

    For TOTP MFA to work your Zabbix server must have correct time. Sometimes
    it's not the case especially if you are working with containers so pay attention
    to this.

Se um usuário mudar (ou perder) seu telefone, então o administrador do Zabbix
deve redefinir sua inscrição. Para isso, no menu, selecione `Users` e marque a
caixa de seleção à esquerda do usuário "teste" e clique no botão "Reset TOTP
secret".

![MFA TOTP resetar a senha](ch02.33-mfa_totp_reset_password.png){ width=99% }

_2.33 Redefinir o segredo TOTP_

Depois de redefinir o segredo TOTP, o usuário de "teste" terá de passar
novamente pelo procedimento de registro.

---

## Provedor Duo MFA

A Duo é uma plataforma de segurança muito famosa que oferece muitos
recursos/produtos relacionados à segurança. Para saber mais, visite
[Duo](https://duo.com/). Aqui falaremos sobre a Duo apenas com relação ao Zabbix
MFA.

???+ Aviso

    For Duo MFA to work your Zabbix WebUI must be configured to work with HTTPS
    (valid certificate is not required, self-signed certificate will work).

Em primeiro lugar, você precisa criar uma conta no Duo (é gratuito para
gerenciar até 10 usuários) e, em seguida, fazer login no Duo, pois você é um
administrador aqui. No menu à esquerda, selecione `Applications (Aplicativos)` e
clique no botão `Protect an Application (Proteger um aplicativo)`.

![Aplicativos MFA DUO](ch02.34-mfa_duo_applications.png){ width=99% }

_2.34 Menu Aplicativos DUO_

Em seguida, você verá o WebSDK na lista de aplicativos, clique nele

![MFA DUO applications list](ch02.35-mfa_duo_applications_list.png){ width=99% }

_2.35 DUO Applications list_

Here you'll see all the data needed for Zabbix.

![MFA DUO ](ch02.36-mfa_duo_data.png){ width=99% }

_2.36 DUO WebSDK application settings_

Now let's go to Zabbix. First we need to configure Duo MFA method. In the menu
select `Users` and click `Authentication`. Then on `MFA settings` tab click
`Add` in `Methods` section.

![MFA DUO ](ch02.37-mfa_duo_add_method.png){ width=99% }

_2.37 Add MFA method_

Fill in all the fields with data from Duo Dashboard -> Applications -> Web SDK
page (see screenshot above) and click `Add`, then click `Update` to update
Authentication settings.

![MFA DUO ](ch02.38-mfa_duo_method_data.png){ width=99% }

_2.38 DUO method settings_

After the MFA method is configured let's switch the "Test" group to use Duo MFA.
In the menu select `Users` and click `User groups`, then click "test" group. In
the field `Multi-factor authentication` select "DUO1" and click `Update`.

![MFA DUO ](ch02.39-mfa_duo_user_group.png){ width=99% }

_2.39 DUO MFA authentication method for user group_

Everything is ready. Let's test it. Sign out of Zabbix and sign back in with
"test" user. You should see a welcome screen from Duo. Click several `Next`
buttons.

![MFA DUO ](ch02.40-mfa_duo_welcome.png){ width=32% }

_2.40 Enrolling into DUO, step1_

![MFA DUO ](ch02.41-mfa_duo_welcome1.png){ width=32% }

_2.41 Enrolling into DUO, step2_

![MFA DUO ](ch02.42-mfa_duo_welcome2.png){ width=32% }

_2.42 Enrolling into DUO, step3_

Then you need to select the method of authentication.

![MFA DUO ](ch02.43-mfa_duo_auth_method.png){ width=50% }

_2.43 Enrolling into DUO, step4_

It is up to you what to select you can experiment with all these methods. Let's
select "Duo Mobile" (you need to install "Duo mobile" application on your
device). Click `I have a tablet` (it's just easier to activate your device this
way) and confirm that you installed "Duo mobile" on your phone. At this point
you should see a QR code that you need to scan in "Duo mobile" application.

![MFA DUO ](ch02.44-mfa_duo_duo_app.png){ width=32% }

_2.44 Enrolling into DUO, step5_

![MFA DUO ](ch02.45-mfa_duo_confirm_app_installed.png){ width=32% }

_2.45 Enrolling into DUO, step6_

![MFA DUO ](ch02.46-mfa_duo_scan_qr.png){ width=32% }

_2.46 Enrolling into DUO, step7_

Open "Duo mobile" on your phone. If you did not have this application previously
installed (thus no accounts enrolled) you will see couple of welcome screens.

![MFA DUO ](ch02.47-mfa_duo_phone_welcome.png){ width=48% }

_2.47 Configure DUO app, step 1_

![MFA DUO ](ch02.48-mfa_duo_phone_add_account.png){ width=48% }

_2.48 Configure DUO app, step 2_

Tap on "Use a QR code" and then scan the code presented by Duo in your Zabbix
login screen. After you do that you will see that the account is enrolled to
your Duo MFA. Enter account name and tap "Done" and you will see the account in
the list of all accounts enrolled into Duo MFA on this device. In Zabbix WebUI
you will also see a confirmation, click "Continue".

![MFA DUO ](ch02.49-mfa_duo_phone_account_added.png){ width=32% }

_2.49 Configure DUO app, step 3_

![MFA DUO ](ch02.50-mfa_duo_phone_accounts.png){ width=32% }

_2.50 Configure DUO app, step 4_

![MFA DUO ](ch02.51-mfa_duo_enrollement_confirmation.png){ width=32% }

_2.51 Enrolment confirmation_

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
"Approve". Also you will see the user "test" in Duo where you can delete the
user, or deactivate just click on it and experiment.

![MFA DUO ](ch02.56-mfa_duo_users.png){ width=98% }

_2.56 New user registered in DUO_

## Conclusão

Implementing Multi-Factor Authentication (MFA) in Zabbix is a powerful way to
significantly advance your system’s security beyond the standard password
policies. This chapter outlined how Zabbix supports two robust MFA mechanisms:

- Time Based One-Time Password (TOTP): Offers user-friendly, secure login via an
  authenticator app (like Google or Microsoft Authenticator). It's easy to
  configure and effective just ensure that your Zabbix server maintains accurate
  time settings to avoid authentication issues.

- Duo MFA: Integrates a more advanced, enterprise grade solution that provides
  features like push notifications and customizable authentication methods. Duo
  offers flexible and strong security, albeit requiring a bit more setup
  (including HTTPS on the Zabbix WebUI).

Both MFA options elevate the login process by introducing an additional layer of
validation. Administrators can apply MFA selectively by assigning it to specific
user groups thus tailoring the security posture to organizational needs.

Ultimately, enabling MFA not only enhances protection against unauthorized
access but also fits within a broader strategy of robust authentication. Whether
through TOTP or Duo, adding MFA demonstrates a commitment to safeguarding access
to your Zabbix environment and fortifying your monitoring infrastructure.n

## Perguntas

- Why is relying on a password alone not sufficient to secure access to a Zabbix
  instance? (Think about common attack methods like password reuse, brute force,
  or phishing.)

- What are the key differences between TOTP-based MFA and Duo MFA in terms of
  setup, security, and user experience?

- How does accurate system time affect the reliability of TOTP authentication,
  and what could go wrong if time synchronization is not maintained?

- If you were tasked with enabling MFA for a production Zabbix system, which
  method (TOTP or Duo) would you choose, and why? (Consider factors such as
  environment size, user skill level, regulatory requirements, and available
  resources.)

- What are some potential challenges when rolling out MFA in an organization,
  and how could an administrator mitigate user resistance or technical issues?

- Why might it be useful to enable MFA only for certain user groups in Zabbix
  rather than enforcing it globally?

- How does adding MFA to Zabbix align with a broader security strategy, and what
  other complementary security measures should be considered?

## URLs úteis

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa)
[https://duo.com/docs/sso-zabbix](https://duo.com/docs/sso-zabbix)


