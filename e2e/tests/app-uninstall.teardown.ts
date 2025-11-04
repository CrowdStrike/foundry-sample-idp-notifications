import { test as teardown } from '../src/fixtures';

teardown('uninstall IdP Notifications app', async ({ appCatalogPage, appName }) => {
  await appCatalogPage.navigateToPath('/foundry/app-catalog', 'App Catalog');
  await appCatalogPage.uninstallApp(appName);
});
