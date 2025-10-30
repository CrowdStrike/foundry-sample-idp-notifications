import { test as baseTest } from '@playwright/test';
import { FoundryHomePage } from './pages/FoundryHomePage';
import { AppManagerPage } from './pages/AppManagerPage';
import { AppCatalogPage } from './pages/AppCatalogPage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { config } from './config/TestConfig';
import { logger } from './utils/Logger';

type FoundryFixtures = {
  foundryHomePage: FoundryHomePage;
  appManagerPage: AppManagerPage;
  appCatalogPage: AppCatalogPage;
  workflowsPage: WorkflowsPage;
  appName: string;
};

export const test = baseTest.extend<FoundryFixtures>({
  page: async ({ page }, use) => {
    const timeouts = config.getPlaywrightTimeouts();
    page.setDefaultTimeout(timeouts.timeout);

    if (!process.env.CONFIG_LOGGED) {
      config.logSummary();
      process.env.CONFIG_LOGGED = 'true';
    }

    await use(page);
  },

  foundryHomePage: async ({ page }, use) => {
    await use(new FoundryHomePage(page));
  },

  appManagerPage: async ({ page }, use) => {
    await use(new AppManagerPage(page));
  },

  appCatalogPage: async ({ page }, use) => {
    await use(new AppCatalogPage(page));
  },

  workflowsPage: async ({ page }, use) => {
    await use(new WorkflowsPage(page));
  },

  appName: async ({}, use) => {
    await use(config.appName);
  },
});

export { expect } from '@playwright/test';
