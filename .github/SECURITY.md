# Security Policy — CodePilot AI

## 1. Supported Versions

We provide security patches and vulnerability remediations for the following versions:

| Version | Supported | Security Maintenance Status |
| :--- | :--- | :--- |
| **1.0.x** | :white_check_mark: Yes | Current production release; full security patching. |
| **0.1.x** | :x: No | Initial pre-release; upgrade to 1.0.0. |

---

## 2. Reporting a Vulnerability

The CodePilot AI security team takes the security of our platform and our users' codebases seriously. If you identify a security vulnerability, we appreciate your cooperation in disclosing it responsibly.

### How to Report
* **Do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**
* Instead, submit reports privately via one of the following methods:
  * **GitHub Security Advisory**: Use the [Private Vulnerability Reporting](https://github.com/v-ani-2006/code-review-agent/security/advisories/new) feature in our GitHub repository.
  * **Email**: Send an encrypted or plain report to `security@codepilot.ai` or `v-ani-2006@github.com`.

### Information to Include in Your Report
To help us triage and resolve the issue quickly, please provide:
1. **Description**: A clear summary of the vulnerability, affected components, and potential impact.
2. **Steps to Reproduce**: Detailed reproduction steps, including sample code, API endpoints, or HTTP payloads.
3. **Proof of Concept (PoC)**: Minimal exploit script or curl command demonstrating the issue.
4. **Environment**: Version of CodePilot AI, OS, Docker configuration, and Python version.
5. **Mitigation Ideas**: Any proposed patches or mitigations if you have them.

---

## 3. Security Response Policy & Timelines

We commit to the following response timelines for acknowledged reports:

1. **Initial Response**: Within **48 hours** of report receipt, we will acknowledge receipt and assign a triage engineer.
2. **Triage & Validation**: Within **5 business days**, we will investigate and confirm or contest the vulnerability.
3. **Patch Development & Testing**: For confirmed Critical or High severity issues, we aim to deliver a patch within **14 business days**.
4. **Public Disclosure**: Once a patch is released to production and available in Docker / PyPI / Git, a coordinated public security advisory will be published, crediting the reporter (unless anonymity is requested).

---

## 4. Responsible Disclosure Guidelines

While researching vulnerabilities, please adhere to the following rules:
* Do not access, modify, or destroy user data belonging to others.
* Do not execute Denial of Service (DoS) attacks against production infrastructure.
* Give the maintainers reasonable time to remediate before making any public disclosure.

Thank you for helping keep CodePilot AI safe for everyone!
