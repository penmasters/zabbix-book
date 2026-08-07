---
descripton: |
    This section from The Zabbix Book, titled "Duo MFA Provider," explains how
    to integrate Duo Security with Zabbix for multi-factor authentication. It
    covers setup, configuration, and login testing, adding an extra security
    layer to protect access to the Zabbix frontend.
tags: [advanced]
---

# Multi factor authentication

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

## Time-based one-time password

In the menu select `Users` section and then `Authentication`

![MFA Settings initial](ch02.57-mfa_settings_initial.png){ width=90% }

_2.57 Initial MFA settings_

Now in `MFA settings` tab select the `Enable multi-factor authentication` check-box,
then select `TOTP` in Type drop-down list.

![MFA Settings TOTP](ch02.58-mfa_settings_TOTP_new.png){ width=90% }

_2.58 New MFA method_

In `Hash function` drop-down list you can choose SHA-1, SHA-256 or SHA-512, the higher
number is the better security.

In `Code lentgh` you can select how many digits will be generated for you by Authenticator
application on your phone.

Click `Add` and then `Update`. Now you have TOTP MFA configured and it is the default
method of MFA.

![MFA Settings TOTP configured](ch02.59-mfa_settings_TOTP_configured.png){ width=90% }

_2.59 New MFA method added_

Now you need to tell Zabbix for which User group (or groups) to use MFA. Let's create
a User group that would require MFA.

In the menu select `Users` section and then `User groups`, then click `Create user
group` button

![MFA list of user groups](ch02.60-mfa_create_user_groups.png){ width=90% }

_2.60 Create user group_

In `Group name` put "test". Note that `Multi-factor authentication` field is "Default",
as currently we have only one MFA method configured it does not matter whether we
select "Default" or "TOTP1" that we created above. You also can disable MFA for
all users belonging to this User group. Click `Add` button to create "test" User
group.

![MFA new user group](ch02.61-mfa_new_user_group.png){ width=90% }

_2.61 New user group configuration_

???+ Note

    MFA method is defined on per User group basis, i.e. MFA method configured for
    a User group will be applied to all users belonging to this group.

Let's add a user to this user group. In the menu select `Users` section and then
`Users`, then click `Create user` button

![MFA create user](ch02.62-mfa_create_user.png){ width=90% }

_2.62 Create user_

Fill in `Username`, `Password` and `Password (once again)` fields. Make sure you
select `test` user group in `Groups` field.

![MFA new user](ch02.63-mfa_new_user.png){ width=90% }

_2.63 New user configuration_

Then switch to `Permissions` tab and select any role.

![MFA new user permissions](ch02.64-mfa_new_user_permissions.png){ width=90% }

_2.64 New user permissions_

Click `Add` button to add the user.

Now we can test how TOTP MFA works. Sign out and then try to sign in as a test user
you just created. You will be presented with a QR code. That means that the user
`test` has not been enrolled in TOTP MFA yet.

![MFA TOTP QR code](ch02.65-mfa_totp_qr_code.png){ width=30% }

_2.65 TOTP QR code_

On your phone you need to install either "Microsoft authenticator" or "Google authenticator"
application. The procedure of adding new QR code is quite similar, here is how it
looks in "Google authenticator". Tap `Add a code` and then `Scan a QR code`. You'll
be immediately presented with a 6 digit code (remember we selected 6 in `Code length`
when we configured TOTP MFA?)

![MFA TOTP auth app1](ch02.66-mfa_totp_auth_app1.png){ width=32% }

_2.66 Authenticator app, step 1_

![MFA TOTP auth app2](ch02.67-mfa_totp_auth_app2.png){ width=32% }

_2.67 Authenticator app, step 2_

![MFA TOTP auth app3](ch02.68-mfa_totp_auth_app3.png){ width=32% }

_2.68 Authenticator app, step 3_

Enter this code into `Verification code` field of your login screen and click
`Sign in`, if you did everything right you are logged in into Zabbix at this point.
At this point the user "test" is considered enrolled into TOTP MFA and Zabbix stores
a special code used for further authentications in its database. The next time
user "test" tries to login into Zabbix there will be only a field to enter
verification code

![MFA TOTP second login](ch02.69-mfa_totp_second_login.png){ width=32% }

_2.69 Verification code request_

