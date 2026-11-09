# Frame.io 迁移报告 {#frame-io-migration-report}

由 `migration/convert.py` 生成。已通过 `.mintignore` 从站点中排除。

## 保留为绝对 URL 的失效链接（在线站点返回 404）(22) {#dead-links-kept-as-absolute-urls-404-on-the-live-site-22}

- platform/docs/getting-started: https://developer.frame.io/platform/api/current
- platform/docs/guides/authentication/overview: https://developer.frame.io/app/tokens
- platform/docs/guides/authentication/python-sdk: https://developer.frame.io/app/tokens
- platform/docs/guides/authentication/typescript-sdk: https://developer.frame.io/app/tokens
- platform/docs/guides/managing-user-permissions: https://developer.frame.io/platform/v4-experimental/api-reference/account-permissions/developer-api-web-experimental-account-user-roles-controller-update
- platform/v2/authentication: https://developer.frame.io/app/oauth_apps
- platform/v2/authentication: https://developer.frame.io/authentication/developer-tokens
- platform/v2/custom-actions-overview: https://developer.frame.io/actions
- platform/v2/deploy-custom-actions-to-zapier: https://developer.frame.io/actions
- platform/v2/gather-all-comments-from-a-project: https://developer.frame.io/authentication/developer-tokens
- platform/v2/reading-the-file-tree: https://developer.frame.io/docs/troubleshooting/troubleshooting
- platform/v2/refreshing-oauth-2-tokens: https://developer.frame.io/oauth-2-applications/building-an-oauth-2-app
- platform/v2/refreshing-oauth-2-tokens: https://developer.frame.io/oauth-2-applications/building-an-oauth-2-app#the-callback
- platform/v2/webhooks-in-zapier: https://developer.frame.io/webhooks
- platform/v2/webhooks-overview: https://developer.frame.io/app/webhooks
- platform/v2/zapier-comment-worflows: https://developer.frame.io/tokens/new
- platform/v4-experimental/changelog/2025/11/23: https://developer.frame.io/platform/v4-experimental/api-reference/files/copy
- platform/v4-experimental/changelog/2025/11/23: https://developer.frame.io/platform/v4-experimental/api-reference/folders/copy
- platform/v4-experimental/changelog/2025/11/23: https://developer.frame.io/platform/v4-experimental/api-reference/version-stacks/copy
- platform/v4-experimental/docs/getting-started: https://developer.frame.io/platform/v4-experimental/api/current
- platform/v4-experimental/docs/guides/authentication: https://developer.frame.io/app/tokens
- platform/v4-experimental/docs/guides/managing-user-permissions: https://developer.frame.io/platform/v4-experimental/api-reference/account-permissions/developer-api-web-experimental-account-user-roles-controller-update

## 保留的失效片段 (1) {#dead-fragments-kept-1}

- camera-to-cloud/getting-started-with-cloud-device-integrations: /camera-to-cloud/implementing-c2c-authentication-and-authorization#h3-section-enabling-qr-code-pairing

## 简化为标签文本的占位符或损坏链接文本 (4) {#placeholder-or-broken-link-text-reduced-to-its-label-4}

