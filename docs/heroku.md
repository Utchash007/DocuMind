# Deploy NoteMind to Heroku from your browser

Heroku builds the Linux container directly from GitHub. This workflow works from Windows using your browser and existing Git publishing tool; it requires no local Heroku CLI or Docker installation.

The deployment uses **Jina AI**, with **`jina-embeddings-v5-omni-small`** and 1024-dimensional vectors, matching the configured index. `JINA_API_KEY` is required in the deployment form.

## 1. Publish the deployment files

Publish the changes to the `main` branch of [Utchash007/DocuMind](https://github.com/Utchash007/DocuMind) using GitHub Desktop, VS Code Source Control, or GitHub's web editor. Confirm these files are present on GitHub:

- [`heroku.yml`](../heroku.yml) and [`app.json`](../app.json)
- The updated root [`Dockerfile`](../Dockerfile), [`.gitignore`](../.gitignore), and [`.gitattributes`](../.gitattributes)
- [`Backend/deploy/start-all-in-one.sh`](../Backend/deploy/start-all-in-one.sh)
- [`Backend/deploy/supervisord.conf`](../Backend/deploy/supervisord.conf)

The Git ignore exceptions publish the manifests, and Git attributes keep the shell scripts' Unix line endings in Windows checkouts. The Dockerfile copies the startup files directly and normalizes line endings during the build.

## 2. Create the app

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/Utchash007/DocuMind/tree/main)

1. Open the button, sign in to Heroku, and select an app name and region.
2. Enter the required configuration values below.
3. Click **Deploy app**. Heroku builds the image, runs the database release command, and starts the web dyno.

The button creates a **new Cedar-generation app on the `container` stack** through `app.json`. For a fork or another branch, change the `template` URL to that repository/branch. Private repositories also work when your linked GitHub account has access.

The manifest selects **one paid Standard-2X dyno (1 GB RAM)** for Next.js, FastAPI, and the PDF worker together. Review its price on the deployment form and adjust sizing in **Resources** based on actual memory usage. Database and provider charges are separate.

### Configuration form

| Required field | Value |
| --- | --- |
| `DATABASE_URL` | Deployment PostgreSQL connection string, with the provider's TLS settings. The release phase applies the DocuMind schema to this database. |
| `APPWRITE_ENDPOINT` | Your Appwrite endpoint including `/v1`. |
| `APPWRITE_PROJECT_ID` | The project used for authentication and PDF storage. |
| `APPWRITE_API_KEY` | Server key with the required email-code authentication and private-storage permissions. |
| `APPWRITE_STORAGE_BUCKET_ID` | Private PDF bucket ID. |
| `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` | Your existing Chroma Cloud index connection. |
| `GROQ_API_KEY` | Answer-generation API key. |
| `JINA_API_KEY` | Your Jina AI API key. |

Enter credentials into Heroku's form; the checked-in manifests contain only field descriptions and non-secret defaults. `NEW_RELIC_LICENSE_KEY` is optional.

These settings are supplied automatically:

```dotenv
DOCUMIND_EMBEDDING_PROVIDER=jina
JINA_EMBEDDING_MODEL=jina-embeddings-v5-omni-small
DOCUMIND_ALLOW_MOCK_EMBEDDINGS=false
BACKEND_URL=http://127.0.0.1:8000
HOSTNAME=0.0.0.0
RUN_MIGRATIONS=false
```

The Heroku web command explicitly selects Jina and supplies this model when `JINA_EMBEDDING_MODEL` is empty. Both the API and worker inherit the same settings. When overriding the model, use the model that produced the existing index.

Heroku supplies `PORT`. Browser API requests use the image's default `/api/backend`; Appwrite configuration and API keys are runtime server settings.

## 3. Complete sign-in configuration

1. Use **Open app** to find the exact assigned hostname.
2. Add that hostname as a **Web platform** in your Appwrite project and enable **Email OTP**.
3. Configure the PDF bucket with file security, no public reads, `pdf` as the allowed extension, and a 25 MiB maximum file size.
4. Sign in at `/sign-in`, complete onboarding, create a project, upload a PDF, wait for **Ready**, and ask a question.

## 4. Deploy subsequent changes

In the app's **Deploy** tab, choose **GitHub**, connect the repository, and select `main`. Use **Deploy Branch** for a manual deployment or **Enable Automatic Deploys** for future pushes. View build/release output under **Activity** and application logs under **More → View logs**.

`app.json` is consumed during button-based app creation. It does not reconfigure an existing app on subsequent GitHub deployments. An existing app must already use the `container` stack and have the required config vars; the button creates a correctly configured new app entirely through the browser.

## How startup works

```text
GitHub → Heroku Docker build → Alembic release phase → web dyno
                                                     ├── Next.js: 0.0.0.0:$PORT
                                                     ├── FastAPI: 127.0.0.1:8000
                                                     └── PDF worker
```

- `heroku.yml` builds the root Dockerfile with repository-root context.
- Its release phase runs `alembic upgrade head` from `/app/backend`; a failed migration prevents the new release from becoming active.
- Web startup sets `RUN_MIGRATIONS=false`, so dyno restarts launch processes directly.
- Supervisor restarts individual processes and forwards their logs to Heroku. The image includes `curl` for release-phase log streaming.
- PDFs, database rows, and vectors remain in Appwrite, PostgreSQL, and Chroma. The dyno's filesystem is temporary; editable notes remain browser-local.

Heroku's **30-second initial-response timeout** still applies to synchronous chat generation and upload preflight/storage. PDF indexing runs in the background. Long-running chat needs a background-generation/polling API change; increasing the Next.js proxy timeout does not change Heroku's limit.

## References

- [Building Docker images with heroku.yml](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml)
- [Deploy to Heroku button](https://devcenter.heroku.com/articles/heroku-button)
- [app.json schema](https://devcenter.heroku.com/articles/app-json-schema)
- [GitHub integration](https://devcenter.heroku.com/articles/github-integration)
- [Request timeout](https://devcenter.heroku.com/articles/request-timeout)
