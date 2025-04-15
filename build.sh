#!/bin/bash
set -e

# Determine current versions
VERSION=$(grep '^test=' VERSION | cut -d'=' -f2 | xargs)
PROD_VERSION=$(grep '^prod=' VERSION | cut -d'=' -f2 | xargs)

# Default options
BUMP_TYPE="patch"
TARGET_ENV=""

# Parse arguments
for arg in "$@"; do
  case $arg in
    --test) TARGET_ENV="test" ;;
    --prod) TARGET_ENV="prod" ;;
    --major|--minor|--patch) BUMP_TYPE="${arg#--}" ;;
    *) echo "❌ Unknown argument: $arg" && exit 1 ;;
  esac
done

if [[ -z "$TARGET_ENV" ]]; then
  echo "❌ You must specify either --test or --prod"
  exit 1
fi

# Get current version
if [[ "$TARGET_ENV" == "test" ]]; then
  CURRENT_VERSION="$VERSION"
elif [[ "$TARGET_ENV" == "prod" ]]; then
  CURRENT_VERSION="$PROD_VERSION"
fi

# Version bump logic
bump_version() {
  local version=$1
  local bump=$2
  local major=$(echo "$version" | cut -d. -f1)
  local minor=$(echo "$version" | cut -d. -f2)
  local patch=$(echo "$version" | cut -d. -f3)

  case "$bump" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
  esac

  echo "$major.$minor.$patch"
}

NEW_VERSION=$(bump_version "$CURRENT_VERSION" "$BUMP_TYPE")

# Update version in __init__.py
update_init_py() {
  echo "__version__ = \"$CURRENT_VERSION\"" > ./src/dbt_sqlx/__init__.py
}

# Set Git branch and tag
if [[ "$TARGET_ENV" == "test" ]]; then
  RELEASE_BRANCH="${CURRENT_VERSION}-pre-live"
  GIT_TAG="v${CURRENT_VERSION}-test"
  TEST_TOKEN=$(grep '^test-pypi=' PYPI_TOKEN | cut -d'=' -f2 | xargs)

  echo "🔧 Switching to test release branch: $RELEASE_BRANCH"
  git checkout -B "$RELEASE_BRANCH"

  echo "🔧 Publishing to TestPyPI → $CURRENT_VERSION"
  poetry version "$CURRENT_VERSION"
  update_init_py
  poetry build
  poetry publish -r dbt-sqlx-test -u __token__ -p "$TEST_TOKEN"
  sed -i "s/^test=$CURRENT_VERSION/test=$NEW_VERSION/" VERSION
  echo "✅ Bumped test version to $NEW_VERSION"

elif [[ "$TARGET_ENV" == "prod" ]]; then
  RELEASE_BRANCH="main"
  GIT_TAG="v${CURRENT_VERSION}"
  PROD_TOKEN=$(grep '^prod-pypi=' PYPI_TOKEN | cut -d'=' -f2 | xargs)

  echo "🚀 Publishing to PyPI → $CURRENT_VERSION"
  git checkout "$RELEASE_BRANCH"
  poetry version "$CURRENT_VERSION"
  update_init_py
  poetry build
  poetry publish -u __token__ -p "$PROD_TOKEN"
  sed -i "s/^prod=$CURRENT_VERSION/prod=$NEW_VERSION/" VERSION
  echo "✅ Bumped prod version to $NEW_VERSION"
fi

# 🏷️ Git commit + tag + push
git add VERSION pyproject.toml ./src/dbt_sqlx/__init__.py
git commit -m "🔖 Release $GIT_TAG"
git tag "$GIT_TAG"
git push origin "$RELEASE_BRANCH" --tags

echo "✅ Git tag $GIT_TAG pushed to $RELEASE_BRANCH branch."
echo "✅ Version bump complete. New version: $NEW_VERSION"