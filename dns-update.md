# Change DNS Address in GoDaddy

Follow these steps to change the DNS address for a gearupapp.org domain registered with GoDaddy:

## Step 1: Log in to Your GoDaddy Account

1. Open your web browser and go to the GoDaddy website [GoDaddy](https://www.godaddy.com/).

2. Click "Sign In" at the top right corner of the page.

3. Enter your GoDaddy username (email or customer number) and password, then click "Sign In."

## Step 2: Access Your Domain Settings

4. Once you are logged in, you'll be taken to the GoDaddy dashboard. Locate and click on "Domains" in the main menu.

5. You'll see a list of your domains. Find the domain named gearupapp.org and click on it to select it.

## Step 3: Access DNS Management

6. After selecting your domain, you'll be taken to the Domain Settings page. Look for an option called "Manage DNS" and click on it.

## Step 4: Change DNS records

7. In the DNS records section, you should see multiple records in that the below mentioned ones are the names that are linked with application servers:

   - **360**: is for the site https://360.gearupapp.org/ (webapp version of the gearupapp)
   - **api**: is for the site https://api.gearupapp.org/ (API backend for the mobile and web application)
   - **@** or **www**: is for https://www.gearupapp.org/ (default site for gearupapp)

8. If you want to change DNS records settings, click on the edit icon and save the settings .
