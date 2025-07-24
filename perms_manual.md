Keeper Commander perms: A Definitive Implementation and Operations Manual


Part 1: Strategic Overview and System Architecture

This document provides the definitive design, implementation specification, and operational guide for the Keeper Commander perms command. It is intended to serve as the canonical blueprint for engineering teams tasked with its development and for the enterprise personnel who will leverage its capabilities for security and operational management.

1.1. The Vision: A Unified Permissions-and-Secrets as Code Platform


Problem Statement

The management of user and team permissions within a modern enterprise is a task of escalating complexity and critical security importance. As organizations scale in personnel, projects, and data sensitivity, the reliance on manual, ad-hoc adjustments to access control lists becomes unsustainable. This traditional, ticket-based approach is inherently error-prone, creating significant operational friction and, more critically, introducing a substantial attack surface. A single misconfiguration—an improperly assigned role or an overlooked folder permission—can lead directly to catastrophic data breaches or, conversely, to productivity-halting access denials that impede business velocity. The lack of a centralized, auditable source of truth for permissions makes it nearly impossible to answer the fundamental question: "Who has access to what, and why?"

The Solution

The perms command for Keeper Commander represents a paradigm shift in enterprise access governance. It introduces a declarative, auditable, and atomic mechanism for managing the complete permission landscape as code. This platform enables the holistic definition of teams, users, shared folder structures, granular permissions, Keeper Secrets Manager (KSM) applications, and administrative Role-Based Access Control (RBAC) assignments from a single, version-controlled "source of truth" configuration file.
Crucially, this configuration is not stored on an insecure local filesystem; it is maintained as a standard, encrypted record within the organization's own Keeper Vault. This "vault-native" architecture ensures that the sensitive blueprint of the enterprise's access control is protected by Keeper's industry-leading zero-knowledge security model. By treating permissions as code, the perms command enables modern, GitOps-style workflows, transforming access management from a reactive, manual chore into a proactive, automated, and highly secure discipline.

Strategic Value

The implementation of the perms command provides transformative strategic value by moving an organization's security posture from a reactive, ticket-based model to a proactive, automated, and GitOps-centric workflow. This fundamentally enhances security by minimizing human error and enforcing policy by design. It increases business velocity by allowing for the rapid and repeatable provisioning of entire work environments. Finally, it establishes an unparalleled level of auditability, creating an immutable, timestamped record of every permission change ever requested or applied across the enterprise.

1.2. Foundational Architectural Principles

The architecture of the perms command is built upon a set of foundational principles designed to enforce a mature, secure, and scalable operational model. These principles are not merely technical choices; they are deliberate design decisions that shape user behavior and promote security best practices.

Principle 1: Vault as the Immutable Source of Truth

The system is designed to fundamentally reject local file-based configurations. The primary and only acceptable input for the perms command is a pointer—either a Record UID (--config-uid) or a vault path (--config-path)—to a specific, encrypted record within the Keeper Vault. The client-side tool, Keeper Commander, operates statelessly; it fetches the configuration from the vault at the beginning of each execution, holds it in memory for the duration of the operation, and then discards it. No configuration is cached or stored on the local machine.
This design has profound behavioral consequences. By making the vault record the only possible source of truth, the architecture inherently discourages the dangerous practice of one-off, unversioned, and unaudited changes made from an administrator's laptop. The high-value workflows for System Administrators and DevOps Engineers all presuppose a Git repository as the human interface for modifying the configuration. An administrator checks out the configuration, makes a change, and submits a pull request. Following peer review and approval, a CI/CD pipeline is triggered, which is the only entity responsible for updating the canonical configuration record in the vault and executing the
keeper perms apply command. This architectural constraint does not just allow for GitOps; it actively guides the organization toward this best-practice model by making the insecure alternative of ad-hoc local configurations impossible.

Principle 2: The Declarative and Idempotent "Diff Engine"

At the heart of the perms command lies a "diff engine" that embodies two critical concepts: declarative syntax and idempotent execution. The configuration file is declarative, meaning the administrator defines the desired end state of the permissions landscape—the "what"—without having to script the specific sequence of steps—the "how"—to achieve it. The diff engine is responsible for comparing this desired state from the configuration with the current state of the enterprise, which it fetches directly from the Keeper backend. It then generates a precise execution plan to reconcile any and all differences.
The engine's execution is idempotent. This guarantees that applying the same configuration multiple times will produce the exact same result without causing errors or unintended side effects. If a command to create 10 teams is run and succeeds, running the exact same command again will result in the engine detecting that all 10 teams already exist and, therefore, taking no action. This property is what makes the apply command safe, predictable, and reliable for use in automated CI/CD pipelines, as it can be re-run to convergence without risk.

Principle 3: Schema Versioning for Future-Proofing

