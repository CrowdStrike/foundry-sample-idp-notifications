import { test, expect } from '../src/fixtures';

test.describe.configure({ mode: 'serial' });

test.describe('IdP Notifications - E2E Tests', () => {
  test('should verify exposed actions are available in workflow builder', async ({ workflowsPage }) => {
    await workflowsPage.navigateToWorkflows();
    await workflowsPage.createNewWorkflow();

    const onDemandTrigger = workflowsPage.page.getByText('On demand').first();
    await onDemandTrigger.click();

    const nextButton = workflowsPage.page.getByRole('button', { name: 'Next' });
    await nextButton.click();

    await workflowsPage.page.waitForLoadState('networkidle');
    await workflowsPage.page.getByText('Add next').waitFor({ state: 'visible', timeout: 10000 });

    const addNextMenu = workflowsPage.page.getByTestId('add-next-menu-container');
    const addActionButton = addNextMenu.getByTestId('context-menu-seq-action-button');
    await addActionButton.click();

    await workflowsPage.page.waitForLoadState('networkidle');

    const expectedActions = [
      'Get latest identity system notifications',
      'Get domain controller sensors details',
    ];

    for (const actionName of expectedActions) {
      const searchBox = workflowsPage.page.getByRole('searchbox').or(workflowsPage.page.getByPlaceholder(/search/i));
      await searchBox.clear();
      await searchBox.fill(actionName);

      await workflowsPage.page.getByText('This may take a few moments').waitFor({ state: 'hidden', timeout: 30000 });
      await workflowsPage.page.waitForLoadState('networkidle');

      const otherSection = workflowsPage.page.getByText('Other (Custom, Foundry, etc.)');
      if (await otherSection.isVisible({ timeout: 2000 })) {
        await otherSection.click();
        await workflowsPage.page.getByText('This may take a few moments').last().waitFor({ state: 'hidden', timeout: 30000 });
        await workflowsPage.page.waitForLoadState('networkidle');
      }

      const actionElement = workflowsPage.page.getByText(actionName, { exact: false });
      await expect(actionElement).toBeVisible({ timeout: 10000 });
      console.log(`✓ Action available: ${actionName}`);
    }

    console.log('All exposed actions verified successfully');
  });
});
