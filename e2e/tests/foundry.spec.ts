import { test, expect } from '../src/fixtures';

test.describe.configure({ mode: 'serial' });

test.describe('IdP Notifications - E2E Tests', () => {
  test('should verify exposed actions are available in workflow builder', async ({ workflowsPage }) => {
    // This app provides identity system notifications
    // We verify both exposed actions are available in the workflow builder
    // Increase timeout as we're testing 2 actions with search waits
    test.setTimeout(120000); // 2 minutes
    await workflowsPage.navigateToWorkflows();
    await workflowsPage.createNewWorkflow();

    // Select "On demand" trigger
    const onDemandTrigger = workflowsPage.page.getByText('On demand').first();
    await onDemandTrigger.click();

    const nextButton = workflowsPage.page.getByRole('button', { name: 'Next' });
    await nextButton.click();

    await workflowsPage.page.waitForLoadState('networkidle');
    await workflowsPage.page.getByText('Add next').waitFor({ state: 'visible', timeout: 10000 });

    // Click "Add action" button once to open the action selection dialog
    const addNextMenu = workflowsPage.page.getByTestId('add-next-menu-container');
    const addActionButton = addNextMenu.getByTestId('context-menu-seq-action-button');
    await addActionButton.click();
    await workflowsPage.page.waitForLoadState('networkidle');

    // Wait for search box to be visible
    const searchBox = workflowsPage.page.getByRole('searchbox').or(workflowsPage.page.getByPlaceholder(/search/i));
    await searchBox.waitFor({ state: 'visible', timeout: 10000 });

    // Wait for initial action list loading to complete
    const loadingMessages = workflowsPage.page.getByText('This may take a few moments');
    await loadingMessages.first().waitFor({ state: 'hidden', timeout: 60000 }).catch(() => {});
    await workflowsPage.page.waitForLoadState('networkidle');

    // Verify all exposed actions by checking their Configure sections
    const expectedActions = [
      'Get latest identity system notifications',
      'Get domain controller sensors details',
    ];

    for (const actionName of expectedActions) {
      // Search for the specific action
      await expect(searchBox).toBeEnabled({ timeout: 10000 });
      await searchBox.fill(actionName);

      // Wait for search results to load
      await loadingMessages.first().waitFor({ state: 'hidden', timeout: 60000 }).catch(() => {});
      await workflowsPage.page.waitForLoadState('networkidle');

      // Expand "Other (Custom, Foundry, etc.)" section if it exists
      const otherSection = workflowsPage.page.getByText('Other (Custom, Foundry, etc.)');
      if (await otherSection.isVisible({ timeout: 2000 }).catch(() => false)) {
        await otherSection.click();

        // Wait for section's internal loading to complete
        await loadingMessages.first().waitFor({ state: 'hidden', timeout: 60000 }).catch(() => {});
        await workflowsPage.page.waitForLoadState('networkidle');
      }

      // Find all instances of this action (may include stale ones from previous installs)
      // Use exact: false to be more flexible with matching
      const actionElements = await workflowsPage.page.getByText(actionName, { exact: false }).all();

      if (actionElements.length === 0) {
        throw new Error(`Action '${actionName}' not found in search results`);
      }

      console.log(`Found ${actionElements.length} instance(s) of '${actionName}' - trying each until one works...`);

      let actionAdded = false;

      // Try each instance until we find one that's not stale
      for (let i = 0; i < actionElements.length; i++) {
        console.log(`  Trying instance ${i + 1}/${actionElements.length}...`);

        try {
          // Click on the action
          await actionElements[i].click();
          await workflowsPage.page.waitForLoadState('networkidle');

          // Wait for the details panel to load and check if configuration is present
          // Stale actions won't show the "Configure" heading
          // Look for the Configure heading as indicator of valid action
          try {
            const configureHeading = workflowsPage.page.getByRole('heading', { name: 'Configure', level: 4 });
            await configureHeading.waitFor({ state: 'visible', timeout: 10000 });
            console.log(`✓ Action verified: ${actionName} - Configure section is present`);
            actionAdded = true;

            // Close the dialog to prepare for next action
            const backButton = workflowsPage.page.getByRole('button', { name: 'Back' }).or(
              workflowsPage.page.getByLabel('Back')
            );
            if (await backButton.isVisible({ timeout: 1000 }).catch(() => false)) {
              await backButton.click();
              await workflowsPage.page.waitForLoadState('networkidle');

              // Wait for action list to reload after going back
              await loadingMessages.first().waitFor({ state: 'hidden', timeout: 60000 }).catch(() => {});
              await workflowsPage.page.waitForLoadState('networkidle');
            }

            break;
          } catch (error) {
            const errorMsg = error.message || 'Unknown error';
            console.log(`  Instance ${i + 1} failed: ${errorMsg}`);
          }
        } catch (error) {
          console.log(`  Instance ${i + 1} failed: ${error.message}, trying next...`);
        }
      }

      if (!actionAdded) {
        throw new Error(`Failed to add action '${actionName}' - all ${actionElements.length} instance(s) appear to be stale or invalid`);
      }
    }

    console.log('All exposed actions verified successfully');
  });
});