Every configuration JSON file must contain a schema_version field (e.g., "schema_version": "1.1"). This simple field is arguably one of the most critical features for the long-term viability and adoption of the perms platform, as it provides a robust mechanism for backward compatibility and non-disruptive evolution.
This tool is designed to manage an enterprise's entire permission state, which may be codified in thousands of lines of carefully curated configuration. A breaking change in the configuration format would be catastrophic, instantly invalidating this investment and potentially halting all automated permission workflows. As the Keeper platform evolves and new manageable entities are introduced, the configuration schema will inevitably need to be updated.
The schema_version field acts as a control switch for the parser within the perms command. The implementation can include logic that states, "If schema_version is '1.1', use parser A; if schema_version is '1.2', use parser B." This allows the tool to support new features and schema structures while continuing to correctly parse older, legacy configurations. It enables a smooth migration path for customers, allowing them to adopt new features at their own pace without forcing the entire user base to upgrade their configurations in lockstep. This protects the customer's investment in building their "Permissions-as-Code" repository and builds crucial trust in the platform's stability and longevity.

1.3. System Integration and Data Flow

The perms command is designed to integrate seamlessly into modern DevOps and SecOps workflows. The following sequence describes the end-to-end data flow for a typical CI/CD-driven change, illustrating how the architectural principles combine in a practical application.
Human Interaction (Git): A DevOps Engineer or System Administrator needs to provision a new project environment. They clone the Git repository that stores the human-readable version of the permissions configuration and create a new branch.
Configuration Change: The engineer adds a new block to the configuration file, defining the new project's team, its users, its required folder structure, its RBAC role assignments, and a dedicated KSM application.
Peer Review and Merge: The engineer submits a pull request. This change is reviewed by a peer or a security team member for correctness and policy compliance. Once approved, the branch is merged into the main branch.
CI/CD Pipeline Trigger: The merge event automatically triggers a CI/CD pipeline (e.g., in GitHub Actions, Jenkins, or GitLab CI).
Authentication and Execution: The pipeline runner authenticates to Keeper Commander using a secure, non-interactive method (e.g., a CI-specific configuration). It then executes the perms command, pointing to the canonical configuration record in the vault and injecting any necessary environment variables. For example: keeper perms apply --config-path "CI/ProductionPerms" --var 'env=titan'.
Vault-Native Operation: Keeper Commander fetches the specified configuration record from the Keeper Vault. The perms engine then performs the reconciliation lifecycle: it validates the schema, substitutes variables, fetches the current enterprise state, calculates the diff, and generates an execution plan.
State Reconciliation: The engine executes the plan, making a series of authenticated API calls to the Keeper backend to create the team, invite users, provision folders, assign roles, and create the KSM application.
Immutable Auditing: Upon completion (whether success or failure), the engine assembles a detailed log of the entire operation in JSON Lines (JSONL) format. It then creates a new, immutable log record in the dedicated Commander/PermissionsAutomation/Logs/ folder within the vault, providing a permanent, structured audit trail of the change.

Part 2: Definitive Component Design and Data Schemas

This section provides the definitive technical specifications for all user-facing interfaces and internal data structures. These schemas are the canonical reference for both developers implementing the feature and users authoring configurations.

2.1. Command-Line Interface (CLI) Specification

The user experience is centered around a clear and consistent command-line interface. The primary command is keeper perms, which is followed by a sub-command and a set of options that control its behavior.
The general structure is:
keeper perms <sub-command> [options]
The available sub-commands are:
apply: The primary execution command. It reconciles the current enterprise state with the desired state defined in the configuration record. It will create, update, and delete resources as necessary to match the configuration.
dry-run: A critical safety and validation tool. It performs the entire reconciliation process, including fetching the current state and calculating the diff, but instead of executing the changes, it prints a detailed report of the proposed execution plan. This allows administrators to review and verify all intended changes before applying them.
export: A utility command that performs the reverse operation. It inspects the current enterprise state (teams, users, folders, etc.) and generates a valid JSON configuration that represents it. This is invaluable for bootstrapping a new configuration from an existing enterprise setup.
create-config: A helper command that creates a new, empty boilerplate configuration record in the user's vault at a specified path. This provides a starting template for users to build upon, ensuring they begin with a correctly structured file.
The behavior of these sub-commands is modified by a set of command-line arguments, detailed in the table below.
Table 1: CLI Argument Reference
Sub-command
Argument
Required?
Description
Example
All
--config-uid <UID>
Yes (one of)
Specifies the configuration record by its unique identifier (UID). Mutually exclusive with --config-path.
... --config-uid "AbCd...EfG"
All
--config-path <PATH>
Yes (one of)
Specifies the configuration record by its path within the Keeper Vault. Mutually exclusive with --config-uid.
... --config-path "Configs/ProdPerms"
apply, dry-run
--var '<key>=<value>'
No
Overrides a variable defined in the configuration's variables block. Can be specified multiple times for different variables. Essential for CI/CD pipelines.
... --var 'env=prod' --var 'region=us-east-1'
apply
--force
No
Safety Guard Rail. Required to execute any destructive changes (e.g., deleting a team, removing a user from a team, deleting a shared folder). The command will fail if destructive changes are planned and this flag is absent.
keeper perms apply... --force
apply
--fail-fast
No (Default)
In the event of an error while executing the plan, the command will stop immediately and log the failure. This is the default behavior.
... --fail-fast
apply
--no-fail-fast
No
In the event of an error, the command will log the error for that specific action but attempt to continue executing the remaining actions in the plan.
... --no-fail-fast
apply, dry-run
--parent-folder-uid <UID>
No
Overrides the default location for creating new team shared folders. If not specified, they are created at the root level of the vault.
... --parent-folder-uid "XyZ...123"
All
--log-folder-uid <UID>
No
Overrides the default location for storing execution log records. The default is the Commander/PermissionsAutomation/Logs/ folder.
... --log-folder-uid "MyLogs/Perms"


