# n8n Workflow Templates for Malaysian Lead Generator

This directory contains predefined workflow templates for use with n8n to automate lead generation, email outreach, and analytics processes.

## Available Workflows

### 1. `lead_scraping.json` - Lead Scraping Workflow

This workflow automates the process of scraping business contact information from various Malaysian sources.

**Features:**
- Scheduled scraping from multiple sources
- Configurable parameters for each source
- Status monitoring for scraping jobs
- Database import of collected leads
- Notifications on job completion

### 2. `email_generation.json` - Email Generation Workflow

This workflow handles the creation of personalized outreach emails based on lead information.

**Features:**
- Intelligent template selection based on lead source
- Personalization with dynamic variables
- Spreadsheet tracking of generated emails
- Notifications for newly generated emails

### 3. `email_sending.json` - Email Sending Workflow

This workflow manages the sending of generated emails with rate limiting and tracking.

**Features:**
- Rate-limited email sending to avoid throttling
- Success/failure tracking in spreadsheets
- Error handling and notification
- Campaign statistics collection
- Email reporting capabilities

### 4. `analytics.json` - Analytics & Reporting Workflow

This workflow generates comprehensive reports on lead generation and email campaign performance.

**Features:**
- Daily performance metrics collection
- Source and template effectiveness analysis
- PDF report generation
- Distribution via email
- Notifications through Telegram and n8n dashboard

### 5. `email_sending_with_proposals.json` - Email Sending with Proposal Attachments

This workflow specializes in sending emails with PDF proposal attachments tailored to specific leads using an intelligent package-based selection system.

**Features:**
- Intelligent package-based proposal selection based on lead characteristics
- Organization type detection (corporate, government, university, school)
- Automatic matching of proposals to leads based on semantic relevance
- Support for package variants tailored to different organization types
- Detailed tracking of emails with attachments
- Campaign performance analysis specifically for proposal emails
- Specialized reporting on proposal email effectiveness

## Installation & Usage

1. **Install n8n:**
   ```
   npm install n8n -g
   ```

2. **Start n8n:**
   ```
   n8n start
   ```

3. **Access n8n:** Open your browser and navigate to http://localhost:5678/

4. **Import Workflows:**
   - In n8n, go to Workflows → Import From File
   - Select the workflow JSON file you want to import
   - Save the imported workflow

5. **Configure Credentials:**
   - Each workflow requires credentials for the Malaysian Lead Generator API
   - Create a new credential of type "HTTP Basic Auth" with your API username and password
   - For email sending and notifications, configure SMTP and Telegram credentials as needed

6. **Activate Workflows:**
   - Enable the workflow triggers to activate the workflows
   - Adjust scheduling as needed for your use case

## Customizing Workflows

You can customize these workflows to suit your specific needs:

- **Adjust scheduling** by modifying the trigger node parameters
- **Change notification channels** by replacing or configuring the notification nodes
- **Add new data sources** by duplicating and modifying the HTTP Request nodes
- **Modify reporting format** by editing the Markdown and PDF creation nodes

## Package-Based Proposal Selection

The `email_sending_with_proposals.json` workflow implements an intelligent system to match the most appropriate proposal PDF to each lead based on their characteristics:

### Supported Packages

1. **Residential Seminar Package**
   - For leads interested in retreats, workshops, or events with accommodation
   - Variants: Corporate (`residential_seminar_corporate.pdf`), Government (`residential_seminar_government.pdf`)
   - Default: `residential_seminar_package.pdf`

2. **Meeting Package**
   - For leads interested in day meetings, conferences, or presentations without accommodation
   - Variants: Corporate (`meeting_package_corporate.pdf`), Government (`meeting_package_government.pdf`)
   - Default: `meeting_package.pdf`

3. **Camping Package**
   - For leads interested in outdoor activities, adventure, or team building in nature
   - Variants: Corporate, University, Government, School (e.g., `camping_package_university.pdf`)
   - Default: `camping_package.pdf`

### How It Works

1. **File Organization**: Place your proposal PDFs in the `/proposals` directory with the naming convention shown above
2. **Lead Analysis**: The workflow analyzes lead information (organization name, role, source URL) 
3. **Organization Type Detection**: Determines if the lead is from a corporate, government, university, or school entity
4. **Package Selection**: Selects the most appropriate package type based on keyword matching
5. **Variant Selection**: Chooses the specific variant for the lead's organization type
6. **Fallback Mechanism**: Uses default packages if no specific match is found

### Customizing the Selection Logic

To modify the selection criteria:

1. Edit the `Match Proposals to Leads` function node in the workflow
2. Update the `PACKAGE_TYPES` object to change keywords for each package
3. Modify the `ORGANIZATION_TYPES` object to adjust organization detection
4. Customize the matching logic in the `determinePackageType` and `determineOrganizationType` functions

## Troubleshooting

If you encounter issues with the workflows:

1. **Check API connectivity:** Ensure the Malaysian Lead Generator API is running at http://localhost:8000
2. **Verify credentials:** Make sure your API credentials are correct
3. **Check execution logs:** Review the execution logs in n8n for errors
4. **Test individual nodes:** Execute nodes individually to identify issues 

## Setting Up Proposal Attachments

For the email sending with proposals workflow:

1. **Create a proposals directory:** Create a directory at `/proposals` or configure the workflow to use your existing directory
2. **Add proposal PDFs:** Place your company proposal PDFs following the naming convention (see "Package-Based Proposal Selection" section)
3. **Test the workflow:** Run a test execution to verify proposals are being correctly matched and attached
4. **Monitor selection process:** Check execution data to see which package and variant was selected for each lead
5. **Analyze effectiveness:** Use the campaign stats to evaluate which proposals and variants are most effective 