- camera-to-cloud/how-to-log-footage-in-real-time: [channel create](link)
- 字面损坏链接文本： Automatically Upload Dropbox Files to Frame.io](doc:upload-dropbox-files-to-frameio
- platform/v2/implementing-c2c-authentication-and-authorization-hardware: [Before We Start Implementing](link)
- platform/v2/implementing-c2c-authentication-and-authorization-hardware: [this introduction](link)

## 已修复为明确目标的链接 (93) {#links-repaired-to-a-clear-target-93}

- camera-to-cloud/how-to-manage-channels: ./how-to-authorization-management-hardware 改为 /platform/v2/how-to-authorization-management-hardware
- camera-to-cloud/how-to-organize-assets: ./implementing-c2c-authentication-and-authorization-c2c-application 改为 /platform/v2/implementing-c2c-authentication-and-authorization-c2c-application
- camera-to-cloud/how-to-organize-assets: ./implementing-c2c-authentication-and-authorization-hardware 改为 /platform/v2/implementing-c2c-authentication-and-authorization-hardware
- platform/changelog/2026/1/18: /platform/v4/api-reference/account-user-roles/index 改为 /platform/api-reference/users/account-permissions-index
- platform/changelog/2026/1/18: /platform/v4/api-reference/metadata/field-definitions.create 改为 /platform/api-reference/metadata-fields/metadata-field-definitions-create
- platform/changelog/2026/1/18: /platform/v4/api-reference/metadata/field-definitions.delete 改为 /platform/api-reference/metadata-fields/metadata-field-definitions-delete
- platform/changelog/2026/1/18: /platform/v4/api-reference/metadata/field-definitions.index 改为 /platform/api-reference/metadata-fields/metadata-field-definitions-index
- platform/changelog/2026/1/18: /platform/v4/api-reference/metadata/field-definitions.update 改为 /platform/api-reference/metadata-fields/metadata-field-definitions-update
- platform/changelog/2026/1/18: /platform/v4/api-reference/project-user-roles/index 改为 /platform/api-reference/project-permissions/index
- platform/changelog/2026/1/18: /platform/v4/api-reference/project-user-roles/update 改为 /platform/api-reference/project-permissions/project-user-roles-update
- platform/changelog/2026/1/18: /platform/v4/api-reference/workspace-user-roles/delete 改为 /platform/api-reference/workspace-permissions/workspace-user-roles-delete
- platform/changelog/2026/1/18: /platform/v4/api-reference/workspace-user-roles/index 改为 /platform/api-reference/workspace-permissions/index
- platform/changelog/2026/1/18: /platform/v4/api-reference/workspace-user-roles/update 改为 /platform/api-reference/workspace-permissions/workspace-user-roles-update
- platform/changelog/2026/1/25: /platform/v4/api-reference/auditlog/index 改为 /platform/api-reference/accounts/auditlog-index
- platform/changelog/2026/5/10: /platform/v4/api-reference/account-user-roles/index 改为 /platform/api-reference/users/account-permissions-index
- platform/changelog/2026/5/10: /platform/v4/api-reference/metadata/field-definitions.index 改为 /platform/api-reference/metadata-fields/metadata-field-definitions-index
- platform/changelog/2026/5/10: /platform/v4/api-reference/project-user-roles/index 改为 /platform/api-reference/project-permissions/index
- platform/changelog/2026/5/10: /platform/v4/api-reference/workspace-user-roles/index 改为 /platform/api-reference/workspace-permissions/index
- platform/changelog/2026/5/17: /platform/v4/api-reference/folder-user-roles/index 改为 /platform/api-reference/folder-permissions/folder-user-roles-index
- platform/changelog/2026/5/17: /platform/v4/api-reference/folder-user-roles/update 改为 /platform/api-reference/folder-permissions/folder-user-roles-update
- platform/changelog/2026/6/14: /platform/v4/api-reference/account-projects/index 改为 /platform/api-reference/projects/account-projects-index
- platform/changelog/2026/6/14: /platform/v4/api-reference/invited-projects/index 改为 /platform/api-reference/projects/invited-projects-index
- platform/changelog/2026/8/30: /platform/v4/api-reference/account-user-roles/update 改为 /platform/api-reference/account-permissions/account-user-roles-update
- platform/docs/getting-started: /platform/docs/sdk-reference/typescript-sdk-reference 改为 /platform/docs/sdk-reference/type-script-sdk-reference
- platform/docs/resources/migration: /platform/v4/api-reference/files/create_local_upload 改为 /platform/api-reference/files/create-local-upload
- platform/docs/resources/migration: /platform/v4/api-reference/files/create_remote_upload 改为 /platform/api-reference/files/create-remote-upload
- platform/docs/resources/migration: /platform/v4/docs/guides/how-to-upload 改为 /platform/v4-experimental/docs/guides/how-to-upload
- platform/v2/authentication: /getting-started/key-concepts#scopes 改为 /platform/v2/key-concepts
- platform/v2/building-an-oauth2-app: /oauth-2-applications/oauth-2-code-authorization-flow 改为 /platform/v2/oauth-2-code-authorization-flow
- platform/v2/custom-actions-overview: doc:webhooks 改为 /platform/v2/webhooks-overview
- platform/v2/custom-actions-three-ways: /docs/custom-actions/deploy-custom-actions-to-zapier 改为 /platform/v2/deploy-custom-actions-to-zapier
- platform/v2/gather-all-comments-from-a-project: /getting-started/key-concepts#pagination 改为 /platform/v2/key-concepts
- platform/v2/gather-all-comments-from-a-project: /other-tools/using-glitch 改为 /platform/v2/using-glitch
- platform/v2/gather-all-comments-from-a-project: /workflows-assets/reading-the-file-tree 改为 /platform/v2/reading-the-file-tree
- platform/v2/index: /automations-webhooks/webhooks-overview 改为 /platform/v2/webhooks-overview
- platform/v2/index: /custom-actions/custom-actions-overview 改为 /platform/v2/custom-actions-overview
- platform/v2/index: /device-integrations/getting-started-with-cloud-device-integrations 改为 /camera-to-cloud/getting-started-with-cloud-device-integrations
- platform/v2/index: /getting-started/authentication#developer-tokens 改为 /platform/v2/authentication
- platform/v2/index: /oauth-2-applications/building-an-oauth2-app 改为 /platform/v2/building-an-oauth2-app
- platform/v2/index: /workflows-assets/reading-the-file-tree 改为 /platform/v2/reading-the-file-tree
- platform/v2/index: /workflows-assets/uploading-assets 改为 /platform/v2/uploading-assets
- platform/v2/index: /zapier/get-started-with-zapier 改为 /platform/v2/get-started-with-zapier
- platform/v2/manage-version-stacks: ref:assets 改为 /platform/v2/api-reference/assets/library-search-get
- platform/v2/manage-version-stacks: ref:post_assets-assetid-version 改为 /platform/v2/api-reference/assets/add-version-to-asset
- platform/v2/manage-version-stacks: ref:post_assets-parentid-children 改为 /platform/v2/api-reference/assets/create-asset
- platform/v2/oauth-2-code-authorization-flow: /getting-started/authentication#developer-tokens 改为 /platform/v2/authentication
- platform/v2/oauth-2-code-authorization-flow: /oauth-2-applications/building-an-oauth2-app 改为 /platform/v2/building-an-oauth2-app
- platform/v2/reading-the-file-tree: doc:managing-version-stacks 改为 /platform/v2/manage-version-stacks
- platform/v2/uploading-assets: doc:get-a-developer-token 改为 /platform/v2/authentication
- platform/v2/user-management: /getting-started/authentication 改为 /platform/v2/authentication
- platform/v2/user-management: ref:post_projects-projectid-collaborators 改为 /platform/v2/api-reference/projects/add-collaborator-to-project
- platform/v2/user-management: ref:post_teams-teamid-members 改为 /platform/v2/api-reference/teams/add-team-member
- platform/v2/webhooks-in-zapier: doc:authentication 改为 /platform/v2/authentication
- platform/v2/working-with-audit-logs: /getting-started/key-concepts#pagination 改为 /platform/v2/key-concepts
- platform/v2/working-with-audit-logs: /workflows-assets/search-for-assets 改为 /platform/v2/search-for-assets
- platform/v2/working-with-review-links: /workflows-assets/uploading-assets 改为 /platform/v2/uploading-assets
- platform/v4-experimental/changelog/2025/10/26: /platform/v4-experimental/api-reference/DeveloperApiWeb/Experimental.AccountUserRolesController.update 改为 /platform/v4-experimental/api-reference/account-permissions/account-user-roles-update
- platform/v4-experimental/changelog/2025/10/5: /platform/v4-experimental/api-reference/invited-projects/index 改为 /platform/v4-experimental/api-reference/projects/invited-projects-index
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/DeveloperApiWeb/Experimental.AccountUserRolesController.update 改为 /platform/v4-experimental/api-reference/account-permissions/account-user-roles-update
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/actions/create 改为 /platform/v4-experimental/api-reference/custom-actions/actions-create
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/actions/delete 改为 /platform/v4-experimental/api-reference/custom-actions/actions-delete
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/actions/index 改为 /platform/v4-experimental/api-reference/custom-actions/actions-index
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/actions/show 改为 /platform/v4-experimental/api-reference/custom-actions/actions-show
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/actions/update 改为 /platform/v4-experimental/api-reference/custom-actions/actions-update
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/auditlog/index 改为 /platform/v4-experimental/api-reference/accounts/auditlog-index
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/invited-projects/index 改为 /platform/v4-experimental/api-reference/projects/invited-projects-index
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/metadata/field-definitions.create 改为 /platform/v4-experimental/api-reference/metadata-fields/metadata-field-definitions-create
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/metadata/field-definitions.delete 改为 /platform/v4-experimental/api-reference/metadata-fields/metadata-field-definitions-delete
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/metadata/field-definitions.index 改为 /platform/v4-experimental/api-reference/metadata-fields/metadata-field-definitions-index
- platform/v4-experimental/changelog/2026/1/18: /platform/v4-experimental/api-reference/metadata/field-definitions.update 改为 /platform/v4-experimental/api-reference/metadata-fields/metadata-field-definitions-update
- platform/v4-experimental/changelog/2026/1/25: /platform/v4-experimental/api-reference/account-user-roles/index 改为 /platform/v2/index
- platform/v4-experimental/changelog/2026/1/25: /platform/v4-experimental/api-reference/project-user-roles/index 改为 /platform/v4-experimental/api-reference/project-permissions/project-user-roles-index
- platform/v4-experimental/changelog/2026/1/25: /platform/v4-experimental/api-reference/workspace-user-roles/index 改为 /platform/v4-experimental/api-reference/workspace-permissions/workspace-user-roles-index
- platform/v4-experimental/changelog/2026/10/4: /platform/v4-experimental/api-reference/account-user-roles/memberships 改为 /platform/v4-experimental/api-reference/users/account-user-roles-memberships
- platform/v4-experimental/changelog/2026/2/1: /platform/v4-experimental/api-reference/folder-user-roles/index 改为 /platform/v4-experimental/api-reference/folder-permissions/folder-user-roles-index
- platform/v4-experimental/changelog/2026/2/1: /platform/v4-experimental/api-reference/folder-user-roles/update 改为 /platform/v4-experimental/api-reference/folder-permissions/folder-user-roles-update
- platform/v4-experimental/changelog/2026/3/29: /platform/v4-experimental/api-reference/account-projects/index 改为 /platform/v4-experimental/api-reference/projects/account-projects-index
- platform/v4-experimental/changelog/2026/4/12: /platform/v4-experimental/api-reference/project-group-roles/delete 改为 /platform/v4-experimental/api-reference/project-permissions/project-group-roles-delete
- platform/v4-experimental/changelog/2026/4/12: /platform/v4-experimental/api-reference/project-group-roles/update 改为 /platform/v4-experimental/api-reference/project-permissions/project-group-roles-update
- platform/v4-experimental/changelog/2026/5/3: /platform/v4-experimental/api-reference/workspace-group-roles/delete 改为 /platform/v4-experimental/api-reference/workspace-permissions/workspace-group-roles-delete
- platform/v4-experimental/changelog/2026/5/3: /platform/v4-experimental/api-reference/workspace-group-roles/update 改为 /platform/v4-experimental/api-reference/workspace-permissions/workspace-group-roles-update
- platform/v4-experimental/changelog/2026/6/14: /platform/v4-experimental/api-reference/workspace-group-roles/index 改为 /platform/v4-experimental/api-reference/workspace-permissions/workspace-group-roles-index
- platform/v4-experimental/changelog/2026/6/7: /platform/v4-experimental/api-reference/project-group-roles/index 改为 /platform/v4-experimental/api-reference/project-permissions/project-group-roles-index
- platform/v4-experimental/changelog/2026/8/30: /platform/v4-experimental/api-reference/account-user-roles/show 改为 /platform/v4-experimental/api-reference/users/account-user-roles-show
- platform/v4-experimental/changelog/2026/9/13: /platform/v4-experimental/api-reference/metadata/field-definitions.show 改为 /platform/v4-experimental/api-reference/metadata-fields/metadata-field-definitions-show
- platform/v4-experimental/docs/getting-started: /platform/docs/sdk-reference/typescript-sdk-reference 改为 /platform/docs/sdk-reference/type-script-sdk-reference
- platform/v4-experimental/docs/guides/authentication: ./python-sdk 改为 /platform/docs/guides/authentication/python-sdk
- platform/v4-experimental/docs/guides/authentication: ./typescript-sdk 改为 /platform/docs/guides/authentication/typescript-sdk
- platform/v4-experimental/docs/guides/how-to-upload: ./python-sdk-upload-guide 改为 /platform/docs/guides/uploading-to-frame-io/python-sdk-upload-guide
- platform/v4-experimental/docs/resources/migration: /platform/v4/api-reference/files/create_local_upload 改为 /platform/api-reference/files/create-local-upload
- platform/v4-experimental/docs/resources/migration: /platform/v4/api-reference/files/create_remote_upload 改为 /platform/api-reference/files/create-remote-upload
- platform/v4-experimental/docs/resources/migration: /platform/v4/docs/guides/how-to-upload 改为 /platform/v4-experimental/docs/guides/how-to-upload
- platform/v4-experimental/welcome: /docs/sdk-reference 改为 /platform/docs/sdk-reference/python-sdk-reference

## 已修复的片段 (6) {#fragments-repaired-6}

- camera-to-cloud/how-to-advanced-uploads: #handling-the-paused-status 改为 #managing-the-paused-status
- camera-to-cloud/how-to-log-footage-in-real-time: #fetching-connection-information 改为 #retrieving-connection-information
- camera-to-cloud/how-to-log-footage-in-real-time: #h2-section-uploading-reliably 改为 #uploading-reliably
- camera-to-cloud/how-to-log-footage-in-real-time: #h3-section-offset---handling-paused-devices 改为 #offset---handling-paused-devices
- camera-to-cloud/how-to-manage-channels: #fetching-connection-information 改为 #retrieving-connection-information
- platform/v2/implementing-c2c-authentication-and-authorization-c2c-application: #device-identification-device_id 改为 #device-identification

## 现在直接落到其索引页的章节 URL (24) {#section-urls-that-now-land-on-their-index-page-24}

- /platform/api-reference/accounts 直接提供 /platform/api-reference/accounts/index，而不是重定向到 /platform/api-reference/accounts/index
- /platform/api-reference/collections 直接提供 /platform/api-reference/collections/index，而不是重定向到 /platform/api-reference/collections/index
- /platform/api-reference/comments 直接提供 /platform/api-reference/comments/index，而不是重定向到 /platform/api-reference/comments/create
- /platform/api-reference/folders 直接提供 /platform/api-reference/folders/index，而不是重定向到 /platform/api-reference/folders/copy
- /platform/api-reference/groups 直接提供 /platform/api-reference/groups/index，而不是重定向到 /platform/api-reference/groups/create
- /platform/api-reference/project-permissions 直接提供 /platform/api-reference/project-permissions/index，而不是重定向到 /platform/api-reference/project-permissions/index
- /platform/api-reference/projects 直接提供 /platform/api-reference/projects/index，而不是重定向到 /platform/api-reference/projects/create
- /platform/api-reference/shares 直接提供 /platform/api-reference/shares/index，而不是重定向到 /platform/api-reference/shares/add-asset
- /platform/api-reference/version-stacks 直接提供 /platform/api-reference/version-stacks/index，而不是重定向到 /platform/api-reference/version-stacks/copy
- /platform/api-reference/webhooks 直接提供 /platform/api-reference/webhooks/index，而不是重定向到 /platform/api-reference/webhooks/create
- /platform/api-reference/workspace-permissions 直接提供 /platform/api-reference/workspace-permissions/index，而不是重定向到 /platform/api-reference/workspace-permissions/index
- /platform/api-reference/workspaces 直接提供 /platform/api-reference/workspaces/index，而不是重定向到 /platform/api-reference/workspaces/create
- /platform/v2 直接提供 /platform/v2/index，而不是重定向到 /platform/v2/index
- /platform/v4-experimental/api-reference/accounts 直接提供 /platform/v4-experimental/api-reference/accounts/index，而不是重定向到 /platform/v4-experimental/api-reference/accounts/show
- /platform/v4-experimental/api-reference/collections 直接提供 /platform/v4-experimental/api-reference/collections/index，而不是重定向到 /platform/v4-experimental/api-reference/collections/index
- /platform/v4-experimental/api-reference/comments 直接提供 /platform/v4-experimental/api-reference/comments/index，而不是重定向到 /platform/v4-experimental/api-reference/comments/create
- /platform/v4-experimental/api-reference/folders 直接提供 /platform/v4-experimental/api-reference/folders/index，而不是重定向到 /platform/v4-experimental/api-reference/folders/bulk-copy
- /platform/v4-experimental/api-reference/groups 直接提供 /platform/v4-experimental/api-reference/groups/index，而不是重定向到 /platform/v4-experimental/api-reference/groups/add-adobe-group-to-account
- /platform/v4-experimental/api-reference/projects 直接提供 /platform/v4-experimental/api-reference/projects/index，而不是重定向到 /platform/v4-experimental/api-reference/projects/invited-projects-index
- /platform/v4-experimental/api-reference/session-watermark-templates 直接提供 /platform/v4-experimental/api-reference/session-watermark-templates/index，而不是重定向到 /platform/v4-experimental/api-reference/session-watermark-templates/create
- /platform/v4-experimental/api-reference/shares 直接提供 /platform/v4-experimental/api-reference/shares/index，而不是重定向到 /platform/v4-experimental/api-reference/shares/add-reviewers
- /platform/v4-experimental/api-reference/version-stacks 直接提供 /platform/v4-experimental/api-reference/version-stacks/index，而不是重定向到 /platform/v4-experimental/api-reference/version-stacks/create
- /platform/v4-experimental/api-reference/webhooks 直接提供 /platform/v4-experimental/api-reference/webhooks/index，而不是重定向到 /platform/v4-experimental/api-reference/webhooks/index
- /platform/v4-experimental/api-reference/workspaces 直接提供 /platform/v4-experimental/api-reference/workspaces/index，而不是重定向到 /platform/v4-experimental/api-reference/workspaces/index

## 失去 Fern 表格搜索功能的页面 (2) {#pages-that-lost-fern-table-search-2}

- platform/docs/resources/migration
- platform/v4-experimental/docs/resources/migration

## 失去固定表头的页面 (3) {#pages-that-lost-sticky-table-headers-3}

- platform/docs/guides/postman-collection
- platform/docs/resources/migration
- platform/v4-experimental/docs/resources/migration

## 已移除的 Hero 装饰 (3) {#hero-decoration-dropped-3}

- camera-to-cloud/welcome: unicorn-studio-bg
- platform/v4-experimental/welcome: hero-bg-image
- platform/welcome: hero-bg-image

## 已映射的图标 (2) {#icons-mapped-2}

- platform/docs/guides/zapier: trending-up 改为 arrow-trend-up
- platform/v4-experimental/docs/guides/zapier: trending-up 改为 arrow-trend-up

## 已提升的空表头行 (1) {#empty-table-header-rows-promoted-1}

- platform/docs/quick-start

## 固定为旧 ID 的标题锚点 (36) {#heading-anchors-pinned-to-the-old-id-36}

- camera-to-cloud/how-to-handle-errors#aws-errors-1
- camera-to-cloud/implementing-c2c-authentication-and-authorization#payload-parameters-1
- platform/docs/guides/media-links#example-request-1
- platform/docs/guides/media-links#example-request-2
- platform/docs/guides/media-links#example-request-3
- platform/docs/guides/media-links#example-request-4
- platform/docs/guides/media-links#example-request-5
- platform/docs/guides/media-links#example-response-1
- platform/docs/guides/media-links#example-response-2
- platform/docs/guides/media-links#example-response-3
- platform/docs/guides/media-links#example-response-4
- platform/docs/guides/media-links#example-response-5
- platform/docs/guides/media-links#fields-1
- platform/docs/guides/media-links#fields-2
- platform/docs/guides/media-links#fields-3
- platform/docs/guides/media-links#fields-4
- platform/docs/guides/media-links#fields-5
- platform/docs/guides/media-links#when-to-use-1
- platform/docs/guides/media-links#when-to-use-2
- platform/docs/guides/media-links#when-to-use-3
- platform/docs/guides/media-links#when-to-use-4
- platform/docs/guides/media-links#when-to-use-5
- platform/docs/guides/uploading-to-frame-io/how-local-remote-uploads-work#request-example-1
- platform/docs/guides/uploading-to-frame-io/how-local-remote-uploads-work#response-example-1
- platform/docs/guides/webhooks#step-3-create-a-webhook-resource-using-postman
- platform/v2/custom-actions-three-ways#cons-1
- platform/v2/custom-actions-three-ways#cons-2
- platform/v2/custom-actions-three-ways#pros-1
- platform/v2/custom-actions-three-ways#pros-2
- platform/v2/implementing-c2c-authentication-and-authorization-hardware#payload-parameters-1
- platform/v2/refreshing-oauth-2-tokens#with-pkce-1
- platform/v2/refreshing-oauth-2-tokens#without-pkce-1
- platform/v2/working-with-annotations#breakdown-1
- platform/v4-experimental/docs/guides/how-to-upload#request-example-1
- platform/v4-experimental/docs/guides/how-to-upload#response-example-1
- platform/v4-experimental/docs/guides/webhooks#step-3-create-a-webhook-resource-using-postman