2.2. Configuration Schema (Version 1.1)

The entire system is driven by the config_json field within the designated Keeper record. This JSON object must adhere to the schema specified below. The schema's design, particularly the inclusion of teams, users, roles, and secrets_manager_apps as top-level, first-class arrays, elevates the tool from a simple permission manager to a comprehensive "Workspace-as-Code" platform.
For a DevOps engineer, this holistic structure means a single keeper perms apply command can provision a complete, secure workspace for a new project. It can create the development team, assign them appropriate administrative privileges via an RBAC role, provision their shared folders for collaboration, and create the dedicated Keeper Secrets Manager application to securely store the project's credentials and API keys. This unified approach is a core feature of the platform.
Table 2: Configuration JSON Schema v1.1 Reference
Key Path
Type
Required
Description
schema_version
String
Yes
The version of the schema this configuration adheres to. Must be "1.1" for this specification. Ensures backward compatibility.
settings
Object
No
A container for global settings and safety guard rails that apply to the entire execution.
settings.protected_teams
Array of Strings
No
A list of Team UIDs or Names. The tool will refuse to modify or delete any team in this list, providing a critical safety layer for essential teams like "Domain Admins".
settings.protected_users
Array of Strings
No
A list of User Emails. The tool will refuse to modify these users or remove them from any teams, protecting key personnel accounts.
settings.protected_roles
Array of Strings
No
A list of Role UIDs or Names. The tool will refuse to assign or unassign any role in this list, preventing accidental privilege escalation or de-escalation.
settings.protected_folders
Array of Strings
No
A list of Shared Folder UIDs or vault paths. The tool will refuse to modify or delete any folder in this list.
variables
Object
No
A key-value map of default variables that can be used for substitution throughout the configuration. These can be overridden at runtime by the --var CLI argument.
folder_templates
Object
No
A dictionary where keys are template names and values are folder structure objects. Allows for the definition of reusable, complex folder hierarchies that can be applied to multiple teams.
teams
Array of Objects
No
The primary list of teams to be managed. Each object in the array defines a single team and its associated resources.
teams.name
String
Yes
The name of the team. Can use variable substitution, e.g., "{{env}}-backend-team".
teams.users
Array of Strings
No
A list of user emails that should be members of this team. The engine will invite new users and remove users not on this list.
teams.roles
Array of Strings
No
RBAC Integration. A list of Enterprise Role names or UIDs to be assigned to this team, baking the principle of least privilege directly into the configuration.
users
Array of Objects
No
A list for managing individual users outside the context of a specific team, primarily for assigning enterprise-wide roles.
users.email
String
Yes
The email address of the user to manage.
users.roles
Array of Strings
No
A list of Enterprise Role names or UIDs to be assigned directly to this individual user.
secrets_manager_apps
Array of Objects
No
KSM Integration. A list of Keeper Secrets Manager (KSM) applications to be created and shared.
secrets_manager_apps.name
String
Yes
The title of the KSM application record that will be created in the vault.
secrets_manager_apps.sharing
Array of Objects
No
A list of sharing permissions for the KSM application. Each object specifies a team or user to share with, along with their permissions.


2.3. Immutable Audit Log Structure

