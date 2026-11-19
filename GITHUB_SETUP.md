# Publish this GitHub-ready project

The files in this folder are ready to upload. This package does **not** automatically create a repository in your GitHub account.

1. Sign in to GitHub and open https://github.com/new
2. Name the repository `xwiz-project-portfolio`, choose **Public** (or Private until you've reviewed it), and leave **Add a README** unchecked.
3. On your own computer, extract this ZIP. Open Terminal in the extracted `xwiz-project-portfolio` directory.
4. Run:

   ```bash
   git init -b main
   git add .
   git commit -m "Initial XWiz project portfolio"
   git remote add origin https://github.com/checkopuffs/xwiz-project-portfolio.git
   git push -u origin main
   ```

   You may be prompted to authenticate using GitHub Credential Manager, an SSH key, or a PAT—**never paste that token into any chat**. GitHub Desktop is an alternative: `File > Add local repository` (create the repository if prompted), then `Publish repository`.

5. To make a GitHub *profile* landing page, create a second public repository named **`checkopuffs`** and copy `PROFILE_README.md` into that repository as `README.md`.

## Before making it public

- Replace conceptual renders with photographs you actually took of your builds, if desired.
- Review every file; do not post screenshots of IP addresses, credentials, private chats, or school/family details.
- Decide on a code/CAD license before giving others reuse rights. No license is included by default.
- Update project pages after physically testing the designs and after validating firmware against exact board revisions.
