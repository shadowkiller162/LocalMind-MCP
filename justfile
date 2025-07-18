export COMPOSE_FILE := "docker-compose.local.yml"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments.
## For more information, see https://github.com/casey/just/issues/2473 .


# Default command to list all available commands.
default:
    @just --list

# build: Build python image.
build:
    @echo "Building python image..."
    @docker compose build

# up: Start up containers.
up:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# logs: View container logs
logs *args:
    @docker compose logs -f {{args}}

# manage: Executes `manage.py` command.
manage +args:
    @docker compose run --rm django python ./manage.py {{args}}

# reload-env: Reload environment variables by restarting containers.
reload-env:
    @echo "🔄 Reloading environment variables..."
    @docker compose down
    @docker compose up -d --remove-orphans
    @echo "✅ Environment variables reloaded"
    @echo "💡 Use 'just test-ai' to test AI services"

# test-ai: Test AI services configuration.
test-ai:
    @echo "🧪 Testing AI services..."
    @docker compose exec django python /app/scripts/setup_ai_keys.py