A cornerstone of the perms command is its robust and secure auditing capability. After every run (apply, dry-run, SUCCESS, or FAILURE), the system generates a detailed audit log and stores it as a new, immutable record in the Keeper Vault.
Logs are stored by default in a dedicated, non-configurable folder: Commander/PermissionsAutomation/Logs/. This ensures that audit trails are centrally located and cannot be accidentally misplaced. The title of each log record is standardized for easy identification and sorting: Perms Log - <STATUS> - YYYY-MM-DDTHH:MM:SSZ.
The choice of JSON Lines (JSONL) for the log_content field is a deliberate engineering decision to optimize the audit trail for machine consumption. The high-value workflow for Security and Compliance teams explicitly involves integrating this data with external Security Information and Event Management (SIEM) platforms. A traditional, single JSON blob for logging would be highly inefficient for this purpose, requiring a SIEM agent to download and parse the entire log file for every new entry. With JSONL, each line is a self-contained, valid JSON object. An ingestion agent can stream the
log_content field and process new lines as they are appended, making integration with systems like Splunk, Elasticsearch, or other log analyzers trivial and highly efficient. This technical choice directly enables the continuous compliance and automated monitoring workflow.
Table 3: Audit Log Record Fields
Field
Type
Description
title
String
The standardized title of the record, e.g., Perms Log - SUCCESS - 2025-07-24T12:00:00Z.
type
String
The Keeper record type, which will be perm-automation-config.
custom_fields.log_content
Multiline Text (JSONL)
A structured, line-by-line log of every action attempted or performed during the run. Each line is a distinct JSON object detailing a single step.
custom_fields.status
String
The final, overall status of the run. Possible values are SUCCESS, FAILURE, or DRY_RUN.
custom_fields.invoked_by
String
The email address of the user who executed the perms command, providing clear accountability.
custom_fields.config_uid
String
The UID of the configuration record that was used for this specific run, allowing auditors to trace any action back to its exact source configuration.
custom_fields.summary
String
A concise, human-readable summary of the changes made or proposed (e.g., "Created 2 teams, updated 5 users, deleted 1 shared folder.").


Part 3: The Execution Engine: A Deep Dive

This section transitions from the "what" of the system's components to the "how" of its internal operation. It provides a detailed look at the logic and processes that constitute the perms command's execution engine.

3.1. The Reconciliation Lifecycle