???+ warning

    For TOTP MFA to work your Zabbix server must have correct time. Sometimes
    it's not the case especially if you are working with containers so pay attention
    to this.

If a user changes (or loses) his/her phone, then Zabbix administrator should reset
his/her enrolment. To do that in the menu select `Users` then mark a check-box to
the left of "test" user and click "Reset TOTP secret" button.

![MFA TOTP reset password](ch02.70-mfa_totp_reset_password.png){ width=99% }

_2.70 Reset TOTP secret_

After you reset TOTP secret the "test" user will have to undergo enrolment procedure
again.

---

## Duo MFA provider

Duo is a very famous security platform that provides a lot of security related features/products.
To read more please visit [Duo](https://duo.com/). Here we'll talk about Duo only
in regards to Zabbix MFA.

???+ warning

    For Duo MFA to work your Zabbix WebUI must be configured to work with HTTPS
    (valid certificate is not required, self-signed certificate will work).

First of all you need to create an account with Duo (it's free to manage up to
10 users) then login into Duo, you are an admin here. In the menu on the left select
`Applications` and click `Protect an Application` button.

![MFA DUO applications](ch02.71-mfa_duo_applications.png){ width=99% }

_2.71 DUO Applications menu_

Then you will see WebSDK in applications list, click on it

![MFA DUO applications list](ch02.72-mfa_duo_applications_list.png){ width=99% }

_2.72 DUO Applications list_

Here you'll see all the data needed for Zabbix.

![MFA DUO ](ch02.73-mfa_duo_data.png){ width=99% }

_2.73 DUO WebSDK application settings_

Now let's go to Zabbix. First we need to configure Duo MFA method. In the menu select
`Users` and click `Authentication`. Then on `MFA settings` tab click `Add` in
`Methods` section.

![MFA DUO ](ch02.74-mfa_duo_add_method.png){ width=99% }

_2.74 Add MFA method_

Fill in all the fields with data from Duo Dashboard -> Applications -> Web SDK page
(see screenshot above) and click `Add`, then click `Update` to update Authentication
settings.

![MFA DUO ](ch02.75-mfa_duo_method_data.png){ width=99% }

_2.75 DUO method settings_

After the MFA method is configured let's switch the "Test" group to use Duo MFA.
In the menu select `Users` and click `User groups`, then click "test" group. In
the field `Multi-factor authentication` select "DUO1" and click `Update`.

![MFA DUO ](ch02.76-mfa_duo_user_group.png){ width=99% }

_2.76 DUO MFA authentication method for user group_

Everything is ready. Let's test it. Sign out of Zabbix and sign back in with "test"
user. You should see a welcome screen from Duo. Click several `Next` buttons.

![MFA DUO ](ch02.77-mfa_duo_welcome.png){ width=32% }

_2.77 Enrolling into DUO, step1_

![MFA DUO ](ch02.78-mfa_duo_welcome1.png){ width=32% }

_2.78 Enrolling into DUO, step2_

![MFA DUO ](ch02.79-mfa_duo_welcome2.png){ width=32% }

_2.79 Enrolling into DUO, step3_

Then you need to select the method of authentication.

![MFA DUO ](ch02.80-mfa_duo_auth_method.png){ width=50% }

_2.80 Enrolling into DUO, step4_

It is up to you what to select you can experiment with all these methods. Let's
select "Duo Mobile" (you need to install "Duo mobile" application on your device).
Click `I have a tablet` (it's just easier to activate your device this way) and
confirm that you installed "Duo mobile" on your phone. At this point you should
see a QR code that you need to scan in "Duo mobile" application.

![MFA DUO ](ch02.81-mfa_duo_duo_app.png){ width=32% }

_2.81 Enrolling into DUO, step5_

![MFA DUO ](ch02.82-mfa_duo_confirm_app_installed.png){ width=32% }

_2.82 Enrolling into DUO, step6_

![MFA DUO ](ch02.83-mfa_duo_scan_qr.png){ width=32% }

_2.83 Enrolling into DUO, step7_

Open "Duo mobile" on your phone. If you did not have this application previously
installed (thus no accounts enrolled) you will see couple of welcome screens.

![MFA DUO ](ch02.84-mfa_duo_phone_welcome.png){ width=48% }

_2.84 Configure DUO app, step 1_

![MFA DUO ](ch02.85-mfa_duo_phone_add_account.png){ width=48% }

_2.85 Configure DUO app, step 2_

Tap on "Use a QR code" and then scan the code presented by Duo in your Zabbix login
screen. After you do that you will see that the account is enrolled to your Duo
MFA. Enter account name and tap "Done" and you will see the account in the list
of all accounts enrolled into Duo MFA on this device. In Zabbix WebUI you will
also see a confirmation, click "Continue".

![MFA DUO ](ch02.86-mfa_duo_phone_account_added.png){ width=32% }

_2.86 Configure DUO app, step 3_

![MFA DUO ](ch02.87-mfa_duo_phone_accounts.png){ width=32% }

_2.87 Configure DUO app, step 4_

![MFA DUO ](ch02.88-mfa_duo_enrollement_confirmation.png){ width=32% }

_2.88 Enrolment confirmation_

Duo will ask you now whether you want to add another method of authentication,
click `Skip for now` and you'll see a confirmation that set up completed. Click
`Login with Duo` and a notification will be pushed to your device.

![MFA DUO ](ch02.89-mfa_duo_another_method.png){ width=32% }

_2.89 Add another way to login_

![MFA DUO ](ch02.90-mfa_duo_setup_completed.png){ width=32% }

_2.90 MFA DUO set up completed_

![MFA DUO ](ch02.91-mfa_duo_push_sent.png){ width=32% }

_2.91 DUO push notification sent_

Now just tap on "Approve" on your device and you will be logged in into Zabbix.

![MFA DUO ](ch02.92-mfa_duo_phone_push_notification.png){ width=50% }

_2.92 DUO push notification on the phone_

Duo MFA enrolment complete. If you sign out and sign in back then immediately a
push notification will be sent to your device and all you need is tap on
"Approve". Also you will see the user "test" in Duo where you can delete the user,
or deactivate just click on it and experiment.

![MFA DUO ](ch02.93-mfa_duo_users.png){ width=98% }

_2.93 New user registered in DUO_

## Conclusion

Implementing Multi-Factor Authentication (MFA) in Zabbix is a powerful way to
significantly advance your system’s security beyond the standard password policies.
This chapter outlined how Zabbix supports two robust MFA mechanisms:

- Time Based One-Time Password (TOTP): Offers user-friendly, secure login via an
  authenticator app (like Google or Microsoft Authenticator). It's easy to
  configure and effective just ensure that your Zabbix server maintains accurate
  time settings to avoid authentication issues.

- Duo MFA: Integrates a more advanced, enterprise grade solution that provides
  features like push notifications and customizable authentication methods. Duo
  offers flexible and strong security, albeit requiring a bit more setup (including
  HTTPS on the Zabbix WebUI).

Both MFA options elevate the login process by introducing an additional layer of
validation. Administrators can apply MFA selectively by assigning it to specific
user groups thus tailoring the security posture to organizational needs.

Ultimately, enabling MFA not only enhances protection against unauthorized access
but also fits within a broader strategy of robust authentication. Whether through
TOTP or Duo, adding MFA demonstrates a commitment to safeguarding access to your
Zabbix environment and fortifying your monitoring infrastructure.n

## Questions

- Why is relying on a password alone not sufficient to secure access to a Zabbix
  instance? (Think about common attack methods like password reuse, brute force,
  or phishing.)

- What are the key differences between TOTP-based MFA and Duo MFA in terms of setup,
  security, and user experience?

- How does accurate system time affect the reliability of TOTP authentication,
  and what could go wrong if time synchronization is not maintained?

- If you were tasked with enabling MFA for a production Zabbix system, which method
  (TOTP or Duo) would you choose, and why? (Consider factors such as environment
  size, user skill level, regulatory requirements, and available resources.)

- What are some potential challenges when rolling out MFA in an organization,
  and how could an administrator mitigate user resistance or technical issues?

- Why might it be useful to enable MFA only for certain user groups in Zabbix
  rather than enforcing it globally?

- How does adding MFA to Zabbix align with a broader security strategy, and what
  other complementary security measures should be considered?

## Useful URLs

[https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/mfa)
[https://duo.com/docs/sso-zabbix](https://duo.com/docs/sso-zabbix)


