import { test as setup } from '../src/fixtures';

setup('install IdP Notifications app', async ({ appCatalogPage, appName }) => {
  const isInstalled = await appCatalogPage.isAppInstalled(appName);

  if (!isInstalled) {
    console.log(`App '${appName}' is not installed. Installing...`);
    const installed = await appCatalogPage.installApp(appName);

    if (!installed) {
      throw new Error(
        `Failed to install app '${appName}'. The app may need to be deployed first.\n` +
        `See the README for deployment instructions.`
      );
    }
  } else {
    console.log(`App '${appName}' is already installed`);
  }
});