The core of the perms command is an ordered, multi-stage processing pipeline that ensures predictable, safe, and correct execution. Every run of apply or dry-run proceeds through the following lifecycle:
Configuration Loading & Validation: The process begins by fetching the specified configuration record from the Keeper Vault using its UID or path. The config_json field is extracted and parsed. The resulting object is immediately passed to the SchemaValidator, which rigorously checks it against the v1.1 schema. It enforces the presence of schema_version, validates data types, and ensures the structural integrity of the configuration. If validation fails, the process terminates immediately with a descriptive error.
Variable Substitution: The validated configuration object is then passed to the VariableSubstitutionEngine. This component scans the entire configuration for placeholders (e.g., {{env}}) and replaces them with corresponding values. It first uses the defaults defined in the variables block of the config, then overwrites them with any values provided via the --var command-line arguments. This allows for dynamic, environment-specific configurations without duplicating files.
Current State Fetching: Once the desired state is fully resolved, the PermissionProcessor invokes its _fetch_current_state method. This method is responsible for building a comprehensive, in-memory snapshot of the enterprise's current permission landscape. It makes a series of efficient calls to the keepercommander.api to retrieve all relevant objects: teams, team memberships, users, administrative roles, role assignments, shared folders, and KSM applications. For performance, this data is organized into lookup maps (e.g., Python dictionaries) keyed by UID, name, or email, allowing for near-instantaneous lookups during the diffing phase.
The "Diff" Calculation: This is the intellectual core of the engine. The _calculate_diff method systematically compares the desired state (from the processed configuration) against the current state (from the state fetcher). It iterates through each entity type (teams, users, roles, etc.) and identifies all discrepancies:
Creations: Entities present in the config but not in the current state.
Deletions: Entities present in the current state but absent from the config (and not protected).
Updates: Entities present in both but with differing attributes (e.g., a team's user list has changed).
Execution Plan Generation: The output of the diff calculation is the execution_plan: an ordered list of Action objects. Each object represents a single, atomic operation required to reconcile one discrepancy (e.g., a CreateTeamAction or a RemoveUserFromTeamAction). The plan is ordered logically to handle dependencies, for instance, ensuring a team is created before users are added to it. For a dry-run, this plan is simply formatted and printed. For an apply, it is passed to the executor.

3.2. Action Classes and the Executor

To manage the complexity of the various operations, the system uses the Command design pattern. Instead of a monolithic block of code with many if/else statements, each atomic operation is encapsulated in its own class.

The Command Pattern: Action Classes

A base Action class defines a common interface for all operations. This interface includes methods like:
execute(): Contains the specific keepercommander.api call(s) needed to perform the action.
describe(): Returns a human-readable string describing the action for logging purposes (e.g., "Create team 'Backend-Services'").
to_json(): Returns a structured JSON representation of the action for the JSONL audit log.
Subclasses are then created for each specific operation: CreateTeamAction, DeleteTeamAction, AddUserToTeamAction, RemoveUserFromTeamAction, AssignRoleAction, ProvisionKSMAppAction, etc. This approach makes the system highly extensible. To add a new manageable entity type in the future, a developer simply needs to create a new set of Action subclasses without modifying the core execution engine.

The Executor

The _execute_plan method within the PermissionProcessor acts as the executor. It is a simple but robust loop that iterates through the execution_plan list. For each Action object in the plan, it performs the following steps:
Logs the description of the action it is about to attempt.
Calls the execute() method on the Action object, wrapping it in a try/except block to catch any API errors.
If the execution is successful, it logs the success.
If an error occurs, it logs the failure. If the system is in the default --fail-fast mode, it immediately halts further execution and proceeds to the final logging step. If in --no-fail-fast mode, it records the error and continues to the next action in the plan.
This clean separation of concerns between the diff engine (which decides what to do) and the action executor (which does it) is key to the system's maintainability and robustness.

Part 4: Implementation Blueprint for Logical Incremental Development

This section provides a direct, actionable guide for an engineering team, breaking the project into manageable phases. This logical, incremental approach is designed to build the feature from the ground up, ensuring each component is tested and stable before the next is added.

4.1. Phase 1: Scaffolding and Configuration Loading

The initial phase focuses on establishing the basic structure of the command and ensuring it can communicate with the vault to load its configuration.
Tasks:
Command Stubbing: Create the file keepercommander/commands/perms.py. Inside, define a basic PermsCommand class.
CLI Registration: In keepercommander/cli.py, register the new PermsCommand so that the keeper perms command is recognized by the application. Stub out the sub-commands (apply, dry-run, export, create-config).
Argument Parsing: Implement the get_parser() method within PermsCommand to define and parse all the command-line arguments specified in Table 1, including --config-uid, --config-path, and --var.
Configuration Fetching: Implement the core logic within the command's execute method to handle the --config-uid and --config-path arguments. Use the keepercommander.api module to fetch the specified Keeper record from the vault.
JSON Parsing: Extract the config_json custom field from the fetched record and parse it into a Python dictionary. Implement robust error handling for cases where the record is not found or the content is not valid JSON.
Developer Focus: The goal of this phase is to have a command that can be invoked from the CLI and successfully loads a configuration object into memory. All subsequent logic can be stubbed out. Testing should focus on the CLI argument parsing and vault communication.

4.2. Phase 2: Building the Core Processor and State Fetching

This phase builds the foundational components of the permission processor that prepare the data for the main diff engine.
Tasks:
Processor Module: Create a new file, keepercommander/permission_processor.py, to house the core logic.
Schema Validator: Implement a SchemaValidator class or function. This component will take the parsed JSON from Phase 1 and validate it against the v1.1 schema definition from Table 2. It must check for the correct schema_version, required keys, and proper data types.
Variable Substitution Engine: Implement a VariableSubstitutionEngine. This component will process the validated configuration, replacing all {{...}} placeholders with values from the config's variables block and the CLI's --var arguments.
State Fetcher: Implement the _fetch_current_state method within the main PermissionProcessor class. This method will use the keepercommander.api to query the enterprise for all teams, users, roles, and other relevant data. The fetched data must be organized into efficient lookup maps (dictionaries) for fast access.
Developer Focus: At the end of this phase, the system should be able to produce two key artifacts: a fully resolved "desired state" object (from the validated and substituted config) and a comprehensive "current state" object (from the state fetcher). Unit tests should heavily mock the API calls to verify that the state fetcher correctly structures the data it receives.

4.3. Phase 3: The Diff Engine and Action Execution

This is the most complex phase, where the core reconciliation logic is implemented.
Tasks:
Diff Engine: Implement the _calculate_diff method in PermissionProcessor. This method will take the "desired state" and "current state" objects from Phase 2 and produce an execution_plan (a list of Action objects). Start with a single entity type, such as teams, to simplify the initial implementation.
Action Classes: Define the base Action class and its initial subclasses. Focus first on the actions needed for the first entity type (e.g., CreateTeamAction, DeleteTeamAction).
Executor: Implement the _execute_plan method. This method will loop through the execution_plan and call the execute() method on each Action object. Implement the basic --fail-fast logic.
Developer Focus: The key is to approach this iteratively. Get the full diff -> plan -> execute loop working perfectly for one simple case (e.g., creating a team) before adding more complexity. Once team creation works, add team deletion, then add user management within teams, and so on. The following table provides a guide for implementing the required action classes.
Table 4: Action Class Implementation Guide
Action Class
Purpose
Key Parameters
Underlying API Calls
Idempotency Check
CreateTeamAction
Creates a new team.
team_name, restrict_edit, restrict_share
api.team_add()
Check if a team with the same name already exists before executing.
DeleteTeamAction
Deletes an existing team.
team_uid
api.team_delete()
Check if the team UID still exists before executing.
AddUserToTeamAction
Adds a user to a team.
team_uid, user_email
api.team_add_user()
Check if the user is already a member of the team before executing.
RemoveUserFromTeamAction
Removes a user from a team.
team_uid, user_email
api.team_remove_user()
Check if the user is still a member of the team before executing.
AssignRoleAction
Assigns an admin role to a user/team.
role_id, target_uid (user or team)
api.execute_role_command() (or equivalent)
Check if the target already has the role assigned before executing.
ProvisionKSMAppAction
Creates and shares a KSM app.
app_name, sharing_list
api.record_add(), api.add_share()
Check if a record with the same title already exists in the target folder.


4.4. Phase 4: Auxiliary Commands and Logging

The final phase rounds out the feature set by implementing the helper commands and the critical vault-based logging.
Tasks:
export Command: Implement the logic for the export sub-command. This will essentially use the _fetch_current_state method from Phase 2 and then run a translation layer to convert the "current state" object into the valid JSON configuration format.
create-config Command: Implement the create-config sub-command. This will generate a string containing a minimal, valid boilerplate JSON configuration and use the api to create a new record in the vault with that content.
Vault-Based Logging: Implement the final, robust logging mechanism. After every run, this code must assemble the log_content in JSONL format, gather the summary metadata (status, user, config UID), and create the final log record in the Commander/PermissionsAutomation/Logs/ folder. This must execute reliably, even if the main execution plan failed midway.
Developer Focus: The export command is a good test of the accuracy of the state fetcher. The logging mechanism is a critical component for security and must be treated as a primary feature, not an afterthought.

Part 5: Enterprise-Grade Resilience and Safety Mechanisms

For a tool that wields the power to modify an entire enterprise's permission structure, resilience and safety are not optional features; they are core requirements. This section details the non-functional requirements that make the perms command suitable for production use in large, security-conscious organizations.

5.1. Error Handling: The "Fail-Fast, Idempotent Re-run" Model

The system's error handling strategy is designed for maximum safety and predictability in automated environments. It is defined as a "Fail-Fast, Log, and Idempotent Re-run" model.
Fail-Fast: By default (--fail-fast), when the executor encounters the first error during the execution of its plan, it immediately stops. It will not attempt to proceed with any subsequent actions. This prevents a single configuration error (e.g., a typo in a user's email) from causing a cascade of failures or leaving the system in an unknown, partially-configured state.
Log: Upon stopping, the system immediately proceeds to the logging stage. It generates a complete audit log record with a status of FAILURE. This log contains a detailed account of all the actions that succeeded before the failure, and a precise error message for the action that failed. This provides an administrator with a perfect snapshot of the system's state at the moment of failure.
Idempotent Re-run: After an administrator inspects the log and corrects the root cause of the error in the configuration file, they can simply re-run the exact same keeper perms apply command. This is where the idempotency of the diff engine becomes critical. On the second run, the _fetch_current_state method will report the new reality—for instance, that 5 out of the 10 planned teams were successfully created in the first run. The _calculate_diff engine will then compare the desired state (all 10 teams) with the new current state (5 teams exist) and will generate a new, smaller execution plan that only contains actions to create the remaining 5 teams. This process effectively allows the command to "resume" from the point of failure, making it safe and simple to re-run the command until it achieves the desired state and reports SUCCESS.

5.2. API Interaction: The Exponential Backoff and Retry Wrapper

In a large enterprise, a single apply command could generate hundreds or even thousands of individual API calls to the Keeper backend. Under such load, it is not a question of if API rate-limiting will be encountered, but when. To prevent these predictable events from causing brittle, failed pipeline runs, all calls to the keepercommander.api functions must be wrapped in a robust retry utility.
This wrapper will implement an exponential backoff and retry strategy. When an API call fails with a specific rate-limiting error code (e.g., HTTP 429 "Too Many Requests"), the wrapper will not immediately fail. Instead, it will:
Pause the execution for a short, randomized duration (e.g., 1-2 seconds).
Retry the exact same API call.
If the call fails again, it will double the potential pause duration (e.g., 2-4 seconds) and retry again.
This process will repeat, with the pause duration increasing exponentially, up to a configurable maximum number of retries (e.g., 5 attempts).
If the API call eventually succeeds, the execution continues seamlessly. Only if it fails after all retry attempts will the wrapper pass the error up to the main executor, triggering the fail-fast mechanism. This strategy is non-negotiable for ensuring the reliability of the perms command in large-scale enterprise environments.

5.3. Safety Guard Rails: Preventing Unintended Changes

The perms command includes two primary safety mechanisms designed to prevent catastrophic accidents resulting from human error in the configuration file.
The --force Flag: The tool distinguishes between additive/updating changes (creating a team, adding a user) and destructive changes (deleting a team, removing a user). The execution engine will refuse to perform any destructive action unless the operator explicitly includes the --force flag in the apply command. If the execution plan contains destructive actions and the flag is absent, the command will fail immediately with a clear error message listing the destructive changes it was asked to perform. This forces the human operator to consciously acknowledge and authorize the deletion of resources, preventing accidental removals caused by a copy-paste error or an incorrect merge in the configuration.
protected_* Lists: The settings block in the configuration file provides a second, more permanent layer of protection. Administrators can define lists of protected_teams, protected_users, protected_roles, and protected_folders by their name or UID. If the diff engine ever generates a plan that would modify or delete an entity present in one of these lists, it will automatically remove that action from the plan and issue a warning in the log. This acts as a permanent policy enforcement layer, making it impossible for the automation to touch the company's most critical resources (e.g., the "Domain Administrators" team, the CEO's user account, or the root "Company" shared folder), even if an administrator accidentally removes them from the main configuration.

Part 6: Quality Assurance and Validation Strategy

A comprehensive testing suite is non-negotiable to ensure the quality, reliability, and security of the perms command. The feature must ship with a full test matrix that validates every aspect of its functionality, from individual components to the end-to-end user workflow.

6.1. The Full Test Matrix

The quality assurance strategy is composed of three distinct layers of testing, each with a specific scope and purpose.
Table 5: Test Matrix and Focus Areas
Test Type
Scope
Key Focus Areas
Tools/Mocks
Unit Tests
Individual classes and functions in complete isolation.
Validation logic of the SchemaValidator. Correct string replacement in the VariableSubstitutionEngine. The internal logic of each individual Action class (e.g., ensuring CreateTeamAction uses the correct API parameters).
unittest.mock to simulate inputs and isolate the component from external dependencies.
Integration Tests
The PermissionProcessor class as a complete, integrated unit, from input to output.
The core logic of the _calculate_diff engine. Asserting that the correct execution_plan is generated for a wide variety of configuration and state deltas. Testing the interaction between the diff engine and the protected_* lists.
Mock the entire keepercommander.api module. The tests will provide mock return values for state-fetching calls and assert that the generated plan of Action objects is exactly as expected.
End-to-End (E2E) Tests
The full, compiled keeper perms... CLI command executed as a user would.
The entire reconciliation lifecycle against a live Keeper environment. Validating the --force flag behavior, idempotency, error handling, and the correctness of the final vault-based logging.
A dedicated, clean Keeper test vault that can be programmatically set up and torn down for each test run.


6.2. E2E Test Case Scenarios

The E2E tests are the ultimate validation of the system's correctness. The test suite must include scenarios that cover the primary user workflows and safety features.
Zero to Hero (Initial Provisioning):
Setup: Start with a completely empty test vault.
Action: Run keeper perms create-config to create a new config record. Programmatically update the record with a complex configuration defining multiple teams, users, roles, and a KSM app. Run keeper perms apply.
Assert: Query the vault state using other Keeper commands and assert that every single entity defined in the configuration was created correctly. Assert that the final log record shows SUCCESS and lists all the creation actions.
Idempotency Check:
Setup: Use the vault state from the successful "Zero to Hero" test.
Action: Run the exact same keeper perms apply command a second time.
Assert: Assert that the command's output reports "No changes to apply." Assert that a new log record is created with a SUCCESS status and a summary indicating zero changes.
Destructive Change and --force Guard Rail:
Setup: Modify the configuration from the previous test to remove one team.
Action 1: Run keeper perms apply without the --force flag.
Assert 1: Assert that the command fails with an error message explicitly stating that a destructive change was blocked. Assert that the vault state has not changed.
Action 2: Run keeper perms apply with the --force flag.
Assert 2: Assert that the command succeeds. Query the vault and assert that the specified team has been deleted.
Protected Resource Guard Rail:
Setup: In the configuration, add a specific team (e.g., "Admins") to the settings.protected_teams list. Then, remove the definition of the "Admins" team from the main teams array.
Action: Run keeper perms apply --force.
Assert: Assert that the command succeeds but the log contains a warning that the deletion of the protected team "Admins" was skipped. Query the vault and assert that the "Admins" team still exists.
Drift Detection (dry-run):
Setup: Use a known configuration and a corresponding vault state. Manually create a new team ("Drifted-Team") in the vault using a standard API call, creating a "drift" from the configuration's desired state.
Action: Run keeper perms dry-run against the original configuration.
Assert: Assert that the dry-run output proposes exactly one action: to delete the "Drifted-Team".

Part 7: End-User Guide and Practical Workflows

This guide provides practical instructions and examples for the primary user personas who will interact with the keeper perms command. It demonstrates how to leverage the tool to solve real-world access management challenges.

7.1. Getting Started: Creating Your First Configuration

The first step in using the perms command is to create the configuration record in your Keeper Vault. This record will serve as the single source of truth for your enterprise permissions.
Execute the create-config command: Run the following command, replacing the path with the desired location in your vault.
```bash
keeper perms create-config --config-path "Enterprise/Permissions/MasterConfig"
```

Review the Record: This command creates a new Keeper record at the specified path. The record will be of type perm-automation-config and its config_json custom field will contain a boilerplate JSON structure.
Populate the Configuration: Edit this record in your Keeper Vault to begin defining your enterprise structure. You can start by adding a single team or user to familiarize yourself with the schema.

7.2. Workflow for System Administrators: Onboarding and Offboarding

Goal: Automate the complete lifecycle of a department's access, from onboarding to offboarding, in a single, auditable transaction.
Scenario: Onboard a new 15-person marketing team, provision their shared folders, and assign them the "Marketing" administrative role.
Define the Team in Configuration: Edit your master configuration record (Enterprise/Permissions/MasterConfig) and add a new object to the teams array.
```json
{
  "schema_version": "1.1",
  "teams":,
      "roles":,
      "folder_template": "department_folders"
    }
  ],
  "folder_templates": {
    "department_folders": {
      "name": "Marketing Shared",
      "subfolders":
    }
  }
}
```

Perform a Dry Run (Safety Check): Before making any changes, validate your configuration with a dry-run.
```bash
keeper perms dry-run --config-path "Enterprise/Permissions/MasterConfig"
```

The output will provide a detailed report, confirming that the command intends to:
Create a new team named "Marketing Department".
Add/invite 15 users to the team.
Assign the "Marketing Role" to the team.
Create a new shared folder named "Marketing Shared" with three subfolders.
Apply the Configuration: Once satisfied with the plan, apply it.
```bash
keeper perms apply --config-path "Enterprise/Permissions/MasterConfig"
```

In a single, atomic operation, the entire team environment is provisioned.
Offboarding: When the team is disbanded, simply remove the "Marketing Department" object from the teams array in your configuration. Then, run apply with the --force flag to deprovision all associated resources.
```bash
keeper perms apply --config-path "Enterprise/Permissions/MasterConfig" --force
```


7.3. Workflow for DevOps Engineers: CI/CD Integration

Goal: Integrate permission and secrets management directly into infrastructure-as-code pipelines for fully automated environment provisioning.
Scenario: As part of a GitHub Actions workflow that deploys a new microservice for "Project Titan," automatically create the development team, their shared folder, and a dedicated KSM application for the service's secrets.
Create a Templated Configuration: Define a generic project configuration that uses variables. Store this in a record like DevOps/Templates/ProjectTemplate.
```json
{
  "schema_version": "1.1",
  "variables": {
    "project": "default-project"
  },
  "teams":,
      "folder_template": {
        "name": "Project {{project}} Source"
      }
    }
  ],
  "secrets_manager_apps":
    }
  ]
}
```

Integrate into CI/CD Pipeline: In your GitHub Actions workflow file (.github/workflows/deploy.yml), add a step that runs keeper perms apply and injects the project name using the --var argument.
```yaml
- name: Provision Keeper Environment
  run: |
    keeper perms apply \
      --config-path "DevOps/Templates/ProjectTemplate" \
      --var 'project=titan'
```

When this pipeline runs, it will dynamically create a team named "Project-titan-Devs", a folder named "Project titan Source", and a KSM application named "KSM App for titan", all shared correctly.

7.4. Workflow for Security & Compliance Teams: Drift Detection and Auditing

Goal: Continuously monitor the enterprise for unauthorized permission changes ("drift") and maintain a complete, immutable audit trail.
Scenario: Run an hourly check to ensure the live permission state matches the approved "golden" configuration and alert on any deviations.
Maintain a "Golden" Configuration: Curate a master configuration record (e.g., Security/GoldenState) that represents the officially sanctioned access control policy for the entire organization. This record should be tightly controlled.
Schedule a dry-run Job: Set up a scheduled job (e.g., a cron job or a scheduled pipeline) to execute a dry-run against the golden config every hour.
```bash
# Example cron job entry
0 * * * * /usr/local/bin/keeper perms dry-run --config-path "Security/GoldenState" > /var/log/keeper_drift_check.log
```

Alert on Drift: The output of the dry-run will be empty if there is no drift. If any manual, out-of-band changes have been made (e.g., a user was manually added to a sensitive team), the dry-run will output a plan to revert that change. A simple script can check if the log file is empty. If it's not, it can trigger an alert to the security team's SIEM or messaging platform, indicating that permission drift has been detected.
Audit Log Ingestion: Separately, configure an agent to periodically query the Commander/PermissionsAutomation/Logs/ folder in the vault. Because the logs are in structured JSONL format, the agent can easily stream new log entries and forward them to a SIEM for long-term storage, analysis, and reporting.

7.5. Workflow for Team Leads: Self-Service Management

Goal: Empower team leads to manage their own team's membership in a controlled, auditable way, reducing the administrative burden on central IT.
Scenario: The lead of the "Project Phoenix" team needs to add a new contractor for a short-term project.
Delegate Configuration Access: A System Administrator grants the "Project Phoenix" team lead Can Edit permissions on the specific Keeper record that defines their team's configuration (e.g., Teams/ProjectPhoenixConfig). The lead does not have access to any other permission configurations.
Team Lead Edits the User List: The team lead opens the ProjectPhoenixConfig record in their vault. They navigate to the config_json field and simply add the new contractor's email to the users array within their team's definition.
```json
{
  "schema_version": "1.1",
  "teams": [
    {
      "name": "Project Phoenix",
      "users": [
        "current.member@example.com",
        "new.contractor@example.com" // Added by team lead
      ]
    }
  ]
}
```

Automated Reconciliation: A central, automated job runs keeper perms apply against all team configuration records on a schedule (e.g., every 15 minutes). The next time this job runs, the perms engine will detect the change in the ProjectPhoenixConfig record. It will automatically add the new contractor to the "Project Phoenix" team, granting them all the associated folder and role permissions defined in the configuration. This entire process requires zero intervention from central IT, yet it is fully audited in the central log.

