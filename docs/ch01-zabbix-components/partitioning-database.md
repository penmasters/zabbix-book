# Partitioning a Zabbix MariaDB (MySQL) database with Perl
As your Zabbix environment grows, you'll eventually notice that the built-in housekeeper struggles to keep up. This happens because the Zabbix housekeeper works by scanning the database for each history or trend entry that exceeds its configured retention period and deletes them row by row. While this works for smaller setups, as the database grows your housekeeper process will reach a limit as to what it can delete in time.

You can usually see this issue happening when the housekeeper process runs at 100% continuously and the database keeps growing larger. This indicated that the cleanup can't keep pace with incoming data.

PostgreSQL users can use the native TimescaleDB plugin in Zabbix, which handles historical data retention more efficiently. `MariaDB` (or MySQL) doesn't have a similar built-in option.

This is where `MariaDB` partitioning comes in.

???+ note

    It's recommended to do partitioning right after setting up your Zabbix database. This process is a lot easier on a clean database, than it is on a database that is already is use.

## Preparing the database
To begin implementing `MariaDB` partitioning, you'll need access with super privileges to your Zabbix database server. Before starting however, if you are going to partition an existing zabbix database make sure to create a backup of your database. We can do this in various ways and with various tools, but the built-in `mariadb-dump` tool will work perfectly fine.

<https://mariadb.com/kb/en/mariadb-dump/>

<https://mariadb.com/kb/en/mariadb-import/>

`Make sure to export your database backup to a different server (or disk at least).`

Keep in mind, data corruption can happen when performing large scale changes on your DB and as such also with partitioning

To prevent MariaDB running out of space, also make sure to have a generous amount of free space on your system. Running partitioning when you have no free space left can lead to a corrupted database data. Check your free space with:

!!! info "Check disk space availability"

    ```
    df -h
    ```



## Preparing the partitioning
For existing Zabbix databases, partitioning can be a very time-consuming process. It all depends on the size of the database and the resources available to MariaDB-Server.

This is why I always run partitioning in a `tmux` session. If `tmux` hasn't been installed onto your database server yet, do that now.

!!! info "Check disk space availability"

    RedHat-based
    ```
    dnf install tmux
    ```
    Debian-based
    ```
    apt install tmux
    ```

Now we can issue the tmux command to open a new tmux session:

!!! info "Open tmux session"

    ```
    tmux
    ```

This opens up an terminal session that will remain active even if our SSH session times out.

Now, let's open up a notepad and prepare our partitions. We’ll be partitioning the following tables:
| Table name    | Purpose | Data type |
| -------- | ------- |
| history  | Stores numeric floating point values    |
| history_uint | Stores numeric unsigned values     |
| history_str    | Stores text values up to 255 characters    |
| history_text | Stores text values values up to 64kB |
| history_log | Stores text values up to 64kB with additional log related properties like timestamp | 
| history_bin | Stores binary image data | 
| trends | Stores the min/avg/max/count trends of numeric floating point data |
| trends_uint | Stores the min/avg/max/count trends of numeric unsigned data |


We first will have first have to determine how long we want to store the information per table. MariaDB partitioning will take over the history and trend storage periods as usually configured in the Zabbix frontend. We will configure these retention periods later in the perl script. 

Let's say I want to store my history tables for `31 days` and my trend data for `15 months`. This allows me to troubleshoot in depth for a month and also audit my data for little over a year.

Now this is where I open up a notepad and prepare my partitioning commands. Our history tables will be partitioned by day and our trends tables will be partitioned by month.

So, let’s start with our history_uint table:

!!! info "Prepare history partitioning (assuming today is May 10th 2025)"

    ```
    ALTER TABLE history_uint PARTITION BY RANGE ( clock)

    (PARTITION p2025_03_26 VALUES LESS THAN (UNIX_TIMESTAMP("2025-03-27 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_03_27 VALUES LESS THAN (UNIX_TIMESTAMP("2025-03-28 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_03_28 VALUES LESS THAN (UNIX_TIMESTAMP("2025-03-29 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_03_29 VALUES LESS THAN (UNIX_TIMESTAMP("2025-03-30 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_03_30 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_01 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-02 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_02 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-03 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_03 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-04 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_04 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-05 00:00:00")) ENGINE = InnoDB,
    
    PARTITION p2025_04_05 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-06 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_06 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-07 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_07 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-08 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_08 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-09 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_09 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-10 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_10 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-11 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04_11 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-12 00:00:00")) ENGINE = InnoDB);
    ```
