![CrowdStrike Falcon](/images/cs-logo.png?raw=true)

# Falcon IdP Domain and Connector Monitoring sample Foundry app

The Falcon IdP Domain and Connector Monitoring sample Foundry app is a community-driven, open source project which serves as an example of an app which can be built using CrowdStrike's Foundry ecosystem. `foundry-sample-idp-notifications` is an open source project, not a CrowdStrike product. As such, it carries no formal support, expressed or implied.

This app is one of several App Templates included in Foundry that you can use to jumpstart your development. It comes complete with a set of preconfigured capabilities aligned to its business purpose. Deploy this app from the Templates page with a single click in the Foundry UI, or create an app from this template using the CLI.

> [!IMPORTANT]  
> To view documentation and deploy this sample app, you need access to the Falcon console.

## Description

Proactively monitors domain controller coverage, health status, and configuration alongside MFA and IDaaS connector functionality. Delivers notifications when issues are detected to ensure continuous security coverage and authentication service availability.

## Prerequisites

* The Foundry CLI (instructions below).
* Python 3.13+ (needed if modifying the app's functions). See [Python For Beginners](https://www.python.org/about/gettingstarted/) for installation instructions.

### Install the Foundry CLI

You can install the Foundry CLI with Scoop on Windows or Homebrew on Linux/macOS.

**Windows**:

Install [Scoop](https://scoop.sh/). Then, add the Foundry CLI bucket and install the Foundry CLI.

```shell
scoop bucket add foundry https://github.com/crowdstrike/scoop-foundry-cli.git
scoop install foundry
```

Or, you can download the [latest Windows zip file](https://assets.foundry.crowdstrike.com/cli/latest/foundry_Windows_x86_64.zip), expand it, and add the install directory to your PATH environment variable.

**Linux and macOS**:

Install [Homebrew](https://docs.brew.sh/Installation). Then, add the Foundry CLI repository to the list of formulae that Homebrew uses and install the CLI:

```shell
brew tap crowdstrike/foundry-cli
brew install crowdstrike/foundry-cli/foundry
```

Run `foundry version` to verify it's installed correctly.

## Getting Started

Clone this sample to your local system, or [download as a zip file](https://github.com/CrowdStrike/foundry-sample-idp-notifications/archive/refs/heads/main.zip) and import it into Foundry.

```shell
git clone https://github.com/CrowdStrike/foundry-sample-idp-notifications
cd foundry-sample-idp-notifications
```

Log in to Foundry:

```shell
foundry login
```

Select the following permissions:

- [ ] Create and run RTR scripts
- [ ] Create, execute and test workflow templates
- [ ] Create, run and view API integrations
- [ ] Create, edit, delete, and list queries

Deploy the app:

```shell
foundry apps deploy
```

> [!TIP]
> If you get an error that the name already exists, change the name to something unique to your CID in `manifest.yml`.

Once the deployment has finished, you can release the app:

```shell
foundry apps release
```

Next, go to **Foundry** > **App catalog**, find your app, and install it.

## About this sample app

This app helps customers proactively monitor their identity infrastructure by automatically alerting them to problems with connectors or domain controllers, allowing them to quickly identify and troubleshoot issues before they become critical.

This Falcon Foundry application performs scheduled checks against domain controllers and identity connectors using CrowdStrike APIs. It evaluates domain controller coverage by comparing registered DCs against monitored assets, assesses DC health through service status, verifies configuration compliance including sensor settings and traffic inspection status, and monitors MFA/IDaaS connector logs for error conditions. Notifications are delivered via configurable channels including email, webhook integrations, and the Falcon console.

**Purpose**: The app provides monitoring and notification capabilities for identity system health, specifically for:

* Connector health status
* Domain coverage status
* Domain controller functionality

**Two New Actions:**

* Action to pull identity system notifications (connector/domain health)
* Action to get domain controller sensor details

**Workflow Implementation:**

* Customers can create scheduled workflows that run hourly
* The workflows check for issues with connectors, domains, or domain controllers
* When problems are detected, automated email notifications are sent

**Notification Content:**

* Detailed information about what's not working properly
* Specific error messages to help with troubleshooting
* Status indicators (inactive, limited functionality, etc.)

## End-to-End Testing

This app includes E2E tests that verify exposed function actions are available in Fusion SOAR workflows.

### Running E2E Tests Locally

```bash
cd e2e
npm ci
npx playwright install chromium
cp .env.sample .env
# Edit .env with your Falcon credentials
npm test
```

The tests will:
1. Install the app
2. Create a new workflow and verify both exposed actions are available:
   - "Get latest identity system notifications"
   - "Get domain controller sensors details"
3. Uninstall the app

See [e2e/README.md](e2e/README.md) for more details.

## Foundry resources

- Foundry documentation: [US-1](https://falcon.crowdstrike.com/documentation/category/c3d64B8e/falcon-foundry) | [US-2](https://falcon.us-2.crowdstrike.com/documentation/category/c3d64B8e/falcon-foundry) | [EU](https://falcon.eu-1.crowdstrike.com/documentation/category/c3d64B8e/falcon-foundry)
- Foundry learning resources: [US-1](https://falcon.crowdstrike.com/foundry/learn) | [US-2](https://falcon.us-2.crowdstrike.com/foundry/learn) | [EU](https://falcon.eu-1.crowdstrike.com/foundry/learn)

---

<p align="center"><img src="/images/cs-logo-footer.png"><br/><img width="300px" src="/images/adversary-goblin-panda.png"></p>
<h3><p align="center">WE STOP BREACHES</p></h3>
