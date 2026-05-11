import { test as baseTest } from '@playwright/test';
import { WorkflowsPage } from '@crowdstrike/foundry-playwright';

type FoundryFixtures = {
  workflowsPage: WorkflowsPage;
};

export const test = baseTest.extend<FoundryFixtures>({
  workflowsPage: async ({ page }, use) => {
    await use(new WorkflowsPage(page));
  },
});

export { expect } from '@playwright/test';
