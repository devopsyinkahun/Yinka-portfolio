# Yinka Odeneye — Portfolio

A responsive static portfolio served by Nginx in Docker. The GitHub Actions workflow validates the files, builds an image tagged with the exact commit SHA, transfers it to an Ubuntu EC2 instance over verified SSH, deploys it, and checks the public website.

## Project contents

- `index.html`, `styles.css`, `script.js` — portfolio website
- `assets/Olayinka_Odeneye_CV.pdf` — public-safe CV linked from the website
- `Dockerfile`, `nginx.conf` — container and web-server configuration
- `.github/workflows/deploy.yml` — CI/CD workflow
- `scripts/validate.py` — basic required-section and asset validation

## Before publishing

1. Review every personal detail, role, date, certification and skill in the site and CV.
2. Confirm the LinkedIn URL and public contact details.
3. Add a second genuine project/lab when its details are available. The current portfolio intentionally does not invent a second project.
4. Update this README with your actual EC2 public IP, repository URL and Actions run URL after deployment. Do not commit private keys or credentials.

## Run locally

Requirements: Docker installed and running.

```bash
python3 scripts/validate.py
docker build -t yinka-portfolio:local .
docker run -d --name yinka-portfolio -p 8080:80 --restart unless-stopped yinka-portfolio:local
curl --fail http://localhost:8080/
```

Open `http://localhost:8080`. The local port `8080` maps to container port `80`.

Stop and remove the local container:

```bash
docker rm -f yinka-portfolio
```

## EC2 preparation

Use an Ubuntu EC2 instance with Docker Engine installed. In its security group:
- Allow inbound TCP 80 from the intended public audience (`0.0.0.0/0` for a public portfolio).
- Allow SSH TCP 22 only from your current trusted IP address, not from the whole internet.
- Do not open the Docker daemon port (2375/2376) publicly.
- Keep the instance patched and use an IAM role only if the instance needs AWS API access.

Create a dedicated deployment user or use a restricted account with permission to run Docker. Membership in the Docker group effectively grants root-level control, so protect the SSH key and account accordingly.

Find and independently verify the EC2 SSH host-key fingerprint using a trusted administrative channel. Put the verified `known_hosts` line in the GitHub secret `EC2_KNOWN_HOSTS`. Do not blindly trust an unverified `ssh-keyscan` result.

## GitHub repository and secrets

Push this folder to a GitHub repository and use `main` as the default branch. Configure these repository Actions secrets:

| Secret | Value |
|---|---|
| `EC2_HOST` | EC2 public IPv4 address or DNS name |
| `EC2_USER` | SSH deployment username |
| `EC2_SSH_KEY` | Private SSH key for that deployment account (never commit it) |
| `EC2_KNOWN_HOSTS` | Previously verified host-key line(s) for the EC2 host |

The workflow writes the private key to a temporary runner file with restrictive permissions. SSH uses `StrictHostKeyChecking=yes`; host verification is not disabled. Secrets are referenced through the Actions secrets context and are not printed.

## CI/CD behaviour

On every push to `main` (and on manual workflow dispatch), the workflow:
1. Checks out the pushed commit.
2. Runs `scripts/validate.py` to verify the HTML structure and required sections/assets.
3. Builds a Docker image tagged with the full commit SHA.
4. Transfers that image to EC2 over SSH.
5. Replaces the running `portfolio` container with the exact commit image.
6. Checks the site locally on EC2 and then checks the public HTTP endpoint.

The container name is `portfolio`; EC2 host port `80` maps to container port `80`. The container uses `--restart unless-stopped` so Docker restarts it after a host reboot, provided Docker is enabled at boot.

## Prove automatic deployment

1. Complete the first successful workflow run.
2. Open the live website and note a visible sentence.
3. Edit that sentence in `index.html`.
4. Commit and push to `main`:

```bash
git add index.html
git commit -m "Update portfolio introduction"
git push origin main
```

5. Open the Actions tab and capture the successful second run. Record its URL and commit SHA.
6. Refresh the public site and capture the changed sentence. Do not manually restart or redeploy the container for this test.

## Rollback

The deployment script records the image used by the previous container before replacing it. If the new container fails its local health check, the script attempts to restore that previous image automatically. For a manual rollback, connect to EC2 and inspect available local image tags:

```bash
docker images yinka-portfolio
docker rm -f portfolio
docker run -d --name portfolio --restart unless-stopped -p 80:80 yinka-portfolio:PREVIOUS_COMMIT_SHA
curl --fail http://127.0.0.1/
```

Replace `PREVIOUS_COMMIT_SHA` with the actual previously deployed commit tag. Keep the previous image until the new release has been verified.

## Troubleshooting

- **Website unreachable:** check EC2 status, public IP, DNS, security-group TCP 80 rule, and `docker ps`.
- **SSH failure:** verify `EC2_HOST`, `EC2_USER`, key permissions, inbound SSH restriction and the independently verified `EC2_KNOWN_HOSTS` value.
- **Docker permission error:** confirm the deployment user has the required Docker permission; avoid exposing the Docker daemon over TCP.
- **Port already allocated:** check `sudo ss -lntp | grep ':80'` and remove or reconfigure the conflicting service.
- **Workflow health check fails:** inspect the Actions log and on EC2 run `docker logs portfolio` and `docker ps -a`.

## Submission details to complete after deployment

- Live URL: `http://YOUR_EC2_PUBLIC_IP/`
- EC2 public IP:
- Website port: `80`
- Container name: `portfolio`
- GitHub repository URL:
- Successful automatic-update Actions run URL:
- Commit SHA for the visible update:
- CV URL: `http://YOUR_EC2_PUBLIC_IP/assets/Olayinka_Odeneye_CV.pdf`

Do not submit private keys, passwords, AWS credentials, `.pem` files or secret values.