As you can see, I only created `16` partitions here. I could have created `31`, which would have been better perhaps. `MariaDB` will now add all my older than 2025-03-26 data in that single partition. No problem, but it will take longer for my disk space to free up this bigger partitioning, after which is will only keep 1 day worth of data from that point.

I also created a partition in the future, just to have it. The script will handle creating new partitions later for us.

- Creating less than 31 partitions: End up with 1 big partition until it is deleted
- Creating exactly 31 partitions: End up with the ideal set-up immediately, but more to create.

Now, create this `ALTER TABLE` commands with the partitions for all history tables. We then do the same for the trends tables:

!!! info "Prepare trends partitioning (assuming today is May 10th 2025)"

    ```
    ALTER TABLE trends_uint PARTITION BY RANGE ( clock)

    (PARTITION p2024_12 VALUES LESS THAN (UNIX_TIMESTAMP("2025-01-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_01 VALUES LESS THAN (UNIX_TIMESTAMP("2025-02-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_02 VALUES LESS THAN (UNIX_TIMESTAMP("2025-03-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_03 VALUES LESS THAN (UNIX_TIMESTAMP("2025-04-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_04 VALUES LESS THAN (UNIX_TIMESTAMP("2025-05-01 00:00:00")) ENGINE = InnoDB,

    PARTITION p2025_05 VALUES LESS THAN (UNIX_TIMESTAMP("2025-06-01 00:00:00")) ENGINE = InnoDB);
    ```

As you can see, here we are partitioning by month instead of by day. Once again, I can create all partitions for 15 months, or less. That's up to us to decide. Prepared this command for all trends tables.


Then it is time to login to MariaDB and start the partitioning. Please do not forget to use the `tmux` command as we mentioned earlier.

!!! info "Login to MariaDB"

    ```mariadb -u root -p
    ```

Execute the history and trends partitioning commands you prepared in your notepad one by one and make sure to wait for each to finish. As mentioned with large database, be patient. With a clean Zabbix database, this process should be near instant.

## Setting up the Perl script
With the partitioning done, we still need to maintain the partitioned setup. MariaDB will not create new and delete old partitions for us automatically, we need to use a `perl` script for this. Years ago, an honorable Zabbix community member wrote a `perl` script to maintain the partitioning and the people at Opensource ICT Solutions have been maintaining it. You can find it on their GitHub repository:

<https://github.com/OpensourceICTSolutions/zabbix-mysql-partitioning-perl>

Download the script from their GitHub and save it on your Zabbix database server(s) in the following folder:

!!! info "Script folder (create the folder if it doesn't exist)"

    ```/usr/lib/zabbix/
    ```
Then make the script executable, so we can create a cronjob later to execute it.

!!! info "Make the script executable"

    ```chmod 750 /usr/lib/zabbix/mysql_zbx_part.pl
    ```

Now, let's make sure all the settings in the script are set-up correctly. Edit the script with your favourite editor (yes, nano is also an option).

!!! info "Edit the script"

    ```vim /usr/lib/zabbix/mysql_zbx_part.pl
    ```

There are a few lines here we need to edit to make sure the script works. Let's start with our MariaDB login details.

!!! info "Add login details to the script"

    ```
    my $dsn = 'DBI:mysql:'.$db_schema.':mysql_socket=/var/lib/mysql/mysql.sock';

    my $db_user_name = 'zabbix';

    my $db_password = 'password';
    ```

Make sure to modify the credentials and socket path to reflect your own Zabbix database setup. The MariaDB username and password can, for instance, match those defined in your Zabbix server configuration file. You can also create a different user for this if preferred.

Also, keep in mind that the MariaDB socket file can vary depending on your distribution. If the default path (/var/lib/mysql/mysql.sock) doesn't apply, update it accordingly. For example, on Ubuntu systems, the socket is often located at /var/run/mysqld/mysql.sock.


Next up, we should edit the settings related to how long we want our data to be stored. We define that in the following block.

