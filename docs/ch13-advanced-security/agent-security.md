---
description: |
    Use built-in techniques to secure the Zabbix agent with end-to-end encryption. Using  
    both Pre-shared keys (PSK) and Certificates.
tags: [advanced]
---

# Securing the Zabbix agent with encryption
In chapter 4 we have learned how to set up our Zabbix agent in both the active and the passive mode. In an internal network, this might be all you need to do for your monitoring of Linux, Unix and Windows systems. But what if you need to monitor a Zabbix agent host over the internet or what if you'd just like to add an additional layer of security. This is where Zabbix agent encryption comes in. 

There are two basic methods to encrypt your Zabbix agent and they apply to both passive and active agents.
- Pre-shared keys
- Certificates

Both provide a secure method of encrypting the communication between your Zabbix agent and Zabbix server or proxy. So let's dive into both of them.

## Pre-shared keys
Whenever you start working with Zabbix agent encryption, pre-shared keys are the easiest method to provide an additional layer of security on your internal networks or encrypt internet connected agents. They are easy to understand and do not require maintenance, as they are a set and forget kind of encryption method.

The basis is simple, Zabbix agent uses a pre-shared key (PSK) identity and a PSK string. We set these up both on the Zabbix agent and Zabbix server side to encrypt the communication between them. If you are using Zabbix proxies, the Zabbix server will make sure the proxies know about the pre-shared keys (do not forget to encrypt proxy communication).

- *PSK identity*: A non-secret UTF-8 string. 
- *PSK string*: A secret between 128 bit (16 Bytes, 32 character hexadecimal) and 2048 bit (256 Bytes, 512 character hexadecimal) string.

???+ important note

    The combination of the PSK identity and PSK string has to be unique. There can not be two PSKs with the same identity string but different values.
    We have to keep this in mind when setting up the PSK identity and I usually use something that cannot be duplicate like the hostname of the host we're encrypting.

Let's login to the CLI of a host with the Zabbix agent installed. We are going to edit the Zabbix agent 2 configuration file to allow for PSK encryption.

!!! info "Edit Zabbix agent 2 configuration file"

    Linux CLI
    ```bash
    vim /etc/zabbix/zabbix_agent2.conf
    ```

In the configuration file there are 4 parameters we need to edit. By default they aren't set, but we will set them as specified below.

!!! info "Zabbix agent 2 configuration file encryption parameters"

    Linux CLI
    ```bash
    TLSConnect=psk
    TLSAccept=psk

    TLSPSKIdentity=zbx-agent-active-rocky
    TLSPSKFile=/etc/zabbix/agent.psk
    ```

I've used `zbx-agent-active-rocky` as the identity, as that is the hostname on my server and I will use unique PSK keys for each host. If you want to use a default identity/key pair you could use something like `agent-default-key` as the identity and use the same key on each host (less secure). 

- *TLSConnect*: This parameter makes sure that when the Zabbix agent connects in active mode it will either use `unencrypted`, `psk`, or `cert` to connect.
- *TLSAccept*: This parameter makes sure that when the Zabbix agent is connected to in passive mode it will either use `unencrypted`, `psk`, or `cert` to allow the connection.
- *TLSPSKIdentity*: The plain text non-secret identity used for PSK encryption.
- *TLSPSKFile*: The path to the file where the secret PSK is stored.

As you might have noticed, I have set both `TLSConnect` and `TLSAccept`. This is something recommended to always do to safeguard against configuration mistakes. Let's say you only use the Active Zabbix agent connection, but left `TLSConnect` set to `unencrypted`. If your Zabbix agent allows passive agent connections (due to configuration error, history or on purpose) an unencrypted connection will still be allowed. Recommendation, set both alway unless you have a good reason not to.

We're not done with the configuration on the Zabbix agent side however, we still need to create the PSK. There is a simple command to execute and create the PSK.

!!! info "Create agent.psk file with new pre-shared key"

    Linux CLI
    ```bash
    openssl rand -hex 128 | sudo tee /etc/zabbix/agent.psk > /dev/null
    ```

This will not only create the 128 Bytes (1024 bit and 256 Hex characters) PSK, it will also add it to the file we specified in the Zabbix agent configuration file under `TLSPSKFile=/etc/zabbix/agent.psk`. We can check to see what the PSK looks like.

!!! info "Show agent.psk file with new pre-shared key"

    Linux CLI
    ```bash
    cat /etc/zabbix/agent.psk
    ```

We get a string the looks like this:

!!! info "agent.psk file contents"

    Linux CLI
    ```bash
    b1b3b66f2cff98285f3e0ee495bf44660dd6620be2f972207315e45ab030637ae0aa6f18033e86a0ea3a7fca600f793246ced7003351be13342a831ac860f74498153237d3528357a0fea9b0266d34ba18afe086187d6e1e00c6ff4d78433e4dd7e695099c3664903716a0e3a5bf017efc1354ce779715cff274b79ff5aab1d9
    ```

Do not use the above PSK as it is now of course compromised (everyone reading the book has it). But it shows you what it would look like and we can now copy it for later use in the Zabbix frontend, as well as store it in a password vault perhaps.

Before we go on to the Zabbix frontend however, let's make sure the file where we stored the PSK in is secure.

!!! info "agent.psk file security settings"

    Linux CLI
    ```bash
    sudo chown zabbix:zabbix /etc/zabbix/agent.psk
    sudo chmod 400 /etc/zabbix/agent.psk
    ```

This will make sure only the zabbix user on your Linux system has read only access. Now let's move on to the Zabbix frontend and find our `zbx-agent-active-rocky` host under `Data collection` | `Hosts`.

Open you host configuration and go to the `Encryption` tab. By default it will be set to not use encryption.

![Unencrypted agent](ch13.xx-frontend-agent-host-no-encryption.png){ align=center }
*13.xx Unencrypted agent settings*

Let's fill our the details here, just as we did on the Zabbix agent host side.

![Encrypted agent](ch13.xx-frontend-agent-host-encryption.png){ align=center }
*13.xx Encrypted agent settings*

As you can see, even though this is an Active Zabbix agent, I set up encryption requirements for both. Click on the `Update` button to save these changes and go back to the Zabbix agent host CLI to restart the agent.

!!! info "Restart to make encryption settings take effect."

    Linux CLI
    ```bash
    systemctl restart zabbix-agent2
    ```

Your agent icon should remain green and you should now see that the agent is encrypted.

![Encrypted agent staatus](ch13.xx-frontend-agent-host-encryption-status.png){ align=center }
*13.xx Encrypted agent status*

### Active agent autoregistration

## Certificates

## Conclusion
If you want simple to set up security for your Zabbix agent, use pre-shared keys. They are secure, especially when using 2048-bit (512 hexadecimal digits) and if possible unique pre-shared keys for each agent.

If you want some more layers of security, certificates do provide more security in the way they work alone. With certificate expiry, we are forced to set up good certificate management software to make managing the many certificates doable. Furthermore, certificates provide impersonation resistance by allowing us to restrict issuer/subject.

If you are using active agent autoregistration pre-shared keys seems like your only viable option out of the box. We are forced to use a single pre=shared key for this method, and as such it is less secure. This can still be a good option to provide that additional layer of security on internal networks. 

## Questions

## Useful URLs