!!! info "Add login details to the script"

    ```
    my $tables = {  'history' => { 'period' => 'day', 'keep_history' => '31'},

                    'history_log' => { 'period' => 'day', 'keep_history' => '31'},
                    
                    'history_str' => { 'period' => 'day', 'keep_history' => '31'},

                    'history_text' => { 'period' => 'day', 'keep_history' => '31'},

                    'history_uint' => { 'period' => 'day', 'keep_history' => '31'},

                    'history_bin' => { 'period' => 'day', 'keep_history' => '31'},

                    'trends' => { 'period' => 'month', 'keep_history' => '15'},

                    'trends_uint' => { 'period' => 'month', 'keep_history' => '15'},
    ```

Keep in mind that `history` is defined by day here and `trends` are defined by month.

We also need to change the timezone to match the timezone configured on our Zabbix database server. As this was written in the the Netherlands, I will use `Europe/Amsterdam`.

!!! info "Add correct timezone"

    ```my $curr_tz = 'Europe/Amsterdam';
    ```

Then the last important step is to make sure that we comment or uncomment some lines in the script. The script works for both `MariaDB` and `MySQL`, as well as for older versions. It is however not smart enough to detect what to use automatically, but feel free to open up that pull request!

The script is already out of the box configured for `MariaDB`, so we don't need to do anything.

For the `MySQL 8.x` users comment the following `MariaDB` lines.
!!! info "Comment MariaDB"

    ```
    # MySQL 5.6 + MariaDB

        #my $sth = $dbh->prepare(qq{SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = 'partition'});


        #$sth->execute();


        #my $row = $sth->fetchrow_array();


        #$sth->finish();

        #    return 1 if $row eq 'ACTIVE';
    ```

And uncomment the `MySQL 8.x` lines.
!!! info "Uncomment MySQL 8.x"

    ```
    # MySQL 8.x (NOT MariaDB!)

        	my $sth = $dbh->prepare(qq{select version();});

        	$sth->execute();

        	my $row = $sth->fetchrow_array();

        
        	$sth->finish();

               return 1 if $row >= 8;
               
        
        # End of MySQL 8.x
    ```

Keep in mind, ONLY do this if you are using `MySQL 8.x` and later. If you are on `MySQL 5.6` or `MariaDB` do NOT change these lines.

For Zabbix 5.4 and OLDER versions also make sure to uncomment the indicated lines. But do not do this for Zabbix 6.0 and higher though.

!!! info "Uncomment for Zabbix 5.4 and older only"

    ```
    # Uncomment the following line for Zabbix 5.4 and earlier

        #	$dbh->do("DELETE FROM auditlog_details WHERE NOT EXISTS (SELECT NULL FROM auditlog WHERE auditlog.auditid = auditlog_details.auditid)");

        }
    ```

For Zabbix 6.4 and OLDER versions also make sure to comment the following line. Do not do this for Zabbix 7.0 and higher though:

!!! info "Uncomment for Zabbix 6.4 and older only"

    ```'history_bin' => { 'period' => 'day', 'keep_history' => '60'},
    ```

We also need to install some Perl dependencies to make sure we can execute the script.

!!! info "Install dependencies"

    Redhat-Based
    ```
    dnf install perl-DateTime perl-Sys-Syslog
    ```
    Debian-based
    ```
    apt-get install libdatetime-perl liblogger-syslog-perl
    ```

If perl-DateTime isn't available on your RedHat 7.x installation make sure to install the powertools repo.

!!! info "Install correct repository"

    RedHat 7 based
    ```
    yum config-manager --set-enabled powertools
    ```

    RedHat 9 based
    ```
    dnf config-manager --enable crb
    ```

    Genuine RedHat
    ```
    subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms
    ```
    
    Oracle Linux
    ```
    dnf config-manager --set-enabled ol8_codeready_builder
    ```

Then the last step is to add a cronjob to execute the script everyday.

!!! info "Open crontab"

    ```crontab -e
    ```

Add the following line to create the cronjob.

!!! info "Create cronjob"

    ```55 22 * * * /usr/lib/zabbix/mysql_zbx_part.pl >/dev/null 2>&1
    ```

Execute the script manually to test.

!!! info "Manual script execution for testing"

    ```perl /usr/lib/zabbix/mysql_zbx_part.pl
    ```

Then we can check and see if it worked.

!!! info "Check the script log"

    ```journalctl -t mysql_zbx_part
    ```

This will give you back a list of created and deleted partitions if you've done everything right. Make sure to check this command again tomorrow, to make sure the cronjob is working as expected.